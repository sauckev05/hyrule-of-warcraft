#!/usr/bin/env python3
"""The hero's look, for player human males only (Galahad; NPC humans keep the stock model and voice).

- Character\\Human\\Male\\HumanMaleHero.m2: the stock body (patch-Z's HumanMale.m2, with the ported
  rolls) reshaped slimmer and younger (hero/deform.py, variant B) on the same skeleton, so every
  animation still fits; every cloak shape is the split cape, made longer; the emote sounds in its
  animations point at the young voice.
- Its own CreatureModelData / CreatureDisplayInfo / CreatureSoundData rows; ChrRaces gives it to
  every human male player, character creation included. The server needs the same ChrRaces,
  CreatureDisplayInfo and CreatureModelData (written as server-*.dbc beside the patch).
- The young voice: the 155 human male player sounds sped up 26% with reverb (variant C), under
  Sound\\Character\\ZeldaHero, in their own SoundEntries rows; the hero's grunts (CreatureSoundData),
  error speech (VocalUISounds) and text emotes (EmotesTextSound) use them.
- The young face: face 0 in all ten skin colours, softened (CharSections points at the new files).

usage: build_hero.py                                      writes zelda-sql/024_hero.sql
       build_hero.py <client dbc dir> <HumanMale.m2> <face dir> <voice dir> <out dir> [<NightElfMale.m2>]
                                                          writes the patch files and server DBCs
"""
import math
import json
import os
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_mastery import read_dbc, write_dbc, add_string     # noqa: E402

HERO_MODEL = 'Character\\Human\\Male\\HumanMaleHero.mdx'
HERO_M2 = HERO_MODEL[:-4] + '.m2'
STOCK_MODEL_ID = 49           # CreatureModelData / CreatureDisplayInfo / CreatureSoundData of the human male
STOCK_FEMALE_DISPLAY = 50
HERO_MODEL_ID = 2400          # CreatureModelData (stock ends at 2365)
HERO_DISPLAY = 17560          # CreatureDisplayInfo (stock ends at 17548, the Scarlet Warhorse is 17549)
HERO_SOUND = 2300             # CreatureSoundData (stock ends at 2230)
SOUND_BASE = 20000            # SoundEntries of the young voice (stock ends at 9432)
HUMAN = 1
VOICE_DIRS = {
    'Sound\\Character\\Human\\Male': 'Sound\\Character\\ZeldaHero\\Male',
    'Sound\\Character\\Human\\MaleErrorMessages': 'Sound\\Character\\ZeldaHero\\MaleErrorMessages',
    'Sound\\Character\\Human\\HumanVocalMale': 'Sound\\Character\\ZeldaHero\\HumanVocalMale',
    'Sound\\Character\\PlayerExertions\\HumanMaleFinal': 'Sound\\Character\\ZeldaHero\\HumanMaleFinal',
}
# the voice demo's variant C without its room: 26% faster (about +4 semitones), dry, so it sounds
# like the speaker is right there rather than in a hall
VOICE_FILTER = 'asetrate=22050*1.26,aresample=22050,apad=pad_dur=0.1'
FACE = 0                      # the face the young look is painted on, in every skin colour
FACE_FILE = 'Character\\Human\\Male\\HumanMaleFace%sHero%02d_%02d.blp'
# no stock human male facial hair is clean shaven (style 0 is a moustache and goatee): for players,
# style 0 is a bare face (see-through facial hair textures)
CLEAN_FACIAL_STYLE = 0
NO_FACIAL_HAIR = ('Character\\Human\\FacialLowerHairHeroNone.blp', 'Character\\Human\\FacialUpperHairHeroNone.blp')
HERO_SCALE = 0.90             # the whole hero, a little shorter: a 17-year-old beside grown men
HERO_HEAD = 0.97              # the head (and hair and helm) a touch under stock, to suit the slim body
# worn pieces on the young body: the shoulder pads shrink with the narrower shoulders, the helm grows
# with the bigger head, and every attachment point moves with the skin around it
SHOULDER_ATTACH = (5, 6)
SHOULDER_PAD_SCALE = 1.0       # the stock shoulder pads, their normal size
# the worn gauntlet cuffs (forearm geosets 402-404) and boot tops (shin geosets 502-504) can bulk out;
# 1.0 keeps them as the slim body has them (1.25 and 1.15 were tried and set aside)
# around the limb, like armour over a slim arm or leg (the bare forearm 401 and leg 501 stay slim)
ARMOUR_GEOSETS = {402: (78, 95, 79, 97), 403: (78, 95, 79, 97), 404: (78, 95, 79, 97),
                  502: (53, 68, 54, 70), 503: (53, 68, 54, 70), 504: (53, 68, 54, 70)}
ARMOUR_BULK = 1.0
HELM_ATTACH = 11
HEAD_BONE = 64
# the nose: smaller and pointed, a triangle seen from the side (bridge straight down to a sharp tip,
# underside straight back), in the stock model's units; only the head bone's own vertices
NOSE = dict(top=(1.905, 0.165), tip=(1.852, 0.176), base=(1.838, 0.150), plane=0.147,
            zmin=1.835, zmax=1.91, ymax=0.046, xmin=0.140, width=0.75, depth=0.85, round=0.45)
# the cape: every cloak wears one shape; 'split' is the split cape (1504) stretched from the shoulder
# blades down, 'full' the long cape (1502) made a wide cloak hanging from over the shoulders, its
# edges coming round the legs (CAPE_FULL_BOTTOM: where it ends)
CAPE_STYLE = 'full'
CAPE_FULL_BOTTOM = 0.10            # W3: the worn hem's longest tips, down by the ankles (straight hem was 0.40)
CAPE_SHOULDER = 0.26               # how far out over the backs of the shoulders the full cloak spreads
CAPE_ARM_GAP_HALF = 0.27           # under the shoulders, the cloak's half width (0: as wide as CAPE_SHOULDER)
CAPE_HEM_HALF = 0.40               # the hem's half width
CAPE_EDGE_X = -0.17                # the edges' depth under the shoulders (more negative: further back)
CAPE_EDGE_FORWARD = 0.10           # how far forward the edges come by the hem
# the half width down the cloak, (0 under the shoulders .. 1 at the hem, half width): narrow at the
# waist with the body, wider going down; None: straight from CAPE_ARM_GAP_HALF to CAPE_HEM_HALF
CAPE_PROFILE = [(0, 0.185), (0.19, 0.16), (0.41, 0.22), (0.63, 0.30), (0.82, 0.38), (1, 0.46)]   # T2, N2 shoulders (N1: 0.29 / 0.20, 0.165; N3: 0.235 / 0.17, 0.155)
# the full cloak's worn hem: None for a straight hem; else teeth (tips across), depth (how far up the
# tears reach, model units), uneven (spacing jitter), tip_wear / tear_min (tips' and tears' share of
# the depth), seed; CAPE_FULL_BOTTOM is then where the longest tips end
CAPE_TATTER = dict(teeth=6, depth=0.17, uneven=0.5, tip_wear=0.3, tear_min=0.6, seed=11)   # W3
# the scarf every cape wears round the neck (None: none): a thick roll on the shoulders under the helm
# S1, the donut roll it replaced: shape roll, two wraps (see git history)
CAPE_COWL = dict(  # R2 (from F3): the scarf rests on the body like a mound, two soft round rolls in front, wide behind
    x=0.015,
    u=(0.35, 0.95),
    v=(0.3, 0.6),
    seed=5,
    neck_share=0.5,
    lean=0.0,
    shape='mound',
    neck=dict(front=(0.09, 0.08), back=(0.10, 0.085)),       # behind: up under the helm's back edge (F3 had 0.09, 0.08)
    top_z=dict(front=1.765, back=1.82),                    # (F3 had 1.77, which left a gap under some helms)
    front_dip=0.03,
    foot=(0.165, 0.19, 0.2),
    lean_in=dict(front=0.15, back=0.1),
    foot_min_z=1.56,
    bulge=dict(front=0.04, back=0.065),                   # front thinner (R2 had 0.06), same width
    folds=dict(front=0.2, back=0.15),
    fold_count=11,
    front_bulge=0.15,
    peak=dict(front=0.55, back=0.6),
    round=dict(front=0.7, back=1.0),                       # R2: the front rounded
    lift=0.006,
    tuck=0.02,
    v_bands=2,
    rows=20,
    ridges=((0.3, 0.014, 0.16), (0.72, 0.016, 0.18)),       # R2's two soft round rolls, thinner (0.02, 0.022)
    ridge_spread=1.5,
)
CAPE_PROFILE_BOTTOM = 0.40         # with a worn hem: where CAPE_PROFILE's shape ends (T2 was drawn to 0.40)
CAPE_BORDER_V = 0.90               # with a worn hem: the texture v above which the hem's border is drawn to scale
CAPE_FLARE = 0.22                  # below that, how fast the half width keeps widening (per profile length)
FULL_CAPE = 1502
NO_CAPE = 1501                 # the upper back's no-cape piece
# the tabard's lower part (1202) as a long surcoat (None: as stock): the front and back flaps hang
# down to front_bottom / back_bottom (model units; stock 0.53 / 0.66), widening by flare at the hem;
# the front is slit up the middle from its second row, each half following its own thigh more the
# lower it hangs (leg_share at the hem), the halves gap apart by gap (at the slit's top, at the hem)
TABARD_LONG = None     # L2 (tried): dict(front_bottom=0.2, back_bottom=0.24, flare=0.3, gap=(0.008, 0.03), leg_share=1.0, top_share=0.35, calm=True)
TABARD = 1202
# or the tabard's lower part as a long surcoat skirt (None: not), the robe skirt's shape (1302) in the
# tabard's colours (the stock flaps' part of the body texture): it replaces the flaps, sits push out
# over a robe, and is slit up the front from slit_z with the halves gap apart (at the slit's top, at
# the hem); hem_z cuts it shorter (0: the robe's own length, to the ankles)
TABARD_SKIRT = dict(push=0.03, hip_push=0.03, slit_z=0.9, gap=(0.008, 0.05), hem_z=0.3)   # K3
ROBE = 1302
CAPE_COVER_BACK = True         # keep that piece on the body under the cloak (the yoke no longer covers it)
SPLIT_CAPE = 1504
CAPE_ANCHOR_Z = 1.40          # model units; the cape keeps its shape above this
CAPE_BOTTOM_Z = 0.40          # the split cape's tails end at mid-calf (stock: 0.73, at the thigh)
CAPE_BACK_SHARE = 0.4         # how much of the extra length also leans back, off the legs
# the galahad character (the core's one-time change): hair style 6 is geoset 7, colour 6 golden blond
SQL_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zelda-sql', '024_hero.sql')
# key 5 in the saddle (ZeldaSpur): each red circle the hero grunts, in turn, as on the forward roll, the
# backflip and the side rolls (Benilla's ROLL_SOUNDS), and the mount gives its next attack sound
SPUR_VOICE_BASE = 20190
SPUR_VOICE_FILES = ('HumanMaleMainAttackC.wav', 'HumanMaleMainAttackA.wav', 'HumanMaleMainAttackB.wav')
MOUNT_ATTACKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mount_attack_sounds.json')


