#!/usr/bin/env python3
"""The sounds a mount makes when it is spurred (ZeldaSpur), by mount display.

Each spur (each red circle) plays the next of the mount's attack sounds, one file at a time in turn,
round and round (zelda_mount_attack: every file of its attack SoundEntries - exertion, critical and
custom attacks - each made its own single-file SoundEntries row, MOUNT_ATTACK_BASE up, which
build_hero.py adds to patch-Z from mount_attack_sounds.json). Mounts whose model has no attack
sound take their kind's (KIND_ATTACKS).

The idle call (zelda_mount_sound) is kept as the fallback for a mount with no attack sounds:

Each mount model gets its kind's idle sound (a horse's snort-and-whinny HorseStand3, a wolf's
WolfFidget2, ...). Kinds not named below fall back to the model's own CreatureSoundData (fidget,
alert, then aggro). Every CreatureDisplayInfo row on a mount model is listed, custom looks such as
the Scarlet Warhorse included. Run locally with the client's DBCs and the classic world dump (for the
mount creatures' displays); it writes zelda-sql/025_mount_sounds.sql.

usage: build_mount_sounds.py <client dbc dir> <Spell.dbc> <ClassicDB .sql.gz>
       build_mount_sounds.py <client dbc dir> <mount displays .json>
"""
import json
import gzip
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_mastery import read_dbc, DBC_FIELD      # noqa: E402

AURA_MOUNTED = 78
SQL_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zelda-sql', '025_mount_sounds.sql')
ATTACK_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mount_attack_sounds.json')
MOUNT_ATTACK_BASE = 20200      # the single-file attack SoundEntries rows (patch-Z, build_hero.py)
# model path keyword (lower case) -> attack SoundEntries ids, for models with none of their own
KIND_ATTACKS = [
    ('ram', [3425]),              # RamAttack
    ('kodo', [772]),              # KodoBeastAttack
    ('silithid', [715]),          # SilithidWaspAttack (the Qiraji battle tanks)
    ('kathune', [715]),
    ('reindeer', [2651]),         # GiraffeAttack, as the stag has
    ('turtle', [1459]),           # SeaTurtleAttack
]
# CreatureSoundData: exertion, exertion critical, the four custom attacks
CSD_ATTACK_FIELDS = (1, 2, 19, 20, 21, 22)
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


def build(dbc_dir, spell_dbc, world_dump=None):
    _, displays, _ = read_dbc(os.path.join(dbc_dir, 'CreatureDisplayInfo.dbc'))
    _, models, model_strings = read_dbc(os.path.join(dbc_dir, 'CreatureModelData.dbc'))
    _, voices, _ = read_dbc(os.path.join(dbc_dir, 'CreatureSoundData.dbc'))
    by_display = {r[0]: r for r in displays}
    by_model = {r[0]: r for r in models}
    by_voice = {r[0]: r for r in voices}
    if world_dump is None:                         # the mount displays, listed before
        mounts = json.load(open(spell_dbc))
    else:
        mounts = mount_displays(spell_dbc, world_dump)
    mount_models = {by_display[d][1] for d in mounts if d in by_display}
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
    # the attack sounds, file by file
    _, entries, entry_strings = read_dbc(os.path.join(dbc_dir, 'SoundEntries.dbc'))
    by_entry = {r[0]: r for r in entries}
    singles = {}                                   # (entry, file) -> new id
    attacks_of_model = {}
    for mid in sorted(mount_models):
        path = _str(model_strings, by_model[mid][2]).lower()
        voice = by_voice.get(by_model[mid][13])
        ids = [voice[i] for i in CSD_ATTACK_FIELDS if voice and voice[i]] if voice else []
        if not ids:
            ids = next((k for kw, k in KIND_ATTACKS if kw in path), [])
        seq = []
        for e in dict.fromkeys(ids):
            row = by_entry.get(e)
            if not row:
                continue
            for slot in range(10):
                if row[3 + slot]:
                    key = (e, slot)
                    if key not in singles:
                        singles[key] = MOUNT_ATTACK_BASE + len(singles)
                    if singles[key] not in seq:
                        seq.append(singles[key])
        if seq:
            attacks_of_model[mid] = seq
    attack_rows = [(r[0], k, sid) for r in sorted(displays) if r[1] in attacks_of_model
                   for k, sid in enumerate(attacks_of_model[r[1]])]
    with open(ATTACK_JSON, 'w', newline='\n') as fh:
        json.dump({'comment': 'single-file attack SoundEntries rows for the mounts (build_mount_sounds.py): '
                              '[new id, stock SoundEntries id, file slot, file]',
                   'entries': [[nid, e, slot, _str(entry_strings, by_entry[e][3 + slot])]
                               for (e, slot), nid in sorted(singles.items(), key=lambda kv: kv[1])]},
                  fh, indent=1)
    lines = ["-- Zelda of Warcraft: the call a mount makes when it is spurred (ZeldaSpur), by mount display",
             "-- (build_mount_sounds.py, from the client's DBCs). Applied by the server at startup; safe to apply again.",
             "CREATE TABLE IF NOT EXISTS `zelda_mount_sound` (",
             "  `display_id` int unsigned NOT NULL,",
             "  `sound_id` int unsigned NOT NULL,",
             "  PRIMARY KEY (`display_id`)",
             ") ENGINE=MyISAM DEFAULT CHARSET=utf8;",
             "DELETE FROM `zelda_mount_sound`;",
             "INSERT INTO `zelda_mount_sound` (`display_id`, `sound_id`) VALUES"]
    lines.append(',\n'.join("(%d, %d)" % (d, s) for d, s, _ in rows) + ';')
    lines += ["-- each spur plays the next of the mount's attack sounds (one file each, patch-Z's rows from",
              "-- mount_attack_sounds.json), in turn by the red circle it adds",
              "CREATE TABLE IF NOT EXISTS `zelda_mount_attack` (",
              "  `display_id` int unsigned NOT NULL,",
              "  `seq` int unsigned NOT NULL,",
              "  `sound_id` int unsigned NOT NULL,",
              "  PRIMARY KEY (`display_id`, `seq`)",
              ") ENGINE=MyISAM DEFAULT CHARSET=utf8;",
              "DELETE FROM `zelda_mount_attack`;",
              "INSERT INTO `zelda_mount_attack` (`display_id`, `seq`, `sound_id`) VALUES"]
    lines.append(',\n'.join("(%d, %d, %d)" % r for r in attack_rows) + ';')
    with open(SQL_OUT, 'w', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('wrote', SQL_OUT, len(rows), 'displays on', len(sound_of_model), 'mount models;',
          len(attack_rows), 'attack rows,', len(singles), 'attack sounds on', len(attacks_of_model), 'models')
    for mid, (s, p) in sorted(sound_of_model.items()):
        print(' ', mid, p, s)


if __name__ == '__main__':
    build(*sys.argv[1:4])
