#!/usr/bin/env python3
"""The sound a mount makes when it is spurred (ZeldaSpur): its idle call, by mount display.

Each mount model gets its kind's idle sound (a horse's snort-and-whinny HorseStand3, a wolf's
WolfFidget2, ...). Kinds not named below fall back to the model's own CreatureSoundData (fidget,
alert, then aggro). Every CreatureDisplayInfo row on a mount model is listed, custom looks such as
the Scarlet Warhorse included. Run locally with the client's DBCs and the classic world dump (for the
mount creatures' displays); it writes zelda-sql/025_mount_sounds.sql.

usage: build_mount_sounds.py <client dbc dir> <Spell.dbc> <ClassicDB .sql.gz>
"""
import gzip
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_mastery import read_dbc, DBC_FIELD      # noqa: E402

AURA_MOUNTED = 78
SQL_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zelda-sql', '025_mount_sounds.sql')
# model path keyword (lower case) -> SoundEntries id; the first match wins
KIND_SOUNDS = [
    ('undeadhorse', 3610),        # UndeadHorsePreAggro (HorseUndeadStand2A)
    ('mounteddeathknight', 3610),
    ('nightmare', 730),           # HorseStand3
    ('horse', 730),
    ('direwolf', 1018),           # WolfFidget2
    ('frostsabre', 648),          # TigerStand2
    ('tiger', 648),
    ('kodo', 776),                # KodoBeastStand2
    ('raptor', 708),              # RaptorAggro
    ('ram\\', 3429),              # RamPreAggro
    ('mechastrider', 4418),       # MechaStriderPreAggro
    ('tallstrider', 1480),        # TallStriderPreAggro
]


def _str(strings, off):
    return strings[off:strings.index(b'\0', off)].decode('latin1') if off else ''


def _sql_rows(txt, table):
    """The rows of `table`'s INSERTs in a mysqldump, as lists of field strings."""
    out = []
    for m in re.finditer(r"INSERT INTO `%s` VALUES " % table, txt):
        i, n = m.end(), len(txt)
        while i < n and txt[i] != ';':
            if txt[i] != '(':
                i += 1
                continue
            i += 1
            row, cur, quoted = [], '', False
            while True:
                c = txt[i]
                if quoted:
                    if c == '\\':
                        cur += txt[i + 1]
                        i += 2
                        continue
                    if c == "'":
                        quoted = False
                    else:
                        cur += c
                    i += 1
                    continue
                i += 1
                if c == "'":
                    quoted = True
                elif c == ',':
                    row.append(cur)
                    cur = ''
                elif c == ')':
                    row.append(cur)
                    break
                else:
                    cur += c
            out.append(row)
    return out


def mount_displays(spell_dbc, world_dump):
    f, spells, _ = read_dbc(spell_dbc)
    aura, misc = DBC_FIELD['EffectApplyAuraName1'], DBC_FIELD['EffectMiscValue1']
    creatures = {r[misc + i] for r in spells for i in range(3) if r[aura + i] == AURA_MOUNTED and r[misc + i]}
    txt = gzip.open(world_dump, 'rt', errors='replace').read()
    m = re.search(r"CREATE TABLE `creature_template` \((.*?)\) ENGINE", txt, re.S)
    cols = [c.split('`')[1] for c in m.group(1).split('\n') if c.strip().startswith('`')]
    entry, models = cols.index('Entry'), [cols.index('ModelId%d' % k) for k in (1, 2, 3, 4)]
    out = set()
    for row in _sql_rows(txt, 'creature_template'):
        if int(row[entry]) in creatures:
            out.update(int(row[c]) for c in models if int(row[c]))
    return out


def build(dbc_dir, spell_dbc, world_dump):
    _, displays, _ = read_dbc(os.path.join(dbc_dir, 'CreatureDisplayInfo.dbc'))
    _, models, model_strings = read_dbc(os.path.join(dbc_dir, 'CreatureModelData.dbc'))
    _, voices, _ = read_dbc(os.path.join(dbc_dir, 'CreatureSoundData.dbc'))
    by_display = {r[0]: r for r in displays}
    by_model = {r[0]: r for r in models}
    by_voice = {r[0]: r for r in voices}
    mount_models = {by_display[d][1] for d in mount_displays(spell_dbc, world_dump) if d in by_display}
    sound_of_model = {}
    for mid in mount_models:
        path = _str(model_strings, by_model[mid][2]).lower()
        sound = next((s for k, s in KIND_SOUNDS if k in path), 0)
        if not sound:
            voice = by_voice.get(by_model[mid][13])
            if voice:
                sound = next((voice[i] for i in (14, 13, 10) if voice[i]), 0)
        if sound:
            sound_of_model[mid] = (sound, path)
    rows = sorted((r[0], sound_of_model[r[1]][0], sound_of_model[r[1]][1]) for r in displays if r[1] in sound_of_model)
    lines = ["-- Zelda of Warcraft: the call a mount makes when it is spurred (ZeldaSpur), by mount display",
             "-- (build_mount_sounds.py, from the client's DBCs). Applied by the server at startup; safe to apply again.",
             "CREATE TABLE IF NOT EXISTS `zelda_mount_sound` (",
             "  `display_id` int unsigned NOT NULL,",
             "  `sound_id` int unsigned NOT NULL,",
             "  PRIMARY KEY (`display_id`)",
             ") ENGINE=MyISAM DEFAULT CHARSET=utf8mb3;",
             "DELETE FROM `zelda_mount_sound`;",
             "INSERT INTO `zelda_mount_sound` (`display_id`, `sound_id`) VALUES"]
    lines.append(',\n'.join("(%d, %d)" % (d, s) for d, s, _ in rows) + ';')
    with open(SQL_OUT, 'w', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('wrote', SQL_OUT, len(rows), 'displays on', len(sound_of_model), 'mount models')
    for mid, (s, p) in sorted(sound_of_model.items()):
        print(' ', mid, p, s)


if __name__ == '__main__':
    build(*sys.argv[1:4])