# ---------------------------------------------------------------- the model

def _shape_nose(m):
    """Reshape the nose in the stock positions (the body deform then carries it with the head)."""
    n = NOSE
    (zt, xt), (zp, xp), (zb, xb) = n['top'], n['tip'], n['base']
    for v in m.verts:
        x, y, z = v['pos']
        if not (n['zmin'] <= z <= n['zmax'] and abs(y) <= n['ymax'] and x >= n['xmin']):
            continue
        if v['bi'][0] != HEAD_BONE or v['w'][0] != 255:
            continue
        if v['uv'][0] > 0.1 or v['uv'][1] > 0.9:
            continue        # not the nose's own skin: the eyes beside it (their swatch) keep their place
        # the profile at this height: the bridge line above the tip, the underside line below
        if z >= zp:
            u = min(1.0, (z - zp) / (zt - zp))
            # the bridge: straight, or scooped in a little above the tip (a young, short nose)
            prof = xp + (xt - xp) * u - n.get('scoop', 0.0) * math.sin(math.pi * u)
        else:
            prof = xp + (xb - xp) * min(1.0, (zp - z) / (zp - zb))
        # off the middle the nose falls away (a narrow ridge), then the whole nose sits lower
        x2 = min(x, prof - n['round'] * abs(y))
        x2 = n['plane'] + (x2 - n['plane']) * n['depth']
        v['pos'] = (max(x2, min(x, n['plane'])), y * n['width'], z)


def _full_cape(m, pos):
    """The long cape (1502) as a wide cloak hanging behind: its top spreads over the backs of the
    shoulders (CAPE_SHOULDER: how far out), the panel falls straight and widens to CAPE_FULL_BOTTOM,
    its edges coming forward beside the legs; the front stays open."""
    verts = set()
    for s in m.subs:
        if s['id'] == FULL_CAPE:
            verts |= {m.vlookup[m.tris[t]] for t in range(s['st'], s['st'] + s['nt'])}
    top, stock_bottom = 1.42, 0.335
    w = CAPE_SHOULDER                                   # the shoulder line's half width
    # the yoke (stock vertex ids, left/right) laid over the backs of the shoulders
    YOKE = {(2285, 2288): (-0.02, 0.20, 1.735),        # beside the neck, on the shoulder top
            (2271, 2272): (-0.14, 0.15, 1.705),        # behind the neck
            (2243, 2240): (-0.20, 0.21, 1.585),        # between the shoulder blades
            (2278, 2279): (-0.12, w - 0.04, 1.705),    # the back of the shoulder top
            (2286, 2287): (-0.15, w, 1.585)}           # down the back of the shoulder, to the arm
    yoke = {}
    for (a, b), place in YOKE.items():
        yoke[a] = place
        yoke[b] = place
    for v in verts:
        x0, y0, z0 = m.verts[v]['pos']
        side = 1.0 if y0 >= 0 else -1.0
        if v in yoke:
            nx, ny, nz = yoke[v]
            pos[v] = (nx, side * ny, nz)
            continue
        if z0 >= 1.45:
            continue
        u = max(0.0, min(1.0, (top - z0) / (top - stock_bottom)))      # 0 at the back, 1 at the hem
        row_half = 0.176 + (0.367 - 0.176) * u
        s_ = min(1.0, abs(y0) / row_half)                             # 0 middle .. 1 edge
        pos[v] = _cloak_at(u, side * s_)          # the stock hem row stays at the profile's own end


def _profile_bottom():
    """Where CAPE_PROFILE ends (u = 1): the straight hem's height, or, with a worn hem, where the
    T2 shape was drawn to (CAPE_PROFILE_BOTTOM), the cloak hanging on below it to its tips."""
    return CAPE_PROFILE_BOTTOM if CAPE_TATTER else CAPE_FULL_BOTTOM


def _cloak_at(u, s):
    """A point of the full cloak: u 0 under the shoulders .. 1 at the profile's end (past 1 the worn
    hem's extra length, flaring on by CAPE_FLARE), s -1 .. 1 across."""
    if CAPE_PROFILE and u > 1.0:
        half = CAPE_PROFILE[-1][1] + CAPE_FLARE * (u - 1.0)
    elif CAPE_PROFILE:                                                  # the half width down its length
        pts = CAPE_PROFILE
        k = next(i for i in range(len(pts) - 1) if u <= pts[i + 1][0] or i == len(pts) - 2)
        (u0, h0), (u1, h1) = pts[k], pts[k + 1]
        t = max(0.0, min(1.0, (u - u0) / ((u1 - u0) or 1.0)))
        t = t * t * (3 - 2 * t)                                       # eased, so the curve is smooth
        half = h0 + (h1 - h0) * t
    else:
        top_half = CAPE_ARM_GAP_HALF if CAPE_ARM_GAP_HALF else CAPE_SHOULDER + 0.01
        half = top_half + (CAPE_HEM_HALF - top_half) * u              # the new half width
    x_mid = -0.20 - 0.10 * u                                          # the middle hangs behind
    x_edge = CAPE_EDGE_X + CAPE_EDGE_FORWARD * min(u, 1.0)            # the edges come round the legs
    nz = 1.42 - u * (1.42 - _profile_bottom())
    return (x_mid + (x_edge - x_mid) * s * s, s * half, nz)


def _hem_profile():
    """The worn hem: (s, how far up the cut reaches, in model units) from edge to edge; tips and
    tears alternate, their spacing and depth uneven (a fixed seed, so every build is the same)."""
    import random
    t = CAPE_TATTER
    rnd = random.Random(t['seed'])
    n = t['teeth']
    gaps = [1.0 + rnd.uniform(-t['uneven'], t['uneven']) for _ in range(2 * n - 2)]
    total = sum(gaps)
    pts, s = [], -1.0
    for i in range(2 * n - 1):
        tip = i % 2 == 0
        cut = t['depth'] * (rnd.uniform(0.0, t['tip_wear']) if tip else rnd.uniform(t['tear_min'], 1.0))
        pts.append((s, cut))
        if i < 2 * n - 2:
            s += 2.0 * gaps[i] / total
    pts[-1] = (1.0, pts[-1][1])
    return pts


HEM = (2257, 2250, 2249, 2251, 2255)              # the full cloak's hem row, stock vertex ids


