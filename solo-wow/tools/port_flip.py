#!/usr/bin/env python3
"""Zelda of Warcraft: the double jump's front flip for the 1.12 human male, taken from the night elf
male's flipping JumpStart (the second of its two JumpStart clips) and retargeted onto the human
skeleton.

    port_flip.py <HumanMale.m2 (1.12, with port_roll's clips)> <NightElfMale.m2 (1.12)> <out .m2>

The two 1.12 character skeletons share their layout: the same key bones (root 26, spine 4/5,
shoulders 2/3, head 6, arms 0/1...) and the same chains below them. Each human bone is matched to a
night elf bone (the same key bone, else the parent's match's child at the same place, scaled to the
height). Every frame the night elf's world rotations are rebuilt and each matched human bone turned
the same way (its rest direction first aligned to the night elf's, as port_roll does); an unmatched
bone follows its parent. The pelvis moves as the night elf's root does, scaled to the human height.

The clip starts 100 ms in, past the night elf's crouch for a jump from the ground (the double jump
starts in the air), and is added as sequence 155 (Custom2) after the model's last one; Benilla plays
it through ZeldaSwingAnim step 7.
"""
import math
import struct
import sys

FLIP_ID = 155
NE_JUMPSTART, NE_VARIATION = 37, 1         # the night elf's second JumpStart is the flip
SKIP_MS = 100
STEP_MS = 33
ROOT_KEY = 26
SEQ_SIZE, BONE_SIZE = 0x44, 0x6c


def le(fmt, data, off):
    return struct.unpack_from(fmt, data, off)


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def qinv(a):
    return (-a[0], -a[1], -a[2], a[3])


def qnorm(a):
    n = math.sqrt(sum(c * c for c in a)) or 1.0
    return tuple(c / n for c in a)


def slerp(a, b, t):
    d = sum(x * y for x, y in zip(a, b))
    if d < 0:
        b, d = tuple(-c for c in b), -d
    if d > 0.9995:
        return qnorm(tuple(x + (y - x) * t for x, y in zip(a, b)))
    th = math.acos(d)
    s = math.sin(th)
    wa, wb = math.sin((1 - t) * th) / s, math.sin(t * th) / s
    return tuple(wa * x + wb * y for x, y in zip(a, b))


def between(u, v):
    """The shortest rotation taking direction u onto v."""
    nu = math.sqrt(sum(c * c for c in u)) or 1.0
    nv = math.sqrt(sum(c * c for c in v)) or 1.0
    u = [c / nu for c in u]
    v = [c / nv for c in v]
    d = sum(x * y for x, y in zip(u, v))
    if d > 0.99999:
        return (0.0, 0.0, 0.0, 1.0)
    c = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return qnorm((c[0], c[1], c[2], 1.0 + d))


class Skeleton:
    def __init__(self, data):
        self.d = d = data
        u = lambda o: le('<I', d, o)[0]
        self.seqs = [le('<HHII', d, u(0x20) + k * SEQ_SIZE) for k in range(u(0x1c))]
        self.bones = []
        for i in range(u(0x34)):
            b = u(0x38) + i * BONE_SIZE
            key, _, parent = le('<iIh', d, b)
            self.bones.append(dict(key=key, parent=parent, pivot=le('<3f', d, b + 0x60),
                                   rot=self._keys(b + 0x28, 16, '<4f'), tr=self._keys(b + 0x0c, 12, '<3f')))

    def _keys(self, o, size, fmt):
        d = self.d
        gseq = le('<h', d, o + 2)[0]
        n_t, o_t = le('<II', d, o + 0x0c)
        o_v = le('<I', d, o + 0x18)[0]
        if gseq != -1:
            return []
        return [(le('<I', d, o_t + 4 * k)[0], le(fmt, d, o_v + size * k)) for k in range(n_t)]

    def sample(self, keys, start, end, t, default, lerp):
        band = [(ts, v) for ts, v in keys if start <= ts <= end]
        if not band:
            return default
        if t <= band[0][0]:
            return band[0][1]
        for (t0, v0), (t1, v1) in zip(band, band[1:]):
            if t0 <= t <= t1:
                return lerp(v0, v1, (t - t0) / ((t1 - t0) or 1))
        return band[-1][1]

    def children(self, i):
        return [k for k, b in enumerate(self.bones) if b['parent'] == i]


def vlerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def match(hu, ne):
    """human bone -> night elf bone"""
    scale = hu.root_z / ne.root_z
    m = {}
    ne_by_key = {b['key']: i for i, b in enumerate(ne.bones) if b['key'] >= 0}
    for i, b in enumerate(hu.bones):
        if b['key'] >= 0 and b['key'] in ne_by_key and b['parent'] != -1:
            m[i] = ne_by_key[b['key']]
    changed = True
    while changed:
        changed = False
        for i, b in enumerate(hu.bones):
            p = b['parent']
            if i in m or p == -1 or p not in m:
                continue
            hp, np_ = hu.bones[p]['pivot'], ne.bones[m[p]]['pivot']
            rel = [b['pivot'][k] - hp[k] for k in range(3)]
            taken = set(m.values())
            best, bd = None, None
            for c in ne.children(m[p]):
                if c in taken:
                    continue
                cr = [(ne.bones[c]['pivot'][k] - np_[k]) * scale for k in range(3)]
                dist = math.sqrt(sum((x - y) ** 2 for x, y in zip(rel, cr)))
                if bd is None or dist < bd:
                    best, bd = c, dist
            if best is not None and bd < 0.08 + 0.25 * math.sqrt(sum(c * c for c in rel)):
                m[i] = best
                changed = True
    return m


