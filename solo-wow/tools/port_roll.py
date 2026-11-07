#!/usr/bin/env python3
"""Zelda of Warcraft: the dodge roll and the backflip for the 1.12 human male, taken from a modern
(HD) human male's animations and retargeted onto the 1.12 skeleton.

    port_roll.py <HumanMale.m2 (1.12)> <HD human male .mdx> <out HumanMale.m2>

The HD model is a Warcraft III (.mdx) conversion whose sequences keep the modern animation ids in
their names ("Cinematic 666114" is id 666). Two of them turn the whole body over: 666 (a 0.33 s
forward roll) and 736 (a 1.13 s turn the other way, the backflip). Each 1.12 bone is matched to the
HD bone at the same place in the body (MAP below); every frame, a matched bone is turned so it
points where its HD bone points (its rest direction aligned to the HD one's), an unmatched bone
follows its parent, and the pelvis moves as the HD pelvis does, scaled to the 1.12 height.

The two clips are added to the model as new sequences, ids 153 (Custom0) and 154 (Custom1), after
the model's last one; Benilla plays them through ZeldaSwingAnim steps 5 and 6.
"""
import math
import struct
import sys

ROLL_ID, BACKFLIP_ID = 153, 154
# (new id, HD id, milliseconds kept from its start (None: all), the pelvis moves with it): the roll
# keeps its drop into a ball near the ground; the backflip keeps its turn up to the landing, without
# its own leap (the server's push already lifts the hero)
CLIPS = [(ROLL_ID, 666, None, True), (BACKFLIP_ID, 736, 600, False)]
STEP_MS = 33

# 1.12 bone -> HD object id (bone_bNN in the .mdx), with the 1.12 and HD child that give each its
# rest direction (None: no alignment, the torso and the ends of the chains)
MAP = {
    18: (177, None),          # pelvis (key bone Root)
    21: (0, None),            # hips
    20: (1, None),            # lower spine
    22: (11, None),           # chest
    48: (18, (64, 34)),       # neck
    64: (34, None),           # head
    49: (16, (65, 22)),       # left shoulder
    50: (17, (66, 23)),       # right shoulder
    65: (22, (78, 30)),       # left upper arm
    66: (23, (79, 31)),       # right upper arm
    78: (30, (95, 36)),       # left forearm
    79: (31, (97, 41)),       # right forearm
    95: (36, None),           # left hand
    97: (41, None),           # right hand
    25: (3, (53, 8)),         # left thigh
    26: (2, (54, 7)),         # right thigh
    53: (8, (68, 14)),        # left shin
    54: (7, (70, 13)),        # right shin
    68: (14, None),           # left foot
    70: (13, None),           # right foot
    80: (21, None),           # left toes
    81: (20, None),           # right toes
}
PELVIS, HD_PELVIS = 18, 177


# ------------------------------------------------------------------ quaternions (x, y, z, w)
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
    n = math.sqrt(sum(x * x for x in a)) or 1.0
    return tuple(x / n for x in a)


def qrot(q, v):
    p = qmul(qmul(q, (v[0], v[1], v[2], 0.0)), qinv(q))
    return p[:3]


def slerp(a, b, t):
    dot = sum(x * y for x, y in zip(a, b))
    if dot < 0:
        b, dot = tuple(-x for x in b), -dot
    if dot > 0.9995:
        return qnorm(tuple(x + (y - x) * t for x, y in zip(a, b)))
    th = math.acos(dot)
    s = math.sin(th)
    wa, wb = math.sin((1 - t) * th) / s, math.sin(t * th) / s
    return tuple(wa * x + wb * y for x, y in zip(a, b))


def between(u, v):
    """The shortest turn taking direction u onto direction v."""
    nu, nv = math.sqrt(sum(x * x for x in u)), math.sqrt(sum(x * x for x in v))
    u, v = [x / nu for x in u], [x / nv for x in v]
    c = sum(x * y for x, y in zip(u, v))
    axis = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    if c < -0.9999:
        return (1.0, 0.0, 0.0, 0.0)
    return qnorm((axis[0], axis[1], axis[2], 1.0 + c))


