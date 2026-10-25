"""Zelda of Warcraft: a warrior's world. Builds zelda-sql/007_warrior_gear.sql, which stops these
items from appearing anywhere in the game (no loot, no vendors, no quest rewards, no trainer
recipes that make them, nothing on the auction house bot); items characters already own stay.

  - raid items: everything that only comes from Molten Core, Onyxia, Blackwing Lair, Zul'Gurub,
    the two Ahn'Qiraj raids or Naxxramas (their bosses, trash, chests, quests, reputations, and
    what is made from their materials). Quel'Serrar and its forging quest are kept (the Sword of
    Mastery is forged from it).
  - cloth (cloaks and shirts kept) and leather armor, mail armor that needs level 40 or more,
    staves, wands, librams, idols and totems, and gear only other classes may use.

The removed entries are also kept in the world table zelda_removed_item (the core's auction house
bot skips them).

usage: build_warrior_gear.py <classic-db world dump (.sql)>
"""

import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

RAID_MAPS = {249, 309, 409, 469, 509, 531, 533}
RAID_AREAS = {1977, 2677, 2717, 2159, 3428, 3429, 3456, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3384, 3397,
              3398, 3419, 3448, 3449, 3450, 3451, 3452, 3453}
# raid bosses that are summoned by scripts instead of spawned (and Prince Thunderaan, Thunderfury's)
SUMMONED_RAID_CREATURES = {14435, 15989, 11502, 11583, 14515, 15114, 15517, 12739, 16194, 16215, 16216, 11663, 11664}
RAID_FACTIONS = {270, 910, 749}         # Zandalar Tribe, Brood of Nozdormu, Hydraxian Waterlords
KEEP_QUEST_REWARDS_OF = {18348}         # Quel'Serrar (and what its forging needs)
CUSTOM_FROM = 190000                    # Zelda's own items and quests are left alone
KEEP_QUESTS = {3962}                    # It's Dangerous to Go Alone (Zelda sets its reward)
WARRIOR = 1

TABLES = ['item_template', 'creature_template', 'creature', 'creature_spawn_entry', 'gameobject',
          'gameobject_spawn_entry', 'gameobject_template', 'quest_template', 'spell_template', 'npc_vendor',
          'npc_vendor_template', 'npc_trainer', 'npc_trainer_template', 'creature_loot_template',
          'reference_loot_template', 'gameobject_loot_template', 'item_loot_template', 'pickpocketing_loot_template',
          'skinning_loot_template', 'fishing_loot_template', 'mail_loot_template', 'spell_loot_template',
          'disenchant_loot_template']
LOOT_TABLES = TABLES[13:]


# ------------------------------------------------------------------ reading the dump
def parse_values(s, i):
    rows = []
    n = len(s)
    while i < n:
        while s[i] in ' ,\n':
            i += 1
        if s[i] == ';':
            return rows, i + 1
        i += 1
        row = []
        while True:
            c = s[i]
            if c == "'":
                j = i + 1
                buf = []
                while True:
                    ch = s[j]
                    if ch == '\\':
                        buf.append({'n': '\n', 'r': '\r', 't': '\t', '0': '\0'}.get(s[j + 1], s[j + 1]))
                        j += 2
                        continue
                    if ch == "'":
                        if s[j + 1] == "'":
                            buf.append("'")
                            j += 2
                            continue
                        break
                    buf.append(ch)
                    j += 1
                row.append(''.join(buf))
                i = j + 1
            else:
                j = i
                while s[j] not in ',)':
                    j += 1
                tok = s[i:j].strip()
                if tok == 'NULL':
                    row.append(None)
                else:
                    try:
                        row.append(int(tok))
                    except ValueError:
                        row.append(float(tok))
                i = j
            if s[i] == ',':
                i += 1
                continue
            if s[i] == ')':
                i += 1
                break
        rows.append(row)
    return rows, i


