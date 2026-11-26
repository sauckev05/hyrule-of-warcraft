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
       build_hero.py <client dbc dir> <HumanMale.m2> <face dir> <voice dir> <out dir>
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
# variant C of the voice demo: 26% faster (about +4 semitones), a bigger room
VOICE_FILTER = 'asetrate=22050*1.26,aresample=22050,aecho=0.8:0.6:45|80:0.28|0.16,apad=pad_dur=0.25'
FACE = 0                      # the face the young look is painted on, in every skin colour
FACE_FILE = 'Character\\Human\\Male\\HumanMaleFace%sHero%02d_%02d.blp'
# the cape: every cloak wears the split cape (1504), stretched from the shoulder blades down
SPLIT_CAPE = 1504
CAPE_ANCHOR_Z = 1.40          # model units; the cape keeps its shape above this
CAPE_BOTTOM_Z = 0.40          # the split cape's tails end at mid-calf (stock: 0.73, at the thigh)
CAPE_BACK_SHARE = 0.4         # how much of the extra length also leans back, off the legs
# the galahad character (the core's one-time change): hair style 6 is geoset 7, colour 6 golden blond
SQL_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zelda-sql', '024_hero.sql')


# ---------------------------------------------------------------- the model

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
    pos = deform.deform(m, deform.VARIANTS['B'])
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
    # the animations' sound events ($CSD, the emotes' voices) play the young voice
    n_ev, o_ev = struct.unpack_from('<II', d, 0x114)
    for e in range(n_ev):
        r = o_ev + e * 44
        data = struct.unpack_from('<I', d, r + 4)[0]
        if d[r:r + 4] == b'$CSD' and data in sound_map:
            struct.pack_into('<I', d, r + 4, sound_map[data])
    return bytes(d)


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
    return write_dbc(f, rows, strings)


# ---------------------------------------------------------------- the face and the voice

def young_face(upper, lower):
    """The stock face, younger: the brow and cheek creases softened and the folds partly filled,
    the eyes, brows and skin tone kept (the original colour mean is restored, so it matches the body)."""
    from PIL import Image, ImageFilter, ImageChops, ImageStat
    face = Image.new('RGB', (128, 96))
    face.paste(upper.convert('RGB'), (0, 0))
    face.paste(lower.convert('RGB'), (0, 32))
    keep = 18                                           # the eye and teeth swatches at the bottom
    work = face.crop((0, 0, 128, 96 - keep))
    soft = Image.blend(work, work.filter(ImageFilter.GaussianBlur(1.6)), 0.35)
    base = soft.filter(ImageFilter.GaussianBlur(8))
    lift = Image.blend(soft, ImageChops.lighter(soft, base), 0.40)
    m0, m1 = ImageStat.Stat(work).mean, ImageStat.Stat(lift).mean
    lift = Image.merge('RGB', [ch.point(lambda v, k=m0[i] / m1[i]: min(255, int(v * k)))
                               for i, ch in enumerate(lift.split())])
    mask = Image.new('L', work.size, 255)
    h = work.size[1]
    for y in range(h - 8, h):
        for x in range(128):
            mask.putpixel((x, y), int(255 * (h - 1 - y) / 8))
    face.paste(Image.composite(lift, work, mask), (0, 0))
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

def build_files(dbc_dir, stock_m2, face_dir, voice_dir, out_dir):
    """Every patch-Z file of the hero, and the server's three DBCs written into out_dir."""
    os.makedirs(out_dir, exist_ok=True)
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
    `modelid_other_gender`, `modelid_other_team`)
SELECT %(display)d, `bounding_radius`, `combat_reach`, `SpeedWalk`, `SpeedRun`, `gender`, %(female)d, `modelid_other_team`
FROM `creature_model_info` WHERE `modelid` = %(stock)d;
""" % dict(display=HERO_DISPLAY, female=STOCK_FEMALE_DISPLAY, stock=STOCK_MODEL_ID)
    with open(SQL_OUT, 'w', newline='\n') as fh:
        fh.write(sql)
    print('wrote', SQL_OUT)


if __name__ == '__main__':
    write_sql()
    if len(sys.argv) == 6:
        build_files(*sys.argv[1:])