def port(m2_path, ne_path, out_path):
    m2 = bytearray(open(m2_path, 'rb').read())
    hu, ne = Skeleton(bytes(m2)), Skeleton(open(ne_path, 'rb').read())
    hu_root = next(i for i, b in enumerate(hu.bones) if b['key'] == ROOT_KEY)
    ne_root = next(i for i, b in enumerate(ne.bones) if b['key'] == ROOT_KEY)
    hu.root_z, ne.root_z = hu.bones[hu_root]['pivot'][2], ne.bones[ne_root]['pivot'][2]
    scale = hu.root_z / ne.root_z
    m = match(hu, ne)
    # the flip: the night elf's JumpStart clips in file order, the second one
    clip = [s for s in ne.seqs if s[0] == NE_JUMPSTART][NE_VARIATION]
    c_start, c_end = clip[2] + SKIP_MS, clip[3]
    length = c_end - c_start

    # rest alignment: a matched bone with a matched child points its rest direction the night elf's way
    align = {}
    for i in m:
        kids = [c for c in hu.children(i) if c in m]
        if hu.bones[i]['key'] in (ROOT_KEY, 4, 5) or not kids:
            align[i] = (0.0, 0.0, 0.0, 1.0)
            continue
        c = max(kids, key=lambda c: sum((hu.bones[c]['pivot'][k] - hu.bones[i]['pivot'][k]) ** 2 for k in range(3)))
        dh = [hu.bones[c]['pivot'][k] - hu.bones[i]['pivot'][k] for k in range(3)]
        dn = [ne.bones[m[c]]['pivot'][k] - ne.bones[m[i]]['pivot'][k] for k in range(3)]
        align[i] = between(dh, dn)

    u32 = lambda o: le('<I', m2, o)[0]
    n_seq, o_seq = u32(0x1c), u32(0x20)
    n_bone, o_bone = u32(0x34), u32(0x38)
    seqs = [le('<HHII', m2, o_seq + k * SEQ_SIZE) for k in range(n_seq)]
    assert not any(s[0] == FLIP_ID for s in seqs), 'the model already has the flip'
    start = (max(s[3] for s in seqs) // 1000 + 2) * 1000
    template = next(k for k, s in enumerate(seqs) if s[0] == 38)        # Jump

    times = list(range(0, length, STEP_MS)) + [length]
    rot_keys = {i: [] for i in range(n_bone)}
    root_keys = []
    for t in times:
        tt = c_start + t
        ne_world = {}
        for j, b in enumerate(ne.bones):
            q = ne.sample(b['rot'], clip[2], clip[3], tt, (0.0, 0.0, 0.0, 1.0), slerp)
            p = b['parent']
            ne_world[j] = qnorm(qmul(ne_world[p], q)) if p != -1 and p in ne_world else qnorm(q)
        hu_world = {}
        for i in range(n_bone):
            p = hu.bones[i]['parent']
            pw = hu_world[p] if p != -1 else (0.0, 0.0, 0.0, 1.0)
            hu_world[i] = qnorm(qmul(ne_world[m[i]], align[i])) if i in m else pw
            rot_keys[i].append((start + t, qnorm(qmul(qinv(pw), hu_world[i]))))
        tr = ne.sample(ne.bones[ne_root]['tr'], clip[2], clip[3], tt, (0.0, 0.0, 0.0), vlerp)
        root_keys.append((start + t, tuple(c * scale for c in tr)))

    def append(blob):
        while len(m2) % 16:
            m2.append(0)
        off = len(m2)
        m2.extend(blob)
        return off

    seq_blob = bytearray(m2[o_seq:o_seq + n_seq * SEQ_SIZE])
    rec = bytearray(m2[o_seq + template * SEQ_SIZE:o_seq + (template + 1) * SEQ_SIZE])
    struct.pack_into('<HHII', rec, 0, FLIP_ID, 0, start, start + length)
    struct.pack_into('<f', rec, 0x0c, 0.0)
    struct.pack_into('<hH', rec, 0x40, -1, n_seq)
    seq_blob.extend(rec)
    struct.pack_into('<II', m2, 0x1c, n_seq + 1, append(seq_blob))
    slot = n_seq

    n_look, o_look = u32(0x24), u32(0x28)
    look = list(le('<%dh' % n_look, m2, o_look))
    while len(look) <= FLIP_ID:
        look.append(-1)
    look[FLIP_ID] = slot
    struct.pack_into('<II', m2, 0x24, len(look), append(struct.pack('<%dh' % len(look), *look)))
    n_play, o_play = u32(0x2c), u32(0x30)
    play = [le('<HH', m2, o_play + 4 * k) for k in range(n_play)]
    while len(play) <= FLIP_ID:
        play.append((len(play), 0))
    play[FLIP_ID] = (FLIP_ID, 0)
    struct.pack_into('<II', m2, 0x2c, len(play), append(b''.join(struct.pack('<HH', *p) for p in play)))

    def extend_track(track, new_keys, fmt):
        gseq = le('<h', m2, track + 2)[0]
        n_r, o_r = u32(track + 4), u32(track + 8)
        n_t, o_t = u32(track + 0x0c), u32(track + 0x10)
        o_v = u32(track + 0x18)
        if gseq != -1 or n_t == 0:
            return False
        size = struct.calcsize(fmt)
        ts = list(le('<%dI' % n_t, m2, o_t))
        out_v = bytearray(m2[o_v:o_v + n_t * size])
        ranges = [le('<II', m2, o_r + 8 * k) for k in range(n_r)]
        while len(ranges) < n_seq + 1:
            ranges.append((0, 0))
        lo = len(ts)
        for t, v in new_keys:
            ts.append(t)
            out_v.extend(struct.pack(fmt, *v))
        ranges[slot] = (lo, len(ts) - 1)
        struct.pack_into('<II', m2, track + 0x0c, len(ts), append(struct.pack('<%dI' % len(ts), *ts)))
        struct.pack_into('<II', m2, track + 0x14, len(ts), append(bytes(out_v)))
        struct.pack_into('<II', m2, track + 4, len(ranges), append(b''.join(struct.pack('<II', *r) for r in ranges)))
        return True

    holds_t = [(start, (0.0, 0.0, 0.0)), (start + length, (0.0, 0.0, 0.0))]
    holds_s = [(start, (1.0, 1.0, 1.0)), (start + length, (1.0, 1.0, 1.0))]
    missing = []
    for i in range(n_bone):
        b = o_bone + i * BONE_SIZE
        extend_track(b + 0x0c, root_keys if i == hu_root else holds_t, '<3f')
        if not extend_track(b + 0x28, rot_keys[i], '<4f') and i in m and ne.bones[m[i]]['rot']:
            missing.append(i)
        extend_track(b + 0x44, holds_s, '<3f')
    open(out_path, 'wb').write(m2)
    print('matched %d of %d bones; without a rotation track: %s' % (len(m), n_bone, missing))
    print('sequence %d: %d-%d (%d ms)' % (FLIP_ID, start, start + length, length))
    return m


if __name__ == '__main__':
    port(*sys.argv[1:4])