def _hem_geometry(m, d, pos, recs):
    """The worn hem (CAPE_TATTER): a finer strip replacing the full cloak's last band (from the row
    above the hem down), its bottom torn into uneven points. The band hangs on one bone, so every new
    vertex copies a hem vertex (weights, normal) with its own position and texture coordinate; the
    texture is cut with the cloth, so the tears bite into the hem's border. New vertex records go on
    recs; returns the faces (global vertex ids)."""
    ROW = (2256, 2253, 2248, 2252, 2254)          # the row above it (u ~0.81), stock vertex ids
    span = 1.42 - _profile_bottom()
    u_end = (1.42 - CAPE_FULL_BOTTOM) / span       # the longest tips
    u_row = sum((1.42 - pos[v][2]) / span for v in ROW) / len(ROW)
    prof = _hem_profile()
    cols = [s for s, _ in prof]
    rows = CAPE_TATTER.get('rows', 7)
    first = u_row + 0.2 * (u_end - CAPE_TATTER['depth'] / span - u_row)
    v_row, v_hem = m.verts[ROW[2]]['uv'][1], m.verts[HEM[2]]['uv'][1]
    def tex_u(s):                                  # the stock columns' texture u, mirrored about the middle
        a = abs(s)
        return 0.984 + (0.617 - 0.984) * a / 0.62 if a <= 0.62 else 0.617 + (0.25 - 0.617) * (a - 0.62) / 0.38
    # the texture down the strip: the hem's border keeps its stock scale (texture per model unit, as
    # the band above the stock hem had it) at the bottom; the extra length takes the plain cloth just
    # above the border (from the row's v to CAPE_BORDER_V), so no cape's border stretches
    rate = (v_hem - v_row) / ((1.0 - u_row) * span)
    h_border = (v_hem - CAPE_BORDER_V) / rate
    h_row = (u_end - u_row) * span
    def tex_v(u):
        h = (u_end - u) * span                     # how far above the longest tips
        if h <= h_border:
            return v_hem - h * rate
        return CAPE_BORDER_V - (h - h_border) / max(1e-6, h_row - h_border) * (CAPE_BORDER_V - v_row)
    def src(s):                                    # the hem vertex the new one copies
        return HEM[min(range(5), key=lambda k: abs((-1, -0.62, 0, 0.62, 1)[k] - s))]
    o_v = struct.unpack_from('<I', d, 0x48)[0]
    grid = []                                      # grid[r][c] = global vertex id
    for r in range(rows + 1):
        line = []
        for s, cut in prof:
            u_bot = u_end - cut / span
            u = first + (u_bot - first) * r / rows
            p = _cloak_at(u, s)
            rec = bytearray(d[o_v + src(s) * 48:o_v + src(s) * 48 + 48])
            struct.pack_into('<3f', rec, 0, *p)
            struct.pack_into('<2f', rec, 32, tex_u(s), tex_v(u))
            line.append(len(recs) // 48)
            recs += rec
        grid.append(line)
    # faces: the row above zipped to the strip's first row, then the strip's quads
    row_s = [_signed_s(pos, v) for v in ROW]
    faces = []
    i = j = 0
    while i < len(ROW) - 1 or j < len(cols) - 1:
        if j == len(cols) - 1 or (i < len(ROW) - 1 and row_s[i + 1] <= cols[j + 1]):
            faces.append((ROW[i], ROW[i + 1], grid[0][j])); i += 1
        else:
            faces.append((ROW[i], grid[0][j + 1], grid[0][j])); j += 1
    for r in range(rows):
        for c in range(len(cols) - 1):
            a, b, e, f = grid[r][c], grid[r][c + 1], grid[r + 1][c], grid[r + 1][c + 1]
            faces += [(a, b, e), (b, f, e)]
    return faces


def _cowl_geometry(m, d, recs, pos):
    """The scarf (CAPE_COWL): a thick roll of the cape's cloth wound round the base of the neck,
    resting on the shoulders under any helm, bunched in folds and drooping lower in front. A closed
    tube: around the neck (theta, 0 at the front) and round its own cross-section (phi). Weighted to
    the chest (bone 22) and, toward its top, partly the neck (48). Returns faces, outward-facing."""
    if CAPE_COWL.get('shape') == 'mound':
        return _mound_geometry(m, d, recs, pos, CAPE_COWL)
    faces = []
    for layer in CAPE_COWL.get('layers', [{}]):
        faces += _cowl_layer(d, recs, dict(CAPE_COWL, **layer))
    return faces


def _mound_geometry(m, d, recs, pos, c):
    """The scarf as a mound: from a lip tucked round the neck just under the helm, the cloth falls
    outward and down in a rounded slope to rest on the body (the chest, the shoulder tops, and the
    cloak's yoke behind), like a mountain round the neck rather than a ring standing off it. Where it
    meets the body is found by casting, for each way round the neck, a line in toward the neck from
    outside (the outermost surface it meets); the cloth there takes that surface's own bone weights,
    so it stays on the chest and shoulders as they move, blending to the chest and neck at the top."""
    import math, random
    import numpy as np
    rnd = random.Random(c.get('seed', 5))
    ph = [rnd.uniform(0, 2 * math.pi) for _ in range(4)]
    # the surfaces it can rest on: the body (0) and the cloak (its yoke)
    tri_v = []
    for sm in m.subs:
        if sm['id'] in (0, FULL_CAPE):
            tri_v += [[m.vlookup[m.tris[t + k]] for k in range(3)] for t in range(sm['st'], sm['st'] + sm['nt'], 3)]
    tri_v = np.array(tri_v)
    P = np.array(pos, dtype=float)
    A, B, C = P[tri_v[:, 0]], P[tri_v[:, 1]], P[tri_v[:, 2]]
    E1, E2 = B - A, C - A
    def cast(o, dr):
        """The first surface along o + t dr (t > 0): (point, triangle index, barycentric) or None."""
        h = np.cross(dr, E2); det = (E1 * h).sum(1)
        ok = np.abs(det) > 1e-9
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        sv = o - A; u = (sv * h).sum(1) * inv
        q = np.cross(sv, E1); v = (q * dr).sum(1) * inv
        t = (q * E2).sum(1) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
        if not hit.any():
            return None
        k = int(np.argmin(np.where(hit, t, np.inf)))
        return o + t[k] * dr, k, (1 - u[k] - v[k], u[k], v[k])
    def weights_of(k, bary):
        w = {}
        for vi, bw in zip(tri_v[k], bary):
            vv = m.verts[int(vi)]
            for bone, ww in zip(vv['bi'], vv['w']):
                if ww:
                    w[bone] = w.get(bone, 0.0) + bw * ww / 255.0
        return w
    def crease(th):
        k = c['fold_count']
        return (math.sin(k * th / 2 + ph[0]) ** 2 + 0.01) ** 0.25 * (0.75 + 0.25 * math.sin(3 * th + ph[1])) - 0.6
    def par(name, th, default=None):
        """A setting, or one blended round the neck from its 'front' to its 'back' value."""
        val = c.get(name, default)
        if isinstance(val, dict):
            wb = (1 - math.cos(th)) / 2
            wb = wb * wb * (3 - 2 * wb)
            if isinstance(val['front'], (list, tuple)):
                return [f + (b_ - f) * wb for f, b_ in zip(val['front'], val['back'])]
            return val['front'] + (val['back'] - val['front']) * wb
        return val
    nt = c.get('around', 64)
    rows = c.get('rows', 10)
    top_w = {22: 1.0 - c.get('neck_share', 0.5), 48: c.get('neck_share', 0.5)}
    o_v = struct.unpack_from('<I', d, 0x48)[0]
    base = bytearray(d[o_v + HEM[2] * 48:o_v + HEM[2] * 48 + 48])
    cols = []                                       # per way round: [(point, weights, t)]
    for i in range(nt):
        th = 2 * math.pi * i / nt
        cs, sn = math.cos(th), math.sin(th)
        front, back = max(0.0, cs) ** 2, max(0.0, -cs) ** 2
        # where it rests: a ring round the neck (front, side, back reach), dropped onto the surface
        # below from just under the chin, leaning in a little
        reach = c['foot'][1] + (c['foot'][0] - c['foot'][1]) * front + (c['foot'][2] - c['foot'][1]) * back
        ring = np.array([c['x'] + reach * cs, reach * sn, par('top_z', th) - 0.01])
        li = par('lean_in', th, 0.15)
        dr = np.array([-li * cs, -li * sn, -1.0]); dr /= np.linalg.norm(dr)
        got = cast(ring, dr)
        low = c.get('foot_min_z', 0.0)
        if got is None or got[0][2] < low:              # off the chest's front: rest on it at that height
            got = cast(np.array([c['x'] + (reach + 0.15) * cs, (reach + 0.15) * sn, low]), np.array([-cs, -sn, 0.0]))
        if got is None:
            foot, fw = ring + dr * 0.15, dict(top_w)
        else:
            foot, k, bary = got
            nrm = np.cross(E1[k], E2[k]); nrm /= (np.linalg.norm(nrm) or 1.0)
            if np.dot(nrm, dr) < 0:
                nrm = -nrm
            foot = foot + nrm * c.get('lift', 0.006)
            fw = weights_of(k, bary)
        zt = par('top_z', th) - c['front_dip'] * front
        nk = par('neck', th)
        top = np.array([c['x'] + nk[0] * cs, nk[1] * sn, zt])
        rr = np.array([cs, sn, 0.0])
        ch = foot - top
        d_r, d_z = float(np.dot(ch, rr)), float(ch[2])
        n_out = -d_z * rr + np.array([0.0, 0.0, d_r]); n_out /= (np.linalg.norm(n_out) or 1.0)
        bulge = par('bulge', th) * (1 + par('folds', th) * crease(th)) * (1 + c.get('front_bulge', 0.0) * front)
        ridge_w = ((1 + cs) / 2) ** c.get('ridge_spread', 1.0)          # the wraps show in front, fading behind
        col = [(top - rr * c.get('tuck', 0.02) - np.array([0, 0, 0.03]), top_w, -0.15)]     # the lip, tucked in
        for r in range(rows + 1):
            t = r / rows
            hump = math.sin(math.pi * t ** par('peak', th, 0.75)) ** par('round', th, 1.0)   # round < 1: fuller, rounder
            wraps = sum(hh * math.exp(-((t - tc) / ww) ** 2) for tc, hh, ww in c.get('ridges', ())) * ridge_w
            pt = top + ch * t + n_out * (bulge * hump + wraps)
            col.append((pt, None, t))
        col.append((foot - (foot - top) * 0.0 - n_out * 0.012, fw, 1.05))                  # tucked onto the body
        # weights down the slope: the top's, then the body's under it
        col = [(p, w if w is not None else None, t) for p, w, t in col]
        cols.append((col, fw, th))
    grid = []
    for col, fw, th in cols:
        line = []
        for p, w, t in col:
            s_ = max(0.0, min(1.0, t))
            if w is None:
                w = {}
                for bone, ww in top_w.items():
                    w[bone] = w.get(bone, 0.0) + (1 - s_) * ww
                for bone, ww in fw.items():
                    w[bone] = w.get(bone, 0.0) + s_ * ww
            top4 = sorted(w.items(), key=lambda kv: -kv[1])[:4]
            tot = sum(ww for _, ww in top4) or 1.0
            q = [int(round(255 * ww / tot)) for _, ww in top4]
            q[0] += 255 - sum(q)
            bones = [bone for bone, _ in top4] + [0] * (4 - len(top4))
            q += [0] * (4 - len(q))
            rec = bytearray(base)
            struct.pack_into('<3f', rec, 0, *map(float, p))
            struct.pack_into('<4B', rec, 12, *q)
            struct.pack_into('<4B', rec, 16, *bones)
            tu = c['u'][0] + (c['u'][1] - c['u'][0]) * ((1 - math.cos(th)) / 2) ** c.get('u_curve', 1.0) if c.get('u_curve') else c['u'][0] + (c['u'][1] - c['u'][0]) * (1 - abs(th / math.pi - 1))
            tt = max(0.0, min(1.0, t))
            tv = c['v'][0] + (c['v'][1] - c['v'][0]) * tt
            if c.get('v_bands'):                   # in front each wrap runs the texture over and back, as a roll does
                rolled = c['v'][0] + (c['v'][1] - c['v'][0]) * math.sin(math.pi * min(0.999, tt * c['v_bands'] % 1.0))
                rw = ((1 + math.cos(th)) / 2) ** c.get('ridge_spread', 1.0)
                tv += (rolled - tv) * rw
            struct.pack_into('<2f', rec, 32, tu, tv)
            line.append(len(recs) // 48)
            recs += rec
        grid.append(line)
    # normals from the neighbours, facing out (away from the neck, up the slope)
    def wp(g):
        return np.array(struct.unpack_from('<3f', recs, g * 48))
    n_rows = len(grid[0])
    for i in range(nt):
        th = 2 * math.pi * i / nt
        for j in range(n_rows):
            a_ = wp(grid[(i + 1) % nt][j]) - wp(grid[i - 1][j])
            b_ = wp(grid[i][min(j + 1, n_rows - 1)]) - wp(grid[i][max(j - 1, 0)])
            n = np.cross(a_, b_)
            out = np.array([math.cos(th), math.sin(th), 0.6])
            if np.dot(n, out) < 0:
                n = -n
            n /= (np.linalg.norm(n) or 1.0)
            struct.pack_into('<3f', recs, grid[i][j] * 48 + 20, *map(float, n))
    faces = []
    for i in range(nt):
        for j in range(n_rows - 1):
            a_, b_ = grid[i][j], grid[(i + 1) % nt][j]
            e_, f_ = grid[i][j + 1], grid[(i + 1) % nt][j + 1]
            for tri in ((a_, b_, e_), (b_, f_, e_)):
                p0, p1, p2 = (wp(g) for g in tri)
                vn = np.array(struct.unpack_from('<3f', recs, tri[0] * 48 + 20))
                faces.append(tri if np.dot(np.cross(p1 - p0, p2 - p0), vn) >= 0 else (tri[0], tri[2], tri[1]))
    return faces


def _cowl_layer(d, recs, c):
    """One wrap of the scarf (see _cowl_geometry)."""
    import math, random
    o_v = struct.unpack_from('<I', d, 0x48)[0]
    base = bytearray(d[o_v + HEM[2] * 48:o_v + HEM[2] * 48 + 48])
    rnd = random.Random(c.get('seed', 5))
    nt, nph = c.get('around', 48), c.get('cross', 12)
    ph = [rnd.uniform(0, 2 * math.pi) for _ in range(4)]
    def crease(th):                                                  # soft bulges between sharp creases, -0.6 .. 0.4
        k = c['fold_count']
        f = (math.sin(k * th / 2 + ph[0]) ** 2 + 0.01) ** 0.25 * (0.75 + 0.25 * math.sin(3 * th + ph[1]))   # rounded creases
        return f - 0.6
    def point(th, phi):
        front = ((1 + math.cos(th)) / 2) ** 3                       # 1 at the front, 0 behind
        fold = 1 + c['folds'] * crease(th)
        back = ((1 - math.cos(th)) / 2) ** 2                        # 1 behind, 0 in front
        R = c['bulk'] * fold * (1 + c['front_bulk'] * front + c.get('back_bulk', 0.0) * back)   # half thickness
        H = c['height'] * (1 + 0.15 * math.sin(3 * th + ph[2])) * (1 + c['front_drop'] * front * 0.5)
        zc = c['z'] - c['droop'] * front
        sag = 1 + c.get('sag', 0.3) * max(0.0, -math.sin(phi))       # the cloth settles: fuller low and out
        rho = (R + R * math.cos(phi)) * sag
        z = zc + H * math.sin(phi) - c.get('fold_sag', 0.0) * max(0.0, -crease(th)) * max(0.0, math.cos(phi))
        k = max(0.0, min(1.0, (c['z'] + c['height'] - z) / (2 * c['height'])))   # 0 top .. 1 bottom
        a = c['neck'][0] + (c['base'][0] - c['neck'][0]) * k        # the neck widening into the shoulders
        b = c['neck'][1] + (c['base'][1] - c['neck'][1]) * k
        a += c.get('back_out', 0.0) * back                           # behind: out over the cloak's yoke
        return (c['x'] + (a + rho) * math.cos(th), (b + rho) * math.sin(th), z)
    grid = []
    for i in range(nt):
        th = 2 * math.pi * i / nt
        line = []
        for j in range(nph):
            phi = 2 * math.pi * j / nph
            p = point(th, phi)
            e = 1e-3
            dt = [point(th + e, phi)[k] - point(th - e, phi)[k] for k in range(3)]
            dp = [point(th, phi + e)[k] - point(th, phi - e)[k] for k in range(3)]
            n = [dt[1] * dp[2] - dt[2] * dp[1], dt[2] * dp[0] - dt[0] * dp[2], dt[0] * dp[1] - dt[1] * dp[0]]
            out = [math.cos(phi) * math.cos(th), math.cos(phi) * math.sin(th), math.sin(phi)]
            if sum(n[k] * out[k] for k in range(3)) < 0:
                n = [-x for x in n]
            ln = math.sqrt(sum(x * x for x in n)) or 1.0
            rec = bytearray(base)
            struct.pack_into('<3f', rec, 0, *p)
            w48 = max(0.0, min(1.0, (p[2] - c['z'] + c['height']) / (2 * c['height']))) * c.get('neck_share', 0.5)
            w = round(255 * w48)
            struct.pack_into('<4B', rec, 12, 255 - w, w, 0, 0)
            struct.pack_into('<4B', rec, 16, 22, 48, 0, 0)
            struct.pack_into('<3f', rec, 20, *(x / ln for x in n))
            tu = c['u'][0] + (c['u'][1] - c['u'][0]) * (1 - abs(th / math.pi - 1))   # mirrored, no seam
            tv = c['v'][0] + (c['v'][1] - c['v'][0]) * (1 - abs(phi / math.pi - 1))
            struct.pack_into('<2f', rec, 32, tu, tv)
            line.append(len(recs) // 48)
            recs += rec
        grid.append(line)
    faces = []
    def wp(g):
        return struct.unpack_from('<3f', recs, g * 48)
    for i in range(nt):
        for j in range(nph):
            a, b = grid[i][j], grid[(i + 1) % nt][j]
            e, f = grid[i][(j + 1) % nph], grid[(i + 1) % nt][(j + 1) % nph]
            for tri in ((a, b, e), (b, f, e)):
                p0, p1, p2 = (wp(g) for g in tri)
                n = [(p1[1]-p0[1])*(p2[2]-p0[2]) - (p1[2]-p0[2])*(p2[1]-p0[1]),
                     (p1[2]-p0[2])*(p2[0]-p0[0]) - (p1[0]-p0[0])*(p2[2]-p0[2]),
                     (p1[0]-p0[0])*(p2[1]-p0[1]) - (p1[1]-p0[1])*(p2[0]-p0[0])]
                vn = struct.unpack_from('<3f', recs, tri[0] * 48 + 20)
                faces.append(tri if sum(n[k] * vn[k] for k in range(3)) >= 0 else (tri[0], tri[2], tri[1]))
    return faces




# the tabard's flaps, stock vertex ids by row (left, middle, right; y > 0 is the left)
TABARD_FRONT = [(2631, 2621, 2632), (2627, 2626, 2625), (2629, 2630, 2628), (2615, 2617, 2616)]
TABARD_BACK = [(2611, 2610, 2609), (2620, 2618, 2619), (2622, 2623, 2624), (2612, 2613, 2614)]
TABARD_SLIT_ROWS = (2, 3)                       # the front rows split down the middle
THIGHS = (25, 26)                               # the left and right thigh bones
PELVIS = 21
FRONT_FLAP_BONES = (24, 52, 67)                 # the stock front flap's own chain, which swings on the run


def _tabard_shape(m, pos):
    """Lengthen the tabard's flaps (TABARD_LONG): every row below the top is pushed down so the
    hem reaches its bottom, and the flap widens toward the hem."""
    t = TABARD_LONG
    for rows, bottom in ((TABARD_FRONT, t['front_bottom']), (TABARD_BACK, t['back_bottom'])):
        top = sum(pos[v][2] for v in rows[0]) / 3
        low = sum(pos[v][2] for v in rows[-1]) / 3
        k = (top - bottom) / (top - low)
        for row in rows[1:]:
            for v in row:
                x, y, z = pos[v]
                f = (top - z) / (top - low)            # 0 at the top .. 1 at the stock hem
                pos[v] = (x, y * (1 + t['flare'] * f * f), top - (top - z) * k)


def _tabard_geometry(m, d, recs):
    """The front of the long tabard slit up the middle: the slit rows' middle vertices get a twin
    for the right half (the triangles right of the middle take it), the two moved apart; each
    half's slit rows lean to their own thigh. Returns the tabard's triangles (global ids)."""
    t = TABARD_LONG
    o_v = struct.unpack_from('<I', d, 0x48)[0]
    tris = []
    for sm in m.subs:
        if sm['id'] == TABARD:
            tris += [[m.vlookup[m.tris[i + k]] for k in range(3)] for i in range(sm['st'], sm['st'] + sm['nt'], 3)]
            break
    def rec_pos(g):
        return struct.unpack_from('<3f', recs, g * 48)
    twin = {}
    n_slit = len(TABARD_SLIT_ROWS)
    for k, r in enumerate(TABARD_SLIT_ROWS):
        mid = TABARD_FRONT[r][1]
        frac = (k + 1) / n_slit                         # down the slit
        gap = t['gap'][0] + (t['gap'][1] - t['gap'][0]) * frac
        x, y, z = rec_pos(mid)
        new = len(recs) // 48
        recs += bytes(recs[mid * 48:mid * 48 + 48])
        struct.pack_into('<3f', recs, mid * 48, x, gap, z)
        struct.pack_into('<3f', recs, new * 48, x, -gap, z)
        twin[mid] = new
    calm = {b_: PELVIS for b_ in FRONT_FLAP_BONES} if t.get('calm') else {}
    def lean(g, side, share):
        """Blend vertex g's weights toward its side's thigh by share (with calm, the front flap's
        own swinging bones give way to the pelvis first)."""
        w = list(struct.unpack_from('<4B', recs, g * 48 + 12))
        bi = list(struct.unpack_from('<4B', recs, g * 48 + 16))
        acc = {}
        for b_, w_ in zip(bi, w):
            if w_:
                b_ = calm.get(b_, b_)
                acc[b_] = acc.get(b_, 0.0) + w_ / 255.0 * (1 - share)
        thigh = THIGHS[0] if side > 0 else THIGHS[1]
        acc[thigh] = acc.get(thigh, 0.0) + share
        top4 = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
        tot = sum(v for _, v in top4)
        q = [int(round(255 * v / tot)) for _, v in top4]
        q[0] += 255 - sum(q)
        struct.pack_into('<4B', recs, g * 48 + 12, *(q + [0] * (4 - len(q))))
        struct.pack_into('<4B', recs, g * 48 + 16, *([b_ for b_, _ in top4] + [0] * (4 - len(top4))))
    for k, r in enumerate(TABARD_SLIT_ROWS):
        share = t['leg_share'] * (k + 1) / n_slit
        left, mid, right = TABARD_FRONT[r]
        lean(left, 1, share); lean(mid, 1, share)
        lean(right, -1, share); lean(twin[mid], -1, share)
    # the rows above the slit: their sides lean a little too, so the halves turn with the legs
    # from there; with calm, the whole front hangs from the pelvis rather than its swinging bones
    top_share = t.get('top_share', 0.0)
    for r in range(TABARD_SLIT_ROWS[0]):
        left, mid, right = TABARD_FRONT[r]
        share = top_share if r == TABARD_SLIT_ROWS[0] - 1 else 0.0
        if share or calm:
            lean(left, 1, share); lean(right, -1, share)
            if calm:
                lean(mid, 1, 0.0)
    out = []
    for tri in tris:
        if any(v in twin for v in tri):
            others = [rec_pos(v)[1] for v in tri if v not in twin]
            if others and sum(others) / len(others) < 0:
                tri = [twin.get(v, v) for v in tri]
        out.append(tri)
    return out


def _tabard_skirt(m, d, recs):
    """The tabard as a long surcoat (TABARD_SKIRT): a copy of the robe skirt's mesh (with its leg
    weights, so it moves as a robe does), pushed out a little to sit over a robe, textured from the
    tabard's lower part as the stock flaps are (front and back mirrored round the legs, top to hem
    down the flaps' strip), and slit up the front. Returns the tabard's triangles (global ids)."""
    import math
    t = TABARD_SKIRT
    o_v = struct.unpack_from('<I', d, 0x48)[0]
    tris = []
    for sm in m.subs:
        if sm['id'] == ROBE:
            tris += [[m.vlookup[m.tris[i + k]] for k in range(3)] for i in range(sm['st'], sm['st'] + sm['nt'], 3)]
    def p_of(g):
        return struct.unpack_from('<3f', d, o_v + g * 48)
    if t.get('hem_z'):                              # shorter: only the bands above the cut
        tris = [tri for tri in tris if min(p_of(g)[2] for g in tri) >= t['hem_z'] - 0.02]
    verts = sorted({g for tri in tris for g in tri})
    top = max(p_of(g)[2] for g in verts)
    low = min(p_of(g)[2] for g in verts)
    cx = t.get('axis_x', 0.02)
    (u_mid, u_side), (v_top, v_hem) = t.get('u', (0.727, 0.895)), t.get('v', (0.371, 0.172))
    new_of, twin = {}, {}
    def place(g, dy=0.0):
        x, y, z = p_of(g)
        ang = math.atan2(y, x - cx)
        rad = math.hypot(x - cx, y) or 1.0
        # a little more out over the hips (below the belt, above the thighs part), where the legs'
        # own upper part (1301, which a robe would hide) is as wide as the skirt
        hz = t.get('hip_z', (1.1, 0.97, 0.75))
        hip = (top - z) / (top - hz[1]) if z > hz[1] else max(0.0, (z - hz[2]) / (hz[1] - hz[2]))
        push = t['push'] + t.get('hip_push', 0.0) * max(0.0, min(1.0, hip))
        x2 = x + push * (x - cx) / rad
        y2 = y + push * y / rad + dy
        a = abs(math.degrees(ang))
        f = a / 90.0 if a <= 90 else (180.0 - a) / 90.0
        rec = bytearray(d[o_v + g * 48:o_v + g * 48 + 48])
        struct.pack_into('<3f', rec, 0, x2, y2, z)
        struct.pack_into('<2f', rec, 32, u_mid + (u_side - u_mid) * f, v_top + (v_hem - v_top) * (top - z) / (top - low))
        recs.extend(rec)
        return len(recs) // 48 - 1
    for g in verts:
        x, y, z = p_of(g)
        front = abs(math.degrees(math.atan2(y, x - cx))) < 5.0 and x > cx
        if front and z < t['slit_z']:
            frac = (t['slit_z'] - z) / (t['slit_z'] - low)
            gap = t['gap'][0] + (t['gap'][1] - t['gap'][0]) * frac
            new_of[g] = place(g, gap)
            twin[g] = place(g, -gap)
        else:
            new_of[g] = place(g)
    out = []
    for tri in tris:
        pick = new_of
        if any(g in twin for g in tri):
            others = [p_of(g)[1] for g in tri if g not in twin]
            if others and sum(others) / len(others) < 0:
                pick = {g: twin.get(g, new_of[g]) for g in tri}
        out.append([pick[g] for g in tri])
    return out


def _cape_extras(m, d, pos):
    """Add the worn hem and the scarf to the full cloak's submesh (1502, the big one): the new
    vertices go on the end of the vertex list; every view shares the one index and triangle list,
    so the cloak's triangles are appended once and its submesh repointed in every view."""
    n_v, o_v = struct.unpack_from('<II', d, 0x44)
    recs = bytearray(d[o_v:o_v + n_v * 48])
    hem_faces = _hem_geometry(m, d, pos, recs) if CAPE_TATTER else []
    cowl_faces = _cowl_geometry(m, d, recs, pos) if CAPE_COWL else []
    tabard_tris = _tabard_skirt(m, d, recs) if TABARD_SKIRT else (_tabard_geometry(m, d, recs) if TABARD_LONG else None)
    drop = set(HEM) if CAPE_TATTER else set()
    n_new = len(recs) // 48
    while len(d) % 16:
        d.append(0)
    struct.pack_into('<II', d, 0x44, n_new, len(d))
    d += recs
    faces = hem_faces
    def wpos(g):
        return struct.unpack_from('<3f', d, struct.unpack_from('<I', d, 0x48)[0] + g * 48)
    done = {}
    for view in _views(d):
        n_i, o_i, n_t, o_t = struct.unpack_from('<IIII', d, view)
        n_sub, o_sub = struct.unpack_from('<II', d, view + 24)
        n_p, o_p = struct.unpack_from('<II', d, view + 16)
        if (o_i, o_t) not in done:
            idx = list(struct.unpack_from('<%dH' % n_i, d, o_i))
            tris = list(struct.unpack_from('<%dH' % n_t, d, o_t))
            props = bytes(d[o_p:o_p + n_p * 4])
            local = {g: k for k, g in enumerate(idx)}
            cape = next(k for k in range(n_sub) if struct.unpack_from('<H', d, o_sub + k * 32)[0] == FULL_CAPE
                        and local.get(HEM[2]) in tris[struct.unpack_from('<H', d, o_sub + k * 32 + 8)[0]:
                                                      sum(struct.unpack_from('<2H', d, o_sub + k * 32 + 8))])
            sv, nv, st, nt = struct.unpack_from('<4H', d, o_sub + cape * 32 + 4)
            drop_l = {local[g] for g in drop}
            keep = [tris[t:t + 3] for t in range(st, st + nt, 3) if not drop_l & set(tris[t:t + 3])]
            ref = keep[0]                          # the cloak's own facing, from a kept triangle
            def facing(tri_g):
                a, b, c = (wpos(g) for g in tri_g)
                n = [(b[1]-a[1])*(c[2]-a[2]) - (b[2]-a[2])*(c[1]-a[1]),
                     (b[2]-a[2])*(c[0]-a[0]) - (b[0]-a[0])*(c[2]-a[2]),
                     (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])]
                mid = [(a[k] + b[k] + c[k]) / 3 for k in range(3)]
                return n[0] * mid[0] + n[1] * mid[1]            # + : facing away from the body
            want = facing([idx[k] for k in ref]) > 0
            props += props[local[HEM[2]] * 4:local[HEM[2]] * 4 + 4] * n_new
            base = len(idx)
            for g in range(n_v, n_new):
                local[g] = len(idx); idx.append(g)
            new_tris = [k for tri in keep for k in tri]
            for f in faces:
                if (facing(f) > 0) != want:
                    f = (f[0], f[2], f[1])
                new_tris += [local[g] for g in f]
            for f in cowl_faces:
                new_tris += [local[g] for g in f]
            # the upper back: with a cape on, the game hides the no-cape piece (1501) and the stock
            # cape's collar covers that spot; the cloak's yoke no longer does, so the body keeps it:
            # 1501's triangles are added to the body's own submesh (0), always drawn
            body_rec, body_k = None, None
            if CAPE_COVER_BACK:
                ids = [struct.unpack_from('<H', d, o_sub + k * 32)[0] for k in range(n_sub)]
                if 0 in ids and NO_CAPE in ids:
                    body_k, k1 = ids.index(0), ids.index(NO_CAPE)
                    sv0, nv0, st0, nt0 = struct.unpack_from('<4H', d, o_sub + body_k * 32 + 4)
                    st1, nt1 = struct.unpack_from('<2H', d, o_sub + k1 * 32 + 8)
                    body = tris[st0:st0 + nt0] + tris[st1:st1 + nt1]
                    top = max(body) + 1
                    body_rec = (min(sv0, min(body)), top - min(sv0, min(body)), len(tris) + len(new_tris), len(body))
                    new_tris += body
            tab_rec, tab_k = None, None
            if tabard_tris is not None:
                ids = [struct.unpack_from('<H', d, o_sub + k * 32)[0] for k in range(n_sub)]
                if TABARD in ids:
                    tab_k = ids.index(TABARD)
                    tl = [local[g] for tri in tabard_tris for g in tri]
                    tab_rec = (min(tl), max(tl) + 1 - min(tl), len(tris) + len(new_tris), len(tl))
                    new_tris += tl
            arrs = []
            for data in (struct.pack('<%dH' % len(idx), *idx), struct.pack('<%dH' % (len(tris) + len(new_tris)), *(tris + new_tris)), props):
                while len(d) % 16:
                    d.append(0)
                arrs.append(len(d)); d += data
            cape_n = len(new_tris) - (body_rec[3] if body_rec else 0) - (tab_rec[3] if tab_rec else 0)
            done[(o_i, o_t)] = (len(idx), arrs[0], len(tris) + len(new_tris), arrs[1], len(props) // 4, arrs[2],
                                (sv, len(idx) - sv, len(tris), cape_n), cape, body_rec, body_k, tab_rec, tab_k)
        ni, oi, nt_, ot, np_, op, rec, cape, body_rec, body_k, tab_rec, tab_k = done[(o_i, o_t)]
        struct.pack_into('<IIIIII', d, view, ni, oi, nt_, ot, np_, op)
        for k in range(n_sub):
            if struct.unpack_from('<H', d, o_sub + k * 32)[0] == FULL_CAPE and k == cape:
                struct.pack_into('<4H', d, o_sub + k * 32 + 4, *rec)
        if body_rec is not None:
            struct.pack_into('<4H', d, o_sub + body_k * 32 + 4, *body_rec)
        if tab_rec is not None:
            struct.pack_into('<4H', d, o_sub + tab_k * 32 + 4, *tab_rec)




def _signed_s(pos, v):
    """Where a cloak vertex sits across (-1 .. 1), from its placed position."""
    x, y, z = pos[v]
    u = (1.42 - z) / (1.42 - _profile_bottom())
    half = abs(_cloak_at(u, 1.0)[1])
    return max(-1.0, min(1.0, y / half))


def _bulk_armour(m, pos):
    """Push the gauntlet cuffs and boot tops out from their limb's axis (elbow to wrist, knee to
    ankle on that side) by ARMOUR_BULK; the limb's length and the seam's height stay."""
    for sid, (a_left, b_left, a_right, b_right) in ARMOUR_GEOSETS.items():
        for s in m.subs:
            if s['id'] != sid:
                continue
            for v in {m.vlookup[m.tris[t]] for t in range(s['st'], s['st'] + s['nt'])}:
                p = pos[v]
                a, b = (a_left, b_left) if m.verts[v]['pos'][1] > 0 else (a_right, b_right)
                pa, pb = m.bones[a]['pivot'], m.bones[b]['pivot']
                axis = [pb[k] - pa[k] for k in range(3)]
                ll = sum(c * c for c in axis) or 1.0
                t = sum((p[k] - pa[k]) * axis[k] for k in range(3)) / ll
                foot = [pa[k] + axis[k] * t for k in range(3)]
                pos[v] = tuple(foot[k] + (p[k] - foot[k]) * ARMOUR_BULK for k in range(3))


def _views(d):
    n, o = struct.unpack_from('<II', d, 0x4c)
    return [o + i * 44 for i in range(n)]


def build_model(stock, sound_map):
    from hero.m2 import M2
    from hero import deform
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.m2', delete=False) as fh:
        fh.write(stock)
    m = M2(fh.name)
    os.unlink(fh.name)
    shape = dict(deform.VARIANTS['B'], head=HERO_HEAD)
    _shape_nose(m)
    pos = deform.deform(m, shape)
    if CAPE_STYLE == 'full':
        _full_cape(m, pos)
    # the split cape, longer: everything below the anchor is stretched down (and a little back)
    cape = set()
    for s in m.subs:
        if s['id'] == SPLIT_CAPE and CAPE_STYLE == 'split':
            for t in range(s['st'], s['st'] + s['nt']):
                cape.add(m.vlookup[m.tris[t]])
    low = min(pos[v][2] for v in cape) if cape else 0.0
    k = (CAPE_ANCHOR_Z - CAPE_BOTTOM_Z) / (CAPE_ANCHOR_Z - low)
    anchor_x = sum(pos[v][0] for v in cape if abs(pos[v][2] - CAPE_ANCHOR_Z) < 0.05) / \
        max(1, sum(1 for v in cape if abs(pos[v][2] - CAPE_ANCHOR_Z) < 0.05))
    for v in cape:
        x, y, z = pos[v]
        if z < CAPE_ANCHOR_Z:
            z = CAPE_ANCHOR_Z - (CAPE_ANCHOR_Z - z) * k
            x = anchor_x + (x - anchor_x) * (1 + (k - 1) * CAPE_BACK_SHARE)
            pos[v] = (x, y, z)
    if TABARD_LONG:
        _tabard_shape(m, pos)
    _bulk_armour(m, pos)
    m.write_positions(pos)
    d = m.data
    if CAPE_STYLE == 'full' and (CAPE_TATTER or CAPE_COWL or TABARD_LONG or TABARD_SKIRT):
        _cape_extras(m, d, pos)
    # every cloak shape draws the split cape: each other cape submesh takes the split cape's ranges
    # (its own id stays, so the cloak's geoset group still picks it), in every level of detail
    for view in _views(d):
        n_sub, o_sub = struct.unpack_from('<II', d, view + 24)
        subs = [(i, struct.unpack_from('<H', d, o_sub + i * 32)[0]) for i in range(n_sub)]
        keep = FULL_CAPE if CAPE_STYLE == 'full' else SPLIT_CAPE
        split = [i for i, sid in subs if sid == keep]
        for other in [c for c in (1502, 1503, 1504, 1505, 1506) if c != keep]:
            mine = [i for i, sid in subs if sid == other]
            for a, b in zip(mine, split):
                d[o_sub + a * 32 + 2:o_sub + a * 32 + 32] = d[o_sub + b * 32 + 2:o_sub + b * 32 + 32]
    _fit_attachments(m, d, pos, deform)
    # the animations' sound events ($CSD, the emotes' voices) play the young voice
    n_ev, o_ev = struct.unpack_from('<II', d, 0x114)
    for e in range(n_ev):
        r = o_ev + e * 44
        data = struct.unpack_from('<I', d, r + 4)[0]
        if d[r:r + 4] == b'$CSD' and data in sound_map:
            struct.pack_into('<I', d, r + 4, sound_map[data])
    return bytes(d)


def _const_scale(d, bone_rec, k):
    """Give a bone a constant scale: a one-key track on global sequence 0, the data appended."""
    while len(d) % 4:
        d.append(0)
    times = len(d)
    d += struct.pack('<I', 0)
    values = len(d)
    d += struct.pack('<3f', k, k, k)
    struct.pack_into('<Hh6I', d, bone_rec + 0x44, 1, 0, 0, 0, 1, times, 1, values)


def _fit_attachments(m, d, pos, deform):
    """Move every attachment point (and its own bone's pivot) with the skin around it, so worn and
    held things sit on the young body; shrink the shoulder pads and grow the helm with the head."""
    n_att, o_att = struct.unpack_from('<II', d, 0x104)
    skinned = {bi for v in m.verts for w, bi in zip(v['w'], v['bi']) if w}
    body = sorted({m.vlookup[m.tris[t]] for sub in m.subs if sub['id'] in (0, 401, 501)
                   for t in range(sub['st'], sub['st'] + sub['nt'])})     # the skin, not the cape or hair
    for a in range(n_att):
        rec = o_att + a * 48
        aid, bone = struct.unpack_from('<II', d, rec)
        if bone in skinned or bone >= len(m.bones):
            continue
        p = struct.unpack_from('<3f', d, rec + 8)
        bone_rec = m.o_bone + bone * 0x6c
        if aid == HELM_ATTACH:
            # the head bone's pivot with the head's own scale: the helm grows exactly as the head did
            head = HERO_HEAD
            struct.pack_into('<3f', d, bone_rec + 0x60, *m.bones[HEAD_BONE]['pivot'])
            _const_scale(d, bone_rec, head)
            continue
        near = sorted(body, key=lambda i: sum((m.verts[i]['pos'][k] - p[k]) ** 2 for k in range(3)))[:12]
        shift = [sum(pos[i][k] - m.verts[i]['pos'][k] for i in near) / len(near) for k in range(3)]
        q = tuple(p[k] + shift[k] for k in range(3))
        struct.pack_into('<3f', d, rec + 8, *q)
        if tuple(round(c, 4) for c in m.bones[bone]['pivot']) == tuple(round(c, 4) for c in p):
            struct.pack_into('<3f', d, bone_rec + 0x60, *q)
        if aid in SHOULDER_ATTACH:
            _const_scale(d, bone_rec, SHOULDER_PAD_SCALE)


# ---------------------------------------------------------------- the DBCs

def _str(strings, off):
    if not off:
        return ''
    return strings[off:strings.index(b'\0', off)].decode('latin1')


def _load(dbc_dir, name):
    return read_dbc(os.path.join(dbc_dir, name + '.dbc'))


def sound_entries(dbc_dir):
    """The young voice's SoundEntries rows (one per stock row in VOICE_DIRS) and old id -> new id."""
    f, rows, strings = _load(dbc_dir, 'SoundEntries')
    assert f == 29, f
    rows = [r for r in rows if r[0] < SOUND_BASE]
    mapping, files = {}, []
    new_rows = []
    for r in sorted(rows, key=lambda r: r[0]):
        directory = _str(strings, r[23])
        if directory not in VOICE_DIRS:
            continue
        new = list(r)
        new[0] = SOUND_BASE + len(new_rows)
        new[2] = add_string(strings, 'ZeldaHero ' + _str(strings, r[2]))
        new[23] = add_string(strings, VOICE_DIRS[directory])
        for v in r[3:13]:
            if v:
                files.append((directory + '\\' + _str(strings, v), VOICE_DIRS[directory] + '\\' + _str(strings, v)))
        mapping[r[0]] = new[0]
        new_rows.append(new)
    by_id = {r[0]: r for r in rows + new_rows}
    def single(new_id, parent, slot):
        """A SoundEntries row playing just one of `parent`'s files (the rest of it as the parent's)."""
        row = list(by_id[parent])
        name = _str(strings, row[3 + slot])
        row[0] = new_id
        row[2] = add_string(strings, 'Zelda %s %d' % (_str(strings, by_id[parent][2]), slot + 1))
        row[3:13] = [add_string(strings, name)] + [0] * 9
        row[13:23] = [by_id[parent][13 + slot] or 1] + [0] * 9
        return row
    # the hero's grunts on the spurs, in turn: the roll's, the backflip's, the side flip's
    hero_attack = mapping[2941]
    attack_files = [_str(strings, v) for v in by_id[hero_attack][3:13] if v]
    for k, wav in enumerate(SPUR_VOICE_FILES):
        new_rows.append(single(SPUR_VOICE_BASE + k, hero_attack, attack_files.index(wav)))
    # the mounts' attack sounds, a file each (build_mount_sounds.py)
    for new_id, parent, slot, _wav in json.load(open(MOUNT_ATTACKS))['entries']:
        new_rows.append(single(new_id, parent, slot))
    return write_dbc(f, rows + new_rows, strings), mapping, sorted(set(files))


def patch_creature_sound(dbc_dir, mapping):
    f, rows, strings = _load(dbc_dir, 'CreatureSoundData')
    assert f == 30, f
    rows = [r for r in rows if r[0] != HERO_SOUND]
    row = list(next(r for r in rows if r[0] == STOCK_MODEL_ID))
    row[0] = HERO_SOUND
    row = [row[0]] + [mapping.get(v, v) if i != 9 and i != 24 else v for i, v in enumerate(row[1:], 1)]
    rows.append(row)
    return write_dbc(f, sorted(rows, key=lambda r: r[0]), strings)


def patch_model_data(path):
    f, rows, strings = read_dbc(path)
    assert f == 16, f
    rows = [r for r in rows if r[0] != HERO_MODEL_ID]
    row = list(next(r for r in rows if r[0] == STOCK_MODEL_ID))
    row[0] = HERO_MODEL_ID
    row[2] = add_string(strings, HERO_MODEL)
    row[13] = HERO_SOUND
    rows.append(row)
    return write_dbc(f, sorted(rows, key=lambda r: r[0]), strings)


def patch_display_info(path):
    f, rows, strings = read_dbc(path)
    assert f == 12, f
    rows = [r for r in rows if r[0] != HERO_DISPLAY]
    row = list(next(r for r in rows if r[0] == STOCK_MODEL_ID))
    row[0] = HERO_DISPLAY
    row[1] = HERO_MODEL_ID
    row[4] = struct.unpack('<I', struct.pack('<f', HERO_SCALE))[0]
    rows.append(row)
    return write_dbc(f, sorted(rows, key=lambda r: r[0]), strings)


def patch_races(path):
    f, rows, strings = read_dbc(path)
    assert f == 29, f
    for r in rows:
        if r[0] == HUMAN:
            r[4] = HERO_DISPLAY
    return write_dbc(f, rows, strings)


def patch_vocal_ui(dbc_dir, mapping):
    f, rows, strings = _load(dbc_dir, 'VocalUISounds')
    assert f == 7, f
    for r in rows:
        if r[2] == HUMAN:
            r[3] = mapping.get(r[3], r[3])            # the male line
    return write_dbc(f, rows, strings)


def patch_emote_sounds(dbc_dir, mapping):
    f, rows, strings = _load(dbc_dir, 'EmotesTextSound')
    assert f == 5, f
    for r in rows:
        if r[2] == HUMAN and r[3] == 0:
            r[4] = mapping.get(r[4], r[4])
    return write_dbc(f, rows, strings)


def patch_sections(dbc_dir):
    f, rows, strings = _load(dbc_dir, 'CharSections')
    assert f == 10, f
    for r in rows:
        if r[1] == HUMAN and r[2] == 0 and r[3] == 1 and r[4] == FACE:
            r[6] = add_string(strings, FACE_FILE % ('Lower', FACE, r[5]))
            r[7] = add_string(strings, FACE_FILE % ('Upper', FACE, r[5]))
        if r[1] == HUMAN and r[2] == 0 and r[3] == 2 and r[4] == CLEAN_FACIAL_STYLE:
            r[6] = add_string(strings, NO_FACIAL_HAIR[0])
            r[7] = add_string(strings, NO_FACIAL_HAIR[1])
    return write_dbc(f, rows, strings)


# ---------------------------------------------------------------- the face and the voice

def young_face(upper, lower):
    """The stock face, younger: smoothed hard (the forehead and cheek creases, the nose's shading
    under the smaller nose), the folds partly filled; the eyes, mouth and ears keep their detail and
    the brows a little of theirs; the original colour mean is restored, so it matches the body."""
    from PIL import Image, ImageFilter, ImageChops, ImageStat, ImageDraw
    face = Image.new('RGB', (128, 96))
    face.paste(upper.convert('RGB'), (0, 0))
    face.paste(lower.convert('RGB'), (0, 32))
    keep = 18                                           # the eye and teeth swatches at the bottom
    work = face.crop((0, 0, 128, 96 - keep))
    smooth = work.filter(ImageFilter.GaussianBlur(3.0))
    base = work.filter(ImageFilter.GaussianBlur(10))
    smooth = Image.blend(smooth, ImageChops.lighter(smooth, base), 0.6)
    mask = Image.new('L', work.size, 0)                 # what keeps the original (white)
    d = ImageDraw.Draw(mask)
    d.ellipse((2, 29, 34, 40), fill=255)                # eye
    d.ellipse((6, 24, 34, 31), fill=90)                 # brow, mostly smoothed
    d.ellipse((-6, 55, 17, 63), fill=200)               # mouth
    d.rectangle((60, 29, 84, 56), fill=255)             # ear
    mask = mask.filter(ImageFilter.GaussianBlur(2.5))
    out = Image.composite(work, Image.blend(work, smooth, 0.9), mask)
    m0, m1 = ImageStat.Stat(work).mean, ImageStat.Stat(out).mean
    out = Image.merge('RGB', [ch.point(lambda v, k=m0[i] / m1[i]: min(255, int(v * k)))
                              for i, ch in enumerate(out.split())])
    feather = Image.new('L', work.size, 255)
    h = work.size[1]
    for y in range(h - 8, h):
        for x in range(128):
            feather.putpixel((x, y), int(255 * (h - 1 - y) / 8))
    face.paste(Image.composite(out, work, feather), (0, 0))
    return face.crop((0, 0, 128, 32)), face.crop((0, 32, 128, 96))


def face_files(face_dir):
    from PIL import Image
    from scarlet_horse import blp_raw1_alpha
    out = {}
    for c in range(10):
        up = Image.open(os.path.join(face_dir, 'HumanMaleFaceUpper%02d_%02d.blp' % (FACE, c)))
        lo = Image.open(os.path.join(face_dir, 'HumanMaleFaceLower%02d_%02d.blp' % (FACE, c)))
        yu, yl = young_face(up, lo)
        out[FACE_FILE % ('Upper', FACE, c)] = blp_raw1_alpha(yu)
        out[FACE_FILE % ('Lower', FACE, c)] = blp_raw1_alpha(yl)
    return out


def voice_files(voice_dir, files, work):
    out = {}
    for src, dst in files:
        path = os.path.join(voice_dir, *src.split('\\'))
        tmp = os.path.join(work, dst.replace('\\', '_'))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-af', VOICE_FILTER,
                        '-ar', '22050', '-ac', '1', '-c:a', 'pcm_s16le', tmp], check=True)
        out[dst] = open(tmp, 'rb').read()
    return out


