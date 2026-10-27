"""Zelda of Warcraft: dungeons moved to a new level range. For each dungeon in DUNGEONS it builds one
zelda-sql file:

  - every enemy in the dungeon (and the ones its events summon) moves to the new levels, the bosses
    each to its own. Health, damage and armor follow the level (creature_template multipliers on
    the class level stats), and so does the money they carry.
  - their random drops (the green, blue, white and grey world-drop tables) are swapped for the
    tables of the same kind that creatures of the new level use.
  - the boss drops that only come from this dungeon go up by as many levels as their boss: item
    level, required level, stats, resistances, armor, block, weapon damage and price.

Set pieces (sets.py) and items taken out of the game (007_warrior_gear.sql) are left alone; so are
creatures that also live outside the dungeon (snakes, toads).

  - Blackfathom Deeps (009_blackfathom.sql): level 30-35, Aku'mai 35
  - Wailing Caverns (011_wailing_caverns.sql): level 28-33, Mutanus the Devourer 33
  - Scarlet Monastery (018_scarlet_monastery.sql): level 40-45 - Graveyard, Library, Armory, then
    the Cathedral, whose Mograine and Whitemane are 45

usage: build_dungeons.py <world database dump (.sql) without these files applied>
"""

import collections
import os
import re
import sys

from build_warrior_gear import parse_values
from sets import SETS

HERE = os.path.dirname(os.path.abspath(__file__))
CUSTOM_FROM = 190000

# trash: new level = round(new_lo + (old - old_lo) * slope), kept within [floor, cap]
DUNGEONS = [
    dict(name='Blackfathom Deeps', file='009_blackfathom.sql', range='30-35', map=48,
         not_enemies={4787},                    # Argent Guard Thaelrid (quest giver)
         summoned={12876, 4977, 4978},          # Baron Aquanis, Murkshallow Softshell, Aku'mai Servant
         bosses={4887: 31, 4831: 32, 6243: 32, 12902: 33, 12876: 33, 4832: 34, 4830: 34, 4829: 35},
         trash=(22, 30, 5 / 6, 30, 34), max_req=35),
    dict(name='Wailing Caverns', file='011_wailing_caverns.sql', range='28-33', map=43,
         not_enemies={3678, 3679, 5914},        # Disciple of Naralex, Naralex, Deviate Nightmare (friendly)
         # Lady Anacondra and Mutanus come from scripts; the Moccasins and Ectoplasms from the ritual
         summoned={3671, 3654, 5762, 5763},
         bosses={3671: 30, 3669: 30, 3653: 30, 3670: 31, 3674: 31, 5912: 31, 3673: 32, 5775: 32, 3654: 33},
         trash=(17, 28, 3 / 4, 28, 31), max_req=33),
    # the four wings rise through 40-45 in their own order: Graveyard 40-42, Library 41-43, Armory
    # 42-44, Cathedral 43-45 (the old levels already climbed wing by wing, so one slope keeps that)
    dict(name='Scarlet Monastery', file='018_scarlet_monastery.sql', range='40-45', map=189,
         not_enemies={3981, 6547},              # Vorrel Sengutz (quest giver), Suffering Victim (prisoners)
         summoned={6575},                       # Scarlet Trainees, called by Herod's fall
         also_outside={4283},                   # Scarlet Sentry: also guards the monastery's courtyard
         bosses={3983: 41, 6488: 42, 6489: 42, 6490: 42, 4543: 42, 3974: 42, 6487: 43, 6575: 43,
                 3975: 44, 4542: 44, 3976: 45, 3977: 45},
         trash=(30, 40, 1 / 2, 40, 44), max_req=45),
]
WORLD_DROP_REFS = range(60000, 61000)   # level-bracket world drop tables (series = id // 100)

TABLES = ['creature_template', 'creature', 'creature_spawn_entry', 'creature_loot_template',
          'reference_loot_template', 'gameobject_loot_template', 'item_loot_template', 'npc_vendor',
          'npc_vendor_template', 'quest_template', 'item_template']


