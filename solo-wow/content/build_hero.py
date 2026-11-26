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
# the cape: every cloak wears the split cape (1504), stretched from the shoulder blades down
SPLIT_CAPE = 1504
CAPE_ANCHOR_Z = 1.40          # model units; the cape keeps its shape above this
CAPE_BOTTOM_Z = 0.40          # the split cape's tails end at mid-calf (stock: 0.73, at the thigh)
CAPE_BACK_SHARE = 0.4         # how much of the extra length also leans back, off the legs
# the galahad character (the core's one-time change): hair style 6 is geoset 7, colour 6 golden blond
SQL_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zelda-sql', '024_hero.sql')


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
        # the profile at this height: the bridge line above the tip, the underside line below
        if z >= zp:
            prof = xp + (xt - xp) * min(1.0, (z - zp) / (zt - zp))
        else:
            prof = xp + (xb - xp) * min(1.0, (zp - z) / (zp - zb))
        # off the middle the nose falls away (a narrow ridge), then the whole nose sits lower
        x2 = min(x, prof - n['round'] * abs(y))
        x2 = n['plane'] + (x2 - n['plane']) * n['depth']
        v['pos'] = (max(x2, min(x, n['plane'])), y * n['width'], z)


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
    # the split cape, longer: everything below the anchor is stretched down (and a little back)
    cape = set()
    for s in m.subs:
        if s['id'] == SPLIT_CAPE:
            for t in range(s['st'], s['st'] + s['nt']):
                cape.add(m.vlookup[m.tris[t]])
    low = min(pos[v][2] for v in cape)
    k = (CAPE_ANCHOR_Z - CAPE_BOTTOM_Z) / (CAPE_ANCHOR_Z - low)
    anchor_x = sum(pos[v][0] for v in cape if abs(pos[v][2] - CAPE_ANCHOR_Z) < 0.05) / \
        max(1, sum(1 for v in cape if abs(pos[v][2] - CAPE_ANCHOR_Z) < 0.05))
    for v in cape:
        x, y, z = pos[v]
        if z < CAPE_ANCHOR_Z:
            z = CAPE_ANCHOR_Z - (CAPE_ANCHOR_Z - z) * k
            x = anchor_x + (x - anchor_x) * (1 + (k - 1) * CAPE_BACK_SHARE)
            pos[v] = (x, y, z)
    _bulk_armour(m, pos)
    m.write_positions(pos)
    d = m.data
    # every cloak shape draws the split cape: each other cape submesh takes the split cape's ranges
    # (its own id stays, so the cloak's geoset group still picks it), in every level of detail
    for view in _views(d):
        n_sub, o_sub = struct.unpack_from('<II', d, view + 24)
        subs = [(i, struct.unpack_from('<H', d, o_sub + i * 32)[0]) for i in range(n_sub)]
        split = [i for i, sid in subs if sid == SPLIT_CAPE]
        for other in (1502, 1503, 1505, 1506):
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