# ------------------------------------------------------------------ the HD model (.mdx)
class Mdx:
    def __init__(self, data):
        self.d = data
        chunks, i = {}, 4
        while i < len(data):
            tag = data[i:i + 4].decode()
            size = struct.unpack_from('<I', data, i + 4)[0]
            chunks[tag] = (i + 8, size)
            i += 8 + size
        o, sz = chunks['SEQS']
        self.seqs = {}
        for k in range(sz // 132):
            b = o + k * 132
            name = data[b:b + 80].split(b'\0')[0].decode(errors='replace')
            self.seqs[name] = struct.unpack_from('<II', data, b + 80)
        self.nodes = {}
        for tag, extra in (('BONE', 8), ('HELP', 0)):
            o, sz = chunks[tag]
            p = o
            while p < o + sz:
                nsize = struct.unpack_from('<I', data, p)[0]
                oid, parent = struct.unpack_from('<ii', data, p + 84)
                q, tracks = p + 96, {}
                while q < p + nsize:
                    t = data[q:q + 4].decode()
                    nc = {'KGTR': 3, 'KGRT': 4, 'KGSC': 3}[t]
                    n, interp, _ = struct.unpack_from('<IIi', data, q + 4)
                    q += 16
                    keys = []
                    for _ in range(n):
                        f = struct.unpack_from('<i', data, q)[0]
                        keys.append((f, struct.unpack_from('<%df' % nc, data, q + 4)))
                        q += 4 + 4 * nc + (8 * nc if interp > 1 else 0)
                    tracks[t] = keys
                self.nodes[oid] = (parent, tracks)
                p += nsize + extra
        o, sz = chunks['PIVT']
        self.pivots = [struct.unpack_from('<3f', data, o + 12 * k) for k in range(sz // 12)]

    def clip(self, anim_id):
        for name, (s, e) in self.seqs.items():
            if name.startswith('Cinematic ') and name[10:].startswith(str(anim_id)) and \
                    len(name[10:]) > len(str(anim_id)):
                return s, e
        raise KeyError(anim_id)

    def sample(self, oid, tag, t, default):
        keys = self.nodes[oid][1].get(tag)
        if not keys:
            return default
        if t <= keys[0][0]:
            return keys[0][1]
        for (fa, va), (fb, vb) in zip(keys, keys[1:]):
            if fa <= t <= fb:
                f = (t - fa) / (fb - fa) if fb > fa else 0.0
                if tag == 'KGRT':
                    return slerp(va, vb, f)
                return tuple(x + (y - x) * f for x, y in zip(va, vb))
        return keys[-1][1]

    def world(self, oid, t, cache):
        """(rotation, translation) of the node's transform at time t: x -> R x + T."""
        if oid in cache:
            return cache[oid]
        parent = self.nodes[oid][0]
        pr, pt = self.world(parent, t, cache) if parent != -1 else ((0, 0, 0, 1), (0, 0, 0))
        q = qnorm(self.sample(oid, 'KGRT', t, (0, 0, 0, 1)))
        tr = self.sample(oid, 'KGTR', t, (0, 0, 0))
        piv = self.pivots[oid]
        rq = qmul(pr, q)
        local_t = [piv[i] + tr[i] for i in range(3)]
        rp = qrot(q, piv)
        local_t = [local_t[i] - rp[i] for i in range(3)]
        wt = qrot(pr, local_t)
        cache[oid] = (rq, tuple(wt[i] + pt[i] for i in range(3)))
        return cache[oid]


# ------------------------------------------------------------------ the 1.12 model (M2 v256)
SEQ_SIZE, BONE_SIZE = 0x44, 0x6c


def le(fmt, data, off):
    return struct.unpack_from(fmt, data, off)


def port(m2_path, mdx_path, out_path):
    m2 = bytearray(open(m2_path, 'rb').read())
    hd = Mdx(open(mdx_path, 'rb').read())
    u32 = lambda o: le('<I', m2, o)[0]
    assert m2[:4] == b'MD20' and u32(4) == 256

    n_seq, o_seq = u32(0x1c), u32(0x20)
    n_bone, o_bone = u32(0x34), u32(0x38)
    bones = []
    for i in range(n_bone):
        b = o_bone + i * BONE_SIZE
        bones.append(dict(parent=le('<h', m2, b + 8)[0], pivot=le('<3f', m2, b + 0x60)))
    seqs = [le('<HHII', m2, o_seq + k * SEQ_SIZE) for k in range(n_seq)]
    last_end = max(s[3] for s in seqs)
    template = next(k for k, s in enumerate(seqs) if s[0] == 38)      # Jump

    # the rest directions' alignment, 1.12 onto HD
    align = {}
    for b, (h, kids) in MAP.items():
        if kids is None:
            align[b] = (0.0, 0.0, 0.0, 1.0)
            continue
        c, hc = kids
        dc = [bones[c]['pivot'][i] - bones[b]['pivot'][i] for i in range(3)]
        dh = [hd.pivots[hc][i] - hd.pivots[h][i] for i in range(3)]
        align[b] = between(dc, dh)
    scale = bones[PELVIS]['pivot'][2] / hd.pivots[HD_PELVIS][2]

    # the new sequences' frames: per bone, (time, local rotation); the pelvis's translation
    new_seqs, rot_keys, pelvis_keys = [], {i: [] for i in range(n_bone)}, []
    start = (last_end // 1000 + 2) * 1000
    for anim_id, hd_id, keep, moves in CLIPS:
        s, e = hd.clip(hd_id)
        length = min(e - s, keep) if keep else e - s
        times = list(range(0, length, STEP_MS)) + [length]
        for t in times:
            cache = {}
            world = {}
            for i in range(n_bone):
                p = bones[i]['parent']
                pw = world[p] if p != -1 else (0.0, 0.0, 0.0, 1.0)
                if i in MAP:
                    world[i] = qnorm(qmul(hd.world(MAP[i][0], s + t, cache)[0], align[i]))
                else:
                    world[i] = pw
                rot_keys[i].append((start + t, qnorm(qmul(qinv(pw), world[i]))))
            # the pelvis moves as the HD pelvis's pivot does, scaled
            r, tr = hd.world(HD_PELVIS, s + t, cache)
            piv = hd.pivots[HD_PELVIS]
            moved = [qrot(r, piv)[k] + tr[k] - piv[k] for k in range(3)]
            pelvis_keys.append((start + t, tuple(x * scale for x in moved) if moves else (0.0, 0.0, 0.0)))
        new_seqs.append((anim_id, start, start + length))
        start += length + 1000

    # ---- write: new arrays go at the end of the file, their headers repointed
    def append(blob):
        while len(m2) % 16:
            m2.append(0)
        off = len(m2)
        m2.extend(blob)
        return off

    # sequences: the old ones and the two new, from Jump's record
    seq_blob = bytearray(m2[o_seq:o_seq + n_seq * SEQ_SIZE])
    for k, (anim_id, s, e) in enumerate(new_seqs):
        rec = bytearray(m2[o_seq + template * SEQ_SIZE:o_seq + (template + 1) * SEQ_SIZE])
        struct.pack_into('<HHII', rec, 0, anim_id, 0, s, e)
        struct.pack_into('<f', rec, 0x0c, 0.0)                          # moveSpeed
        struct.pack_into('<hH', rec, 0x40, -1, n_seq + k)                # next, alias
        seq_blob.extend(rec)
    struct.pack_into('<II', m2, 0x1c, n_seq + len(new_seqs), append(seq_blob))
    slots = {anim_id: n_seq + k for k, (anim_id, _, _) in enumerate(new_seqs)}

    # the animation lookup and the playable lookup name the new ids as themselves
    n_look, o_look = u32(0x24), u32(0x28)
    look = list(le('<%dh' % n_look, m2, o_look))
    while len(look) <= max(slots):
        look.append(-1)
    for anim_id, slot in slots.items():
        look[anim_id] = slot
    struct.pack_into('<II', m2, 0x24, len(look), append(struct.pack('<%dh' % len(look), *look)))
    n_play, o_play = u32(0x2c), u32(0x30)
    play = [le('<HH', m2, o_play + 4 * k) for k in range(n_play)]
    while len(play) <= max(slots):
        play.append((len(play), 0))
    for anim_id in slots:
        play[anim_id] = (anim_id, 0)
    struct.pack_into('<II', m2, 0x2c, len(play),
                     append(b''.join(struct.pack('<HH', *p) for p in play)))

    # bone tracks: new keys in the new bands, the ranges slots for the new sequences pointed at them
    def extend_track(track, new_keys, fmt):
        gseq = le('<h', m2, track + 2)[0]
        n_r, o_r = u32(track + 4), u32(track + 8)
        n_t, o_t = u32(track + 0x0c), u32(track + 0x10)
        o_v = u32(track + 0x18)
        if gseq != -1 or n_t == 0:
            return False
        size = struct.calcsize(fmt)
        ts = list(le('<%dI' % n_t, m2, o_t))
        vals = bytes(m2[o_v:o_v + n_t * size])
        ranges = [le('<II', m2, o_r + 8 * k) for k in range(n_r)]
        while len(ranges) < n_seq + len(new_seqs):
            ranges.append((0, 0))
        out_v = bytearray(vals)
        for anim_id, s, e in new_seqs:
            lo = len(ts)
            for t, v in new_keys:
                if s <= t <= e:
                    ts.append(t)
                    out_v.extend(struct.pack(fmt, *v))
            ranges[slots[anim_id]] = (lo, len(ts) - 1)
        struct.pack_into('<II', m2, track + 0x0c, len(ts), append(struct.pack('<%dI' % len(ts), *ts)))
        struct.pack_into('<II', m2, track + 0x14, len(ts), append(bytes(out_v)))
        struct.pack_into('<II', m2, track + 4, len(ranges),
                         append(b''.join(struct.pack('<II', *r) for r in ranges)))
        return True

    holds_t = [(s, (0.0, 0.0, 0.0)) for _, s, _ in new_seqs] + [(e, (0.0, 0.0, 0.0)) for _, _, e in new_seqs]
    holds_s = [(s, (1.0, 1.0, 1.0)) for _, s, _ in new_seqs] + [(e, (1.0, 1.0, 1.0)) for _, _, e in new_seqs]
    holds_t.sort()
    holds_s.sort()
    missing = []
    for i in range(n_bone):
        b = o_bone + i * BONE_SIZE
        extend_track(b + 0x0c, pelvis_keys if i == PELVIS else holds_t, '<3f')
        if not extend_track(b + 0x28, rot_keys[i], '<4f') and i in MAP:
            missing.append(i)
        extend_track(b + 0x44, holds_s, '<3f')
    if missing:
        raise SystemExit('matched bones without a rotation track: %s' % missing)
    open(out_path, 'wb').write(m2)
    for anim_id, s, e in new_seqs:
        print('sequence %d: %d-%d (%d ms)' % (anim_id, s, e, e - s))
    print('wrote', out_path, len(m2), 'bytes')


if __name__ == '__main__':
    port(*sys.argv[1:4])