def load(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    db = {}
    for t in TABLES:
        m = re.search(r'CREATE TABLE `%s` \((.*?)\n\) ENGINE' % t, s, re.S)
        cols = re.findall(r'^\s+`(\w+)`', m.group(1), re.M)
        rows = []
        for im in re.finditer(r'INSERT INTO `%s` (?:\([^)]*\) )?VALUES\s*' % t, s):
            rows.extend(parse_values(s, im.end())[0])
        db[t] = [dict(zip(cols, r)) for r in rows]
    return db


def removed_items():
    text = open(os.path.join(HERE, 'zelda-sql', '007_warrior_gear.sql')).read()
    m = re.search(r'INSERT INTO `zelda_removed_item` \(`entry`\) VALUES (.*?);', text, re.S)
    return {int(x) for x in re.findall(r'\((\d+)\)', m.group(1))}


def new_level(d, entry, old):
    if entry in d['bosses']:
        return d['bosses'][entry]
    old_lo, new_lo, slope, floor, cap = d['trash']
    return max(floor, min(cap, int(new_lo + (old - old_lo) * slope + 0.5)))


def compute(db, d):
    MAP = d['map']
    templates = {r['Entry']: r for r in db['creature_template']}
    spawned = {r['id'] for r in db['creature'] if r['map'] == MAP and r['id']}
    random_guids = {r['guid'] for r in db['creature'] if r['map'] == MAP and not r['id']}
    spawned |= {r['entry'] for r in db['creature_spawn_entry'] if r['guid'] in random_guids}
    elsewhere_spawn = {r['id'] for r in db['creature'] if r['map'] != MAP and r['id']}
    enemies = sorted(e for e in (spawned | d['summoned']) if e < CUSTOM_FROM and e not in d['not_enemies']
                     and (e not in elsewhere_spawn or e in d.get('also_outside', ())))

    creatures = {}
    for e in enemies:
        t = templates[e]
        lo, hi = new_level(d, e, t['MinLevel']), new_level(d, e, t['MaxLevel'])
        old_avg = (t['MinLevel'] + t['MaxLevel']) / 2
        money = (((lo + hi) / 2) / old_avg) ** 2
        creatures[e] = dict(name=t['Name'], old=(t['MinLevel'], t['MaxLevel']), new=(lo, hi),
                            shift=(lo + hi) / 2 - old_avg, loot=t['LootId'],
                            gold=(int(round(t['MinLootGold'] * money)), int(round(t['MaxLootGold'] * money))))

    # world drop tables: the average level of the creatures that use each one
    level_of = collections.defaultdict(list)
    loot_owner = collections.defaultdict(list)
    for t in db['creature_template']:
        if t['LootId']:
            loot_owner[t['LootId']].append(t)
    for r in db['creature_loot_template']:
        ref = -r['mincountOrRef']
        if ref in WORLD_DROP_REFS:
            for t in loot_owner[r['entry']]:
                level_of[ref].append((t['MinLevel'] + t['MaxLevel']) / 2)
    ref_level = {ref: sum(v) / len(v) for ref, v in level_of.items() if len(v) >= 5}

    def better_ref(ref, shift):
        if ref not in ref_level:
            return ref
        want = ref_level[ref] + shift
        same = [r for r in ref_level if r // 100 == ref // 100]
        return min(same, key=lambda r: (abs(ref_level[r] - want), r))

    bfd_loot = {c['loot']: e for e, c in creatures.items() if c['loot']}
    ref_rows, drops = [], collections.defaultdict(list)
    for r in db['creature_loot_template']:
        owner = bfd_loot.get(r['entry'])
        if owner is None:
            continue
        if r['mincountOrRef'] < 0 and -r['mincountOrRef'] in WORLD_DROP_REFS:
            new = better_ref(-r['mincountOrRef'], creatures[owner]['shift'])
            ref_rows.append(dict(r, item=new, mincountOrRef=-new))
        elif r['mincountOrRef'] > 0:
            drops[r['item']].append(owner)
    # two old tables may land on the same new one: keep the better chance
    merged = {}
    for r in ref_rows:
        key = (r['entry'], r['item'])
        if key not in merged or r['ChanceOrQuestChance'] > merged[key]['ChanceOrQuestChance']:
            merged[key] = r
    ref_rows = sorted(merged.values(), key=lambda r: (r['entry'], r['item']))

    # boss drops found nowhere else
    elsewhere = collections.Counter()
    for r in db['creature_loot_template']:
        if r['mincountOrRef'] > 0 and r['entry'] not in bfd_loot:
            elsewhere[r['item']] += 1
    for t in ('reference_loot_template', 'gameobject_loot_template', 'item_loot_template'):
        for r in db[t]:
            elsewhere[r['item']] += 1
    for t in ('npc_vendor', 'npc_vendor_template'):
        for r in db[t]:
            elsewhere[r['item']] += 1
    for q in db['quest_template']:
        for k in ['RewChoiceItemId%d' % i for i in range(1, 7)] + ['RewItemId%d' % i for i in range(1, 5)]:
            if q[k]:
                elsewhere[q[k]] += 1
    removed = removed_items() | {p[0] for s in SETS for p in s['pieces']}     # set pieces keep sets.py's stats
    items = {r['entry']: r for r in db['item_template']}
    scaled = []
    for entry, owners in sorted(drops.items()):
        it = items.get(entry)
        if (not it or entry >= CUSTOM_FROM or entry in removed or elsewhere[entry] or it['Quality'] < 2
                or it['class'] not in (2, 4)):
            continue
        shift = int(round(max(creatures[o]['shift'] for o in owners)))
        # no drop asks for more than the dungeon's top level
        if it['RequiredLevel']:
            shift = min(shift, d['max_req'] - it['RequiredLevel'])
        if shift <= 0:
            continue
        scaled.append(scale_item(it, shift, [creatures[o]['name'] for o in owners]))
    return creatures, ref_rows, scaled


def scale_item(it, shift, bosses):
    ilvl = it['ItemLevel'] + shift
    ratio = ilvl / it['ItemLevel']
    out = {'entry': it['entry'], 'name': it['name'], 'bosses': bosses, 'ItemLevel': ilvl,
           'RequiredLevel': it['RequiredLevel'] + shift if it['RequiredLevel'] else 0}

    def up(v):
        return int(round(v * ratio)) if v > 0 else v
    for i in range(1, 11):
        if it['stat_type%d' % i]:
            out['stat_value%d' % i] = up(it['stat_value%d' % i])
    for k in ('armor', 'block', 'holy_res', 'fire_res', 'nature_res', 'frost_res', 'shadow_res', 'arcane_res'):
        if it[k]:
            out[k] = up(it[k])
    for i in range(1, 6):
        if it['dmg_max%d' % i]:
            out['dmg_min%d' % i] = round(it['dmg_min%d' % i] * ratio, 1)
            out['dmg_max%d' % i] = round(it['dmg_max%d' % i] * ratio, 1)
    out['SellPrice'] = int(round(it['SellPrice'] * ratio * ratio))
    out['BuyPrice'] = int(round(it['BuyPrice'] * ratio * ratio))
    out['_old'] = it
    return out


def write_sql(d, creatures, ref_rows, scaled):
    out = ['-- Zelda of Warcraft: %s as a level %s dungeon (generated by build_dungeons.py)\n' % (d['name'], d['range']),
           '-- Applied by the server at startup; every value is absolute, so it is safe to apply again.\n\n']
    for e, c in sorted(creatures.items()):
        out.append("UPDATE `creature_template` SET `MinLevel` = %d, `MaxLevel` = %d, `MinLootGold` = %d, `MaxLootGold` = %d "
                   "WHERE `Entry` = %d; -- %s (was %d-%d)\n" % (c['new'] + c['gold'] + (e, c['name']) + c['old']))
    loot_ids = sorted({c['loot'] for c in creatures.values() if c['loot']})
    out.append('\nDELETE FROM `creature_loot_template` WHERE `entry` IN (%s) AND `mincountOrRef` < 0 AND `item` BETWEEN %d AND %d;\n'
               % (','.join(map(str, loot_ids)), WORLD_DROP_REFS.start, WORLD_DROP_REFS.stop - 1))
    out.append('INSERT INTO `creature_loot_template` (`entry`,`item`,`ChanceOrQuestChance`,`groupid`,`mincountOrRef`,`maxcount`,`condition_id`,`comments`) VALUES\n')
    out.append(',\n'.join("(%d,%d,%s,%d,%d,%d,%d,'%s')" % (r['entry'], r['item'], repr(float(r['ChanceOrQuestChance'])), r['groupid'],
                                                       r['mincountOrRef'], r['maxcount'], r['condition_id'],
                                                       'Zelda: %s level %s world drops' % (d['name'], d['range']))
                          for r in ref_rows) + ';\n\n')
    for it in scaled:
        sets = ', '.join('`%s` = %s' % (k, v) for k, v in it.items() if k not in ('entry', 'name', 'bosses', '_old'))
        out.append('UPDATE `item_template` SET %s WHERE `entry` = %d; -- %s (%s)\n'
                   % (sets, it['entry'], it['name'], ', '.join(it['bosses'])))
    path = os.path.join(HERE, 'zelda-sql', d['file'])
    with open(path, 'w', newline='\n') as f:
        f.write(''.join(out))
    print('wrote', path)
    for e, c in sorted(creatures.items(), key=lambda kv: kv[1]['new']):
        print('  %-28s %2d-%-2d -> %2d-%-2d' % ((c['name'],) + c['old'] + c['new']))
    for it in scaled:
        o = it['_old']
        print('  %-26s ilvl %d -> %d  req %d -> %d' % (it['name'], o['ItemLevel'], it['ItemLevel'], o['RequiredLevel'], it['RequiredLevel']))


if __name__ == '__main__':
    world = load(sys.argv[1])
    for dungeon in DUNGEONS:
        write_sql(dungeon, *compute(world, dungeon))
