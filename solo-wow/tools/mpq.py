"""Minimal MPQ (v1, World of Warcraft 1.12) reader and writer, for the Zelda of Warcraft patch.

Reads files by name (zlib, bzip2 and PKWARE-imploded sectors, encrypted or not) and writes a new
archive of uncompressed-or-zlib files with a (listfile). Standard library only.
"""
import bz2
import struct
import zlib

# ------------------------------------------------------------------ crypt table and hashing
_CRYPT = [0] * 0x500


def _init_crypt():
    seed = 0x00100001
    for i in range(0x100):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            t1 = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            t2 = seed & 0xFFFF
            _CRYPT[idx] = t1 | t2
            idx += 0x100


_init_crypt()


def hash_string(s, kind):
    s1, s2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in s.upper().replace('/', '\\'):
        c = ord(ch)
        s1 = _CRYPT[(kind << 8) + c] ^ ((s1 + s2) & 0xFFFFFFFF)
        s2 = (c + s1 + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return s1


def decrypt(data, key):
    out = bytearray(len(data))
    seed = 0xEEEEEEEE
    for i in range(0, len(data) - len(data) % 4, 4):
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        v = struct.unpack_from('<I', data, i)[0]
        r = v ^ ((key + seed) & 0xFFFFFFFF)
        key = ((((~key) << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        seed = (r + seed + (seed << 5) + 3) & 0xFFFFFFFF
        struct.pack_into('<I', out, i, r)
    out[len(data) - len(data) % 4:] = data[len(data) - len(data) % 4:]
    return bytes(out)


def encrypt(data, key):
    out = bytearray(len(data))
    seed = 0xEEEEEEEE
    for i in range(0, len(data) - len(data) % 4, 4):
        seed = (seed + _CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        v = struct.unpack_from('<I', data, i)[0]
        r = v ^ ((key + seed) & 0xFFFFFFFF)
        key = ((((~key) << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        seed = (v + seed + (seed << 5) + 3) & 0xFFFFFFFF
        struct.pack_into('<I', out, i, r)
    out[len(data) - len(data) % 4:] = data[len(data) - len(data) % 4:]
    return bytes(out)


# ------------------------------------------------------------------ PKWARE DCL explode
_LEN_BITS = [3, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7]
_LEN_CODE = [0x05, 0x03, 0x01, 0x06, 0x0A, 0x02, 0x0C, 0x14, 0x04, 0x18, 0x08, 0x30, 0x10, 0x20, 0x40, 0x00]
_LEN_BASE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 14, 22, 38, 70, 134, 262]
_EX_LEN_BITS = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
_DIST_BITS = [2, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
              7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
_DIST_CODE = [0x03, 0x0D, 0x05, 0x19, 0x09, 0x11, 0x01, 0x3E, 0x1E, 0x2E, 0x0E, 0x36, 0x16, 0x26, 0x06, 0x3A,
              0x1A, 0x2A, 0x0A, 0x32, 0x12, 0x22, 0x42, 0x02, 0x7C, 0x3C, 0x5C, 0x1C, 0x6C, 0x2C, 0x4C, 0x0C,
              0x74, 0x34, 0x54, 0x14, 0x64, 0x24, 0x44, 0x04, 0x78, 0x38, 0x58, 0x18, 0x68, 0x28, 0x48, 0x08,
              0xF0, 0x70, 0xB0, 0x30, 0xD0, 0x50, 0x90, 0x10, 0xE0, 0x60, 0xA0, 0x20, 0xC0, 0x40, 0x80, 0x00]


def _decode_table(bits, codes):
    table = {}
    for i, (b, c) in enumerate(zip(bits, codes)):
        table[(b, c)] = i
    return table


_LEN_TABLE = _decode_table(_LEN_BITS, _LEN_CODE)
_DIST_TABLE = _decode_table(_DIST_BITS, _DIST_CODE)


class _Bits:
    def __init__(self, data):
        self.data, self.pos, self.buf, self.n = data, 0, 0, 0

    def get(self, count):
        while self.n < count:
            b = self.data[self.pos] if self.pos < len(self.data) else 0
            self.pos += 1
            self.buf |= b << self.n
            self.n += 8
        v = self.buf & ((1 << count) - 1)
        self.buf >>= count
        self.n -= count
        return v


def _read_code(bits, table, maxbits):
    code, length = 0, 0
    while length < maxbits:
        code |= bits.get(1) << length
        length += 1
        if (length, code) in table:
            return table[(length, code)]
    raise ValueError('bad PKWARE code')


def explode(data):
    ctype, dict_bits = data[0], data[1]
    if ctype != 0:
        raise ValueError('PKWARE ASCII mode not supported')
    bits = _Bits(data[2:])
    out = bytearray()
    while True:
        if bits.get(1):
            li = _read_code(bits, _LEN_TABLE, 7)
            length = _LEN_BASE[li] + (bits.get(_EX_LEN_BITS[li]) if _EX_LEN_BITS[li] else 0) + 2
            if length == 519:
                break
            di = _read_code(bits, _DIST_TABLE, 8)
            if length == 2:
                dist = (di << 2) | bits.get(2)
            else:
                dist = (di << dict_bits) | bits.get(dict_bits)
            start = len(out) - dist - 1
            for k in range(length):
                out.append(out[start + k])
        else:
            out.append(bits.get(8))
    return bytes(out)


# ------------------------------------------------------------------ reader
class Archive:
    def __init__(self, path):
        self.f = open(path, 'rb')
        head = self.f.read(32)
        off = 0
        while head[:4] != b'MPQ\x1a':
            off += 512
            self.f.seek(off)
            head = self.f.read(32)
            if not head:
                raise ValueError('not an MPQ: ' + path)
        self.base = off
        (_, hsize, asize, ver, shift, hpos, bpos, hcount, bcount) = struct.unpack('<4sIIHHIIII', head)
        self.sector = 512 << shift
        self.f.seek(off + hpos)
        ht = decrypt(self.f.read(hcount * 16), hash_string('(hash table)', 3))
        self.hashes = [struct.unpack_from('<IIHHI', ht, i * 16) for i in range(hcount)]
        self.f.seek(off + bpos)
        bt = decrypt(self.f.read(bcount * 16), hash_string('(block table)', 3))
        self.blocks = [struct.unpack_from('<IIII', bt, i * 16) for i in range(bcount)]

    def _find(self, name):
        n = len(self.hashes)
        start = hash_string(name, 0) % n
        a, b = hash_string(name, 1), hash_string(name, 2)
        for k in range(n):
            ha, hb, loc, plat, bi = self.hashes[(start + k) % n]
            if bi == 0xFFFFFFFF:
                return None
            if ha == a and hb == b and bi != 0xFFFFFFFE:
                return bi
        return None

    def has(self, name):
        bi = self._find(name)
        return bi is not None and self.blocks[bi][3] & 0x80000000

    def read(self, name):
        bi = self._find(name)
        if bi is None:
            return None
        pos, csize, fsize, flags = self.blocks[bi]
        if not flags & 0x80000000:
            return None
        self.f.seek(self.base + pos)
        raw = self.f.read(csize)
        key = 0
        if flags & 0x10000:
            key = hash_string(name.replace('/', '\\').split('\\')[-1], 3)
            if flags & 0x20000:
                key = ((key + pos) ^ fsize) & 0xFFFFFFFF
        if flags & 0x01000000:   # single unit
            data = decrypt(raw, key) if key else raw
            return self._unpack(data, fsize, flags)
        if not flags & 0x300:    # stored
            if not key:
                return raw[:fsize]
            out = bytearray()
            for s in range(0, fsize, self.sector):
                out += decrypt(raw[s:s + self.sector], (key + s // self.sector) & 0xFFFFFFFF)
            return bytes(out[:fsize])
        nsec = (fsize + self.sector - 1) // self.sector
        table = raw[:(nsec + 1) * 4]
        if key:
            table = decrypt(table, (key - 1) & 0xFFFFFFFF)
        offs = struct.unpack('<%dI' % (nsec + 1), table)
        out = bytearray()
        for s in range(nsec):
            chunk = raw[offs[s]:offs[s + 1]]
            if key:
                chunk = decrypt(chunk, (key + s) & 0xFFFFFFFF)
            want = min(self.sector, fsize - s * self.sector)
            out += self._unpack(chunk, want, flags)
        return bytes(out)

    @staticmethod
    def _unpack(chunk, want, flags):
        if len(chunk) >= want:
            return chunk[:want]
        if flags & 0x100:
            return explode(chunk)
        mask, body = chunk[0], chunk[1:]
        if mask & 0x10:
            body = bz2.decompress(body)
        if mask & 0x08:
            body = explode(body)
        if mask & 0x02:
            body = zlib.decompress(body)
        if mask & ~(0x02 | 0x08 | 0x10):
            raise ValueError('unsupported MPQ compression %#x' % mask)
        return body


def read_chain(archives, name):
    """The file from the highest-priority archive that has it (archives in ascending priority)."""
    for a in reversed(archives):
        data = a.read(name)
        if data is not None:
            return data
    return None


# ------------------------------------------------------------------ writer
def write_archive(path, files, sector_shift=3):
    """files: {internal name: bytes}. Each file is zlib-compressed by sector (stored if that is
    not smaller); a (listfile) is added."""
    files = dict(files)
    files['(listfile)'] = ('\r\n'.join(sorted(n for n in files if n != '(listfile)')) + '\r\n').encode()
    names = list(files)
    hcount = 1
    while hcount < len(names) * 2:
        hcount *= 2
    hcount = max(hcount, 16)
    sector = 512 << sector_shift
    body = bytearray()
    blocks = []
    for name in names:
        data = files[name]
        pos = 32 + len(body)
        nsec = max(1, (len(data) + sector - 1) // sector)
        chunks = []
        for s in range(nsec):
            piece = data[s * sector:(s + 1) * sector]
            packed = b'\x02' + zlib.compress(piece, 9)
            chunks.append(packed if len(packed) < len(piece) else piece)
        offs = [(nsec + 1) * 4]
        for c in chunks:
            offs.append(offs[-1] + len(c))
        blob = struct.pack('<%dI' % (nsec + 1), *offs) + b''.join(chunks)
        body += blob
        blocks.append((pos, len(blob), len(data), 0x80000000 | 0x200))
    hashes = [(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFF, 0xFFFF, 0xFFFFFFFF)] * hcount
    hashes = list(hashes)
    for bi, name in enumerate(names):
        k = hash_string(name, 0) % hcount
        while hashes[k][4] != 0xFFFFFFFF:
            k = (k + 1) % hcount
        hashes[k] = (hash_string(name, 1), hash_string(name, 2), 0, 0, bi)
    hpos = 32 + len(body)
    ht = b''.join(struct.pack('<IIHHI', *h) for h in hashes)
    bt = b''.join(struct.pack('<IIII', *b) for b in blocks)
    bpos = hpos + len(ht)
    total = bpos + len(bt)
    header = struct.pack('<4sIIHHIIII', b'MPQ\x1a', 32, total, 0, sector_shift, hpos, bpos, hcount, len(blocks))
    with open(path, 'wb') as f:
        f.write(header)
        f.write(body)
        f.write(encrypt(ht, hash_string('(hash table)', 3)))
        f.write(encrypt(bt, hash_string('(block table)', 3)))