def load(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    db = {}
    for t in TABLES:
        m = re.search(r'CREATE TABLE `%s` \((.*?)\n\) ENGINE' % t, s, re.S)
        cols = re.findall(r'^\s+`(\w+)`', m.group(1), re.M)
        rows = []
        for im in re.finditer(r'INSERT INTO `%s` (?:\([^)]*\) )?VALUES ' % t, s):
            rows.extend(parse_values(s, im.end())[0])
        db[t] = [dict(zip(cols, r)) for r in rows]
    return db


# ------------------------------------------------------------------ what goes
def compute(db):
    items = {r['entry']: r for r in db['item_template']}
    creatures = {r['Entry']: r for r in db['creature_template']}
    spells = db['spell_template']
    spell_by_id = {sp['Id']: sp for sp in spells}

    def by_entry(rows):
        t = collections.defaultdict(list)
        for r in rows:
            t[r['entry']].append(r)
        return t
    loot = {t: by_entry(db[t]) for t in LOOT_TABLES}

    def expand(rows, seen=None):
        seen = seen if seen is not None else set()
        out = set()
        for r in rows:
            if r['mincountOrRef'] < 0:
                ref = -r['mincountOrRef']
                if ref not in seen:
                    seen.add(ref)
                    out |= expand(loot['reference_loot_template'][ref], seen)
            else:
                out.add(r['item'])
        return out

    def spawn_maps(spawns, extra):
        maps = collections.defaultdict(set)
        guid_map = {}
        for r in spawns:
            maps[r['id']].add(r['map'])
            guid_map[r['guid']] = r['map']
        for r in extra:
            if r['guid'] in guid_map:
                maps[r['entry']].add(guid_map[r['guid']])
        return maps
    creature_maps = spawn_maps(db['creature'], db['creature_spawn_entry'])
    object_maps = spawn_maps(db['gameobject'], db['gameobject_spawn_entry'])

    raid_source, other_source = set(), set()

    def found(its, raid):
        (raid_source if raid else other_source).update(its)

    for entry, c in creatures.items():
        maps = creature_maps.get(entry, set())
        in_raid = bool(maps & RAID_MAPS) or entry in SUMMONED_RAID_CREATURES
        elsewhere = bool(maps - RAID_MAPS) or (not maps and entry not in SUMMONED_RAID_CREATURES)
        for loot_id, table in ((c['LootId'], 'creature_loot_template'), (c['SkinningLootId'], 'skinning_loot_template'),
                               (c['PickpocketLootId'], 'pickpocketing_loot_template')):
            if loot_id and loot_id in loot[table]:
                its = expand(loot[table][loot_id])
                if in_raid:
                    found(its, True)
                if elsewhere:
                    found(its, False)
    for g in db['gameobject_template']:
        if g['type'] in (3, 25) and g['data1'] in loot['gameobject_loot_template']:
            maps = object_maps.get(g['entry'], set())
            its = expand(loot['gameobject_loot_template'][g['data1']])
            if maps & RAID_MAPS:
                found(its, True)
            if (maps - RAID_MAPS) or not maps:
                found(its, False)
    for table in ('fishing_loot_template', 'mail_loot_template', 'spell_loot_template', 'disenchant_loot_template'):
        for rows in loot[table].values():
            found(expand(rows), False)
    for table in ('npc_vendor', 'npc_vendor_template'):
        other_source.update(r['item'] for r in db[table])

    quests = db['quest_template']

    def rewards(q):
        return ([q['RewChoiceItemId%d' % i] for i in range(1, 7) if q['RewChoiceItemId%d' % i]] +
                [q['RewItemId%d' % i] for i in range(1, 5) if q['RewItemId%d' % i]])

    def needs(q):
        return ([q['ReqItemId%d' % i] for i in range(1, 5) if q['ReqItemId%d' % i]] +
                ([q['SrcItemId']] if q['SrcItemId'] else []))

    keep = set(KEEP_QUEST_REWARDS_OF)
    grew = True
    while grew:
        grew = False
        for q in quests:
            if set(rewards(q)) & keep:
                for i in needs(q):
                    if i not in keep:
                        keep.add(i)
                        grew = True

    raid = {i for i in raid_source if i not in other_source}
    raid |= {e for e, it in items.items() if it['RequiredReputationFaction'] in RAID_FACTIONS}
    raid_quests = set()
    for _ in range(30):
        before = len(raid)
        for entry, rows in loot['item_loot_template'].items():
            if entry in raid:
                raid |= expand(rows)
        for q in quests:
            req = set(needs(q))
            if q['ZoneOrSort'] in RAID_AREAS or (req & raid and not req & keep):
                raid_quests.add(q['entry'])
        for q in quests:
            if abs(q['PrevQuestId']) in raid_quests:
                raid_quests.add(q['entry'])
        for sp in spells:
            made = [sp['EffectItemType%d' % k] for k in (1, 2, 3) if sp['Effect%d' % k] == 24 and sp['EffectItemType%d' % k]]
            reagents = {sp['Reagent%d' % k] for k in range(1, 9) if sp['Reagent%d' % k]}
            if made and reagents & raid and not reagents & keep:
                raid.update(m for m in made if m not in keep)
        from_raid_quests, from_other_quests = set(), set()
        for q in quests:
            (from_raid_quests if q['entry'] in raid_quests else from_other_quests).update(rewards(q))
        raid |= {i for i in from_raid_quests if i not in other_source and i not in from_other_quests}
        if len(raid) == before:
            break
    raid = {i for i in raid - keep if i < CUSTOM_FROM}

    gear = set()
    for e, it in items.items():
        if e >= CUSTOM_FROM or e in keep:
            continue
        cls, sub, inv = it['class'], it['subclass'], it['InventoryType']
        if cls == 4 and sub == 1 and inv not in (0, 4, 16):            # cloth (shirts and cloaks stay)
            gear.add(e)
        elif cls == 4 and sub == 2 and inv != 0:                        # leather
            gear.add(e)
        elif cls == 4 and sub == 3 and inv != 0 and it['RequiredLevel'] >= 40:   # mail from level 40
            gear.add(e)
        elif cls == 4 and sub in (7, 8, 9):                             # librams, idols, totems
            gear.add(e)
        elif cls == 2 and sub in (10, 19):                              # staves, wands
            gear.add(e)
        elif cls in (2, 4) and inv != 0 and it['AllowableClass'] > 0 and not it['AllowableClass'] & WARRIOR:
            gear.add(e)
    removed = raid | gear

    # crafting: recipes that only make removed items, the trainers' lessons and the recipe items
    def teaches(spell):
        sp = spell_by_id.get(spell)
        if not sp:
            return set()
        return {sp['EffectTriggerSpell%d' % k] for k in (1, 2, 3) if sp['Effect%d' % k] == 36} | {spell}
    recipes = set()
    for sp in spells:
        made = [sp['EffectItemType%d' % k] for k in (1, 2, 3) if sp['Effect%d' % k] == 24 and sp['EffectItemType%d' % k]]
        if made and sp['Attributes'] & 32 and all(m in removed for m in made):
            recipes.add(sp['Id'])
    lessons = set()
    for table in ('npc_trainer', 'npc_trainer_template'):
        lessons |= {r['spell'] for r in db[table] if teaches(r['spell']) & recipes}
    recipe_items = set()
    for e, it in items.items():
        if it['class'] == 9 and e < CUSTOM_FROM:
            taught = set()
            for n in range(1, 6):
                if it['spellid_%d' % n]:
                    taught |= teaches(it['spellid_%d' % n])
            if taught & recipes:
                recipe_items.add(e)
    removed |= recipe_items

    # quest rewards: what is left of each quest's rewards, in order
    quest_rewards = {}
    for q in quests:
        if q['entry'] >= CUSTOM_FROM or q['entry'] in KEEP_QUESTS:
            continue
        choice = [(q['RewChoiceItemId%d' % i], q['RewChoiceItemCount%d' % i]) for i in range(1, 7) if q['RewChoiceItemId%d' % i]]
        fixed = [(q['RewItemId%d' % i], q['RewItemCount%d' % i]) for i in range(1, 5) if q['RewItemId%d' % i]]
        if any(i in removed for i, _ in choice + fixed):
            quest_rewards[q['entry']] = ([c for c in choice if c[0] not in removed], [f for f in fixed if f[0] not in removed])

    print('raid items', len(raid), '- gear', len(gear), '- recipe items', len(recipe_items), '- total', len(removed))
    print('recipes', len(recipes), '- trainer lessons', len(lessons), '- quests with rewards removed', len(quest_rewards))
    return sorted(removed), sorted(lessons), quest_rewards


# ------------------------------------------------------------------ the SQL
def chunks(values, size=400):
    values = list(values)
    for i in range(0, len(values), size):
        yield ','.join(str(v) for v in values[i:i + size])


PVP_RANK_GEAR = '-- the PvP rank rewards from Knight-Lieutenant / Blood Guard (rank 7) up: armor and weapons are gone\nINSERT IGNORE INTO `zelda_removed_item` (`entry`) SELECT `entry` FROM `item_template` WHERE `requiredhonorrank` >= 11 AND `class` IN (2, 4);\n'


def write_sql(removed, lessons, quest_rewards):
    out = ['-- Zelda of Warcraft: a warrior\'s world (generated by build_warrior_gear.py)\n',
           'CREATE TABLE IF NOT EXISTS `zelda_removed_item` (`entry` int unsigned NOT NULL PRIMARY KEY) ENGINE=MyISAM '
           'DEFAULT CHARSET=utf8 COMMENT=\'Zelda of Warcraft: items that no longer appear in the game\';\n',
           'DELETE FROM `zelda_removed_item`;\n']
    for part in chunks(removed):
        out.append('INSERT INTO `zelda_removed_item` (`entry`) VALUES (%s);\n' % part.replace(',', '),('))
    out.append(PVP_RANK_GEAR)
    for table in LOOT_TABLES:
        out.append('DELETE FROM `%s` WHERE `mincountOrRef` >= 0 AND `item` IN (SELECT `entry` FROM `zelda_removed_item`);\n' % table)
    for table in ('npc_vendor', 'npc_vendor_template'):
        out.append('DELETE FROM `%s` WHERE `item` IN (SELECT `entry` FROM `zelda_removed_item`);\n' % table)
    for table in ('npc_trainer', 'npc_trainer_template'):
        for part in chunks(lessons):
            out.append('DELETE FROM `%s` WHERE `spell` IN (%s);\n' % (table, part))
    for entry, (choice, fixed) in sorted(quest_rewards.items()):
        sets = []
        for i in range(6):
            item, count = choice[i] if i < len(choice) else (0, 0)
            sets.append('`RewChoiceItemId%d` = %d, `RewChoiceItemCount%d` = %d' % (i + 1, item, i + 1, count))
        for i in range(4):
            item, count = fixed[i] if i < len(fixed) else (0, 0)
            sets.append('`RewItemId%d` = %d, `RewItemCount%d` = %d' % (i + 1, item, i + 1, count))
        out.append('UPDATE `quest_template` SET %s WHERE `entry` = %d;\n' % (', '.join(sets), entry))
    path = os.path.join(HERE, 'zelda-sql', '007_warrior_gear.sql')
    with open(path, 'w', newline='\n') as f:
        f.write(''.join(out))
    print('wrote', path, sum(len(x) for x in out), 'bytes')


if __name__ == '__main__':
    write_sql(*compute(load(sys.argv[1])))