# ---------------------------------------------------------------- outputs

def build_files(dbc_dir, stock_m2, face_dir, voice_dir, out_dir, ne_m2=None):
    """Every patch-Z file of the hero, and the server's three DBCs written into out_dir; with the
    night elf male's model, the double jump's front flip is ported onto the hero first (port_flip)."""
    os.makedirs(out_dir, exist_ok=True)
    if ne_m2:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
        import port_flip
        flipped = os.path.join(out_dir, 'HumanMale-flip.m2')
        port_flip.port(stock_m2, ne_m2, flipped)
        stock_m2 = flipped
    sounds, mapping, files = sound_entries(dbc_dir)
    model_data = patch_model_data(os.path.join(dbc_dir, 'CreatureModelData.dbc'))
    display = patch_display_info(os.path.join(dbc_dir, 'CreatureDisplayInfo.dbc'))
    races = patch_races(os.path.join(dbc_dir, 'ChrRaces.dbc'))
    patch = {
        HERO_M2: build_model(open(stock_m2, 'rb').read(), mapping),
        'DBFilesClient\\SoundEntries.dbc': sounds,
        'DBFilesClient\\CreatureSoundData.dbc': patch_creature_sound(dbc_dir, mapping),
        'DBFilesClient\\CreatureModelData.dbc': model_data,
        'DBFilesClient\\CreatureDisplayInfo.dbc': display,
        'DBFilesClient\\ChrRaces.dbc': races,
        'DBFilesClient\\VocalUISounds.dbc': patch_vocal_ui(dbc_dir, mapping),
        'DBFilesClient\\EmotesTextSound.dbc': patch_emote_sounds(dbc_dir, mapping),
        'DBFilesClient\\CharSections.dbc': patch_sections(dbc_dir),
    }
    patch.update(face_files(face_dir))
    from PIL import Image
    from scarlet_horse import blp_raw1_alpha
    patch[NO_FACIAL_HAIR[0]] = blp_raw1_alpha(Image.new('RGBA', (128, 64), (0, 0, 0, 0)))
    patch[NO_FACIAL_HAIR[1]] = blp_raw1_alpha(Image.new('RGBA', (128, 32), (0, 0, 0, 0)))
    work = os.path.join(out_dir, 'voice-tmp')
    os.makedirs(work, exist_ok=True)
    patch.update(voice_files(voice_dir, files, work))
    for name, data in (('ChrRaces', races), ('CreatureDisplayInfo', display), ('CreatureModelData', model_data)):
        with open(os.path.join(out_dir, 'server-%s.dbc' % name), 'wb') as fh:
            fh.write(data)
    print('hero: %d patch files, %d voice files, %d sound entries' % (len(patch), len(files), len(mapping)))
    return patch


def write_sql():
    sql = """-- Zelda of Warcraft: the hero's look (build_hero.py). Human male players wear their own display
-- (%(display)d, the young HumanMaleHero model, client patch-Z and the server's DBCs); its model info is
-- the stock human male's. Applied by the server at startup; safe to apply again.
DELETE FROM `creature_model_info` WHERE `modelid` = %(display)d;
INSERT INTO `creature_model_info` (`modelid`, `bounding_radius`, `combat_reach`, `SpeedWalk`, `SpeedRun`, `gender`,
    `modelid_other_gender`)
SELECT %(display)d, `bounding_radius`, `combat_reach`, `SpeedWalk`, `SpeedRun`, `gender`, %(female)d
FROM `creature_model_info` WHERE `modelid` = %(stock)d;
""" % dict(display=HERO_DISPLAY, female=STOCK_FEMALE_DISPLAY, stock=STOCK_MODEL_ID)
    with open(SQL_OUT, 'w', newline='\n') as fh:
        fh.write(sql)
    print('wrote', SQL_OUT)


if __name__ == '__main__':
    write_sql()
    if len(sys.argv) in (6, 7):
        build_files(*sys.argv[1:])
