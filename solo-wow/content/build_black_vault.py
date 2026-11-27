#!/usr/bin/env python3
"""Zelda of Warcraft - the Black Vault of Blackrock Depths, worth opening.

Writes zelda-sql/026_black_vault.sql, which the server applies to the world database at startup, and
(given the stock textures and SpellItemEnchantment.dbc) adds the client's side to patch-Z.MPQ.

  - The twelve Relic Coffers behind the Relic Coffer Doors (still opened with Relic Coffer Keys) can be
    opened: the stock chests carry GO_FLAG_NO_INTERACT, which nothing ever cleared. Each holds a libram
    besides its trinkets. Down each side of the vault, from the way in towards the Dark Coffer: Libram of
    Constitution, Resilience, Rumination, Tenacity and Voracity; the sixth on each side, beside the Dark
    Coffer, holds one of the two new librams (the Libram of Ferocity on the left, the Libram of the
    Bulwark on the right).
  - The Dark Coffer (behind the Secret Safe's door) can be opened too, with the Dark Keeper Key (the core:
    ZeldaDoorKeyHeld). The key drops from Watchman Doomgrip, always, and from no Dark Keeper any more. The
    coffer always holds the Crimson Martial Shirt.
  - Five martial shirts, the Orange Martial Shirt recoloured, each with 100 resistance of its school:
    Crimson (fire), Azure (frost), Verdant (nature), Violet (shadow), Ivory (arcane).
  - Mathredis Firestar (Burning Steppes) takes the new librams like the stock ones: a Black Diamond, 30 gold
    and two more reagents make a belt arcanum. The Libram of Ferocity makes the Arcanum of Ferocity (+1%
    critical strike) or of Precision (+1% hit); the Libram of the Bulwark the Arcanum of the Bulwark (+1%
    block) or of Evasion (+1% dodge). Their use spells and enchantments: build_mastery.py, BELT_ARCANA.

usage: build_black_vault.py
       build_black_vault.py <in patch-Z.MPQ> <out patch-Z.MPQ> <stock SpellItemEnchantment.dbc> <texture dir>
  (the texture dir holds the Orange Martial Shirt's Robe_C_04*.blp from texture.MPQ; the server's
  SpellItemEnchantment.dbc is written beside the output as server-SpellItemEnchantment.dbc)
"""
import colorsys
import io
import os
import struct
import sys

from build_content import esc, insert
from build_mastery import ITEM_COLUMNS, BELT_ARCANA, ENCHANT_HIT_1, clone, read_dbc, write_dbc, add_string

HERE = os.path.dirname(os.path.abspath(__file__))

ORANGE_MARTIAL_SHIRT, ORANGE_MARTIAL_LOOK = 10052, 18916
# school: (item, name, display, resistance column, icon, hue, saturation scale, value scale)
SHIRTS = [
    ('Fire', 191400, 'Crimson Martial Shirt', 60400, 'fire_res', 'INV_Shirt_Red_01', 0, 1.0, 0.92),
    ('Frost', 191401, 'Azure Martial Shirt', 60401, 'frost_res', 'INV_Shirt_Blue_01', 212, 0.95, 0.95),
    ('Nature', 191402, 'Verdant Martial Shirt', 60402, 'nature_res', 'INV_Shirt_Green_01', 112, 0.9, 0.85),
    ('Shadow', 191403, 'Violet Martial Shirt', 60403, 'shadow_res', 'INV_Shirt_Purple_01', 278, 0.85, 0.85),
    ('Arcane', 191404, 'Ivory Martial Shirt', 60404, 'arcane_res', 'INV_Shirt_White_01', 230, 0.10, 1.45),
]
SHIRT_RESISTANCE = 100
FIRE_SHIRT = SHIRTS[0][1]
# the shirt's textures: (ItemDisplayInfo texture field, component folder, stock name, gendered)
SHIRT_TEXTURES = [
    (14, 'ArmUpperTexture', 'Robe_C_04Orange_Sleeve_AU', False),
    (15, 'ArmLowerTexture', 'Robe_C_04Blue_Sleeve_AL', False),
    (17, 'TorsoUpperTexture', 'Robe_C_04Orange_Chest_TU', True),
    (18, 'TorsoLowerTexture', 'Robe_C_04Orange_Chest_TL', True),
]

LIBRAM_OF_CONSTITUTION, LESSER_ARCANUM = 11733, 11642
STOCK_LIBRAMS = [11733, 11736, 11732, 11734, 11737]   # Constitution, Resilience, Rumination, Tenacity, Voracity
LIBRAM_FEROCITY, LIBRAM_BULWARK = 191410, 191411
ARCANUM_ITEMS = [191412, 191413, 191414, 191415]      # Ferocity, Precision, the Bulwark, Evasion (BELT_ARCANA order)
BLACK_DIAMOND, HEART_OF_FIRE, ELEMENTAL_FIRE, CORE_OF_EARTH, ELEMENTAL_EARTH = 11754, 7077, 7068, 7075, 7067
MATHREDIS, LIBRAM_QUEST_SOURCE = 9836, 4481
QUESTS = [90560, 90561, 90562, 90563]

RELIC_COFFER, RELIC_COFFER_LOOT, DARK_COFFER, DARK_COFFER_LOOT = 160836, 11105, 160845, 11103
SECRET_SAFE = 161495
DARK_KEEPER_KEY, WATCHMAN_DOOMGRIP = 11197, 9476
DARK_KEEPERS = (9437, 9438, 9439, 9441, 9442, 9443)
# our coffers: one each for the five stock librams, then Ferocity and the Bulwark; entry = loot id
COFFERS = [191420, 191421, 191422, 191423, 191424, 191425, 191426]
COFFER_LIBRAMS = STOCK_LIBRAMS + [LIBRAM_FEROCITY, LIBRAM_BULWARK]
# the stock spawns (map 230), the way in first: the vault's back wall holds the Secret Safe (the Dark
# Coffer inside) between its middle two coffers, and its side walls run out towards the way in
LEFT_SIDE = [2300077, 2300082, 2300083, 2300084, 2300086, 2300079]
RIGHT_SIDE = [2300081, 2300078, 2300080, 2300085, 2300087, 2300076]

GO_COLUMNS = ['entry', 'type', 'displayId', 'name', 'faction', 'flags', 'ExtraFlags', 'size', 'data0', 'data1',
              'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'data11', 'data12',
              'data13', 'data14', 'data15', 'data16', 'data17', 'data18', 'data19', 'data20', 'data21', 'data22',
              'data23', 'CustomData1', 'mingold', 'maxgold', 'StringId', 'ScriptName']
LOOT_COLUMNS = ['item', 'ChanceOrQuestChance', 'groupid', 'mincountOrRef', 'maxcount', 'condition_id', 'comments']
# quest_template's columns (cmangos classic)
QUEST_COLUMNS = ['entry', 'Method', 'ZoneOrSort', 'MinLevel', 'MaxLevel', 'QuestLevel', 'Type', 'RequiredClasses',
    'RequiredRaces', 'RequiredSkill', 'RequiredSkillValue', 'RequiredCondition', 'RepObjectiveFaction',
    'RepObjectiveValue', 'RequiredMinRepFaction', 'RequiredMinRepValue', 'RequiredMaxRepFaction',
    'RequiredMaxRepValue', 'SuggestedPlayers', 'LimitTime', 'QuestFlags', 'SpecialFlags', 'PrevQuestId',
    'NextQuestId', 'ExclusiveGroup', 'BreadcrumbForQuestId', 'NextQuestInChain', 'SrcItemId', 'SrcItemCount',
    'SrcSpell', 'Title', 'Details', 'Objectives', 'OfferRewardText', 'RequestItemsText', 'EndText',
    'ObjectiveText1', 'ObjectiveText2', 'ObjectiveText3', 'ObjectiveText4', 'ReqItemId1', 'ReqItemId2',
    'ReqItemId3', 'ReqItemId4', 'ReqItemCount1', 'ReqItemCount2', 'ReqItemCount3', 'ReqItemCount4', 'ReqSourceId1',
    'ReqSourceId2', 'ReqSourceId3', 'ReqSourceId4', 'ReqSourceCount1', 'ReqSourceCount2', 'ReqSourceCount3',
    'ReqSourceCount4', 'ReqCreatureOrGOId1', 'ReqCreatureOrGOId2', 'ReqCreatureOrGOId3', 'ReqCreatureOrGOId4',
    'ReqCreatureOrGOCount1', 'ReqCreatureOrGOCount2', 'ReqCreatureOrGOCount3', 'ReqCreatureOrGOCount4',
    'ReqSpellCast1', 'ReqSpellCast2', 'ReqSpellCast3', 'ReqSpellCast4', 'RewChoiceItemId1', 'RewChoiceItemId2',
    'RewChoiceItemId3', 'RewChoiceItemId4', 'RewChoiceItemId5', 'RewChoiceItemId6', 'RewChoiceItemCount1',
    'RewChoiceItemCount2', 'RewChoiceItemCount3', 'RewChoiceItemCount4', 'RewChoiceItemCount5',
    'RewChoiceItemCount6', 'RewItemId1', 'RewItemId2', 'RewItemId3', 'RewItemId4', 'RewItemCount1',
    'RewItemCount2', 'RewItemCount3', 'RewItemCount4', 'RewRepFaction1', 'RewRepFaction2', 'RewRepFaction3',
    'RewRepFaction4', 'RewRepFaction5', 'RewRepValue1', 'RewRepValue2', 'RewRepValue3', 'RewRepValue4',
    'RewRepValue5', 'RewOrReqMoney', 'RewMoneyMaxLevel', 'RewSpell', 'RewSpellCast', 'RewMailTemplateId',
    'RewMailDelaySecs', 'PointMapId', 'PointX', 'PointY', 'PointOpt', 'DetailsEmote1', 'DetailsEmote2',
    'DetailsEmote3', 'DetailsEmote4', 'DetailsEmoteDelay1', 'DetailsEmoteDelay2', 'DetailsEmoteDelay3',
    'DetailsEmoteDelay4', 'IncompleteEmote', 'IncompleteEmoteDelay', 'CompleteEmote', 'CompleteEmoteDelay',
    'OfferRewardEmote1', 'OfferRewardEmote2', 'OfferRewardEmote3', 'OfferRewardEmote4', 'OfferRewardEmoteDelay1',
    'OfferRewardEmoteDelay2', 'OfferRewardEmoteDelay3', 'OfferRewardEmoteDelay4', 'StartScript', 'CompleteScript']


def item_sql():
    out = []
    for school, item, name, display, column, _icon, _h, _s, _v in SHIRTS:
        out.append(clone('item_template', 'entry', item, ORANGE_MARTIAL_SHIRT, ITEM_COLUMNS))
        out.append('UPDATE `item_template` SET `name` = %s, `displayid` = %d, `Quality` = 3, `bonding` = 1, '
                   '`ItemLevel` = 55, `RequiredLevel` = 50, `BuyPrice` = 0, `SellPrice` = 12500, `%s` = %d, '
                   '`description` = %s WHERE `entry` = %d;\n'
                   % (esc(name), display, column, SHIRT_RESISTANCE,
                      esc('Woven in the Shadowforge for the Dark Iron elite.'), item))
    for item, name, text in [
            (LIBRAM_FEROCITY, 'Libram of Ferocity', 'Runes of blades and blood. Mathredis Firestar would know them.'),
            (LIBRAM_BULWARK, 'Libram of the Bulwark', 'Runes of shields and walls. Mathredis Firestar would know them.')]:
        out.append(clone('item_template', 'entry', item, LIBRAM_OF_CONSTITUTION, ITEM_COLUMNS))
        out.append('UPDATE `item_template` SET `name` = %s, `description` = %s WHERE `entry` = %d;\n'
                   % (esc(name), esc(text), item))
    for item, (spell, name, _text, _enchant) in zip(ARCANUM_ITEMS, BELT_ARCANA):
        out.append(clone('item_template', 'entry', item, LESSER_ARCANUM, ITEM_COLUMNS))
        out.append('UPDATE `item_template` SET `name` = %s, `spellid_1` = %d WHERE `entry` = %d;\n'
                   % (esc(name), spell, item))
    return out


def loot_sql():
    out = []
    # the Dark Keeper Key: Watchman Doomgrip's, always; no Dark Keeper's
    out.append('DELETE FROM `creature_loot_template` WHERE `item` = %d AND `entry` IN (%s);\n'
               % (DARK_KEEPER_KEY, ', '.join(str(k) for k in DARK_KEEPERS + (WATCHMAN_DOOMGRIP,))))
    out.append(insert('creature_loot_template', [dict(
        entry=WATCHMAN_DOOMGRIP, item=DARK_KEEPER_KEY, ChanceOrQuestChance=100, groupid=0, mincountOrRef=1,
        maxcount=1, condition_id=0, comments='Zelda: the Dark Coffer')]))
    # the key is kept: stock it is spent (charges -1) on the vault's last door (174565, lock 659), and the
    # Dark Coffer behind that door asks for it again (ZeldaDoorKeyHeld)
    out.append('UPDATE `item_template` SET `spellcharges_1` = 0 WHERE `entry` = %d;\n' % DARK_KEEPER_KEY)
    # the Dark Coffer: openable (no GO_FLAG_NO_INTERACT; the key is checked by the core), the fire shirt always
    out.append('UPDATE `gameobject_template` SET `flags` = 0 WHERE `entry` = %d;\n' % DARK_COFFER)
    # the Secret Safe the Dark Coffer sits over: usable too (the vault's end cleared its NO_INTERACT only
    # for that moment, and a restart brought it back), so it never stands between the cursor and the coffer
    out.append('UPDATE `gameobject_template` SET `flags` = 0 WHERE `entry` = %d;\n' % SECRET_SAFE)
    out.append('DELETE FROM `gameobject_loot_template` WHERE `entry` = %d AND `item` = %d;\n'
               % (DARK_COFFER_LOOT, FIRE_SHIRT))
    out.append(insert('gameobject_loot_template', [dict(
        entry=DARK_COFFER_LOOT, item=FIRE_SHIRT, ChanceOrQuestChance=100, groupid=0, mincountOrRef=1, maxcount=1,
        condition_id=0, comments='Zelda: Crimson Martial Shirt')]))
    # the relic coffers: the stock chest, openable, each with its trinkets and its libram
    cols = ', '.join('`%s`' % c for c in LOOT_COLUMNS)
    for entry, libram in zip(COFFERS, COFFER_LIBRAMS):
        out.append(clone('gameobject_template', 'entry', entry, RELIC_COFFER, GO_COLUMNS))
        out.append('UPDATE `gameobject_template` SET `flags` = 0, `data1` = %d WHERE `entry` = %d;\n' % (entry, entry))
        out.append('DELETE FROM `gameobject_loot_template` WHERE `entry` = %d;\n' % entry)
        out.append('INSERT INTO `gameobject_loot_template` (`entry`, %s) SELECT %d, %s FROM `gameobject_loot_template` '
                   'WHERE `entry` = %d;\n' % (cols, entry, cols, RELIC_COFFER_LOOT))
        out.append(insert('gameobject_loot_template', [dict(
            entry=entry, item=libram, ChanceOrQuestChance=100, groupid=0, mincountOrRef=1, maxcount=1,
            condition_id=0, comments='Zelda: the Black Vault')]))
    for side in (LEFT_SIDE, RIGHT_SIDE):
        for n, guid in enumerate(side):
            entry = COFFERS[n] if n < 5 else COFFERS[5 if side is LEFT_SIDE else 6]
            out.append('UPDATE `gameobject` SET `id` = %d WHERE `guid` = %d;\n' % (entry, guid))
    return out


def quest_sql():
    out = []
    reagents = {LIBRAM_FEROCITY: [(HEART_OF_FIRE, 2), (ELEMENTAL_FIRE, 4)],
                LIBRAM_BULWARK: [(CORE_OF_EARTH, 2), (ELEMENTAL_EARTH, 4)]}
    books = [LIBRAM_FEROCITY, LIBRAM_FEROCITY, LIBRAM_BULWARK, LIBRAM_BULWARK]
    ids = ', '.join(str(q) for q in QUESTS)
    out.append('DELETE FROM `creature_questrelation` WHERE `quest` IN (%s);\n' % ids)
    out.append('DELETE FROM `creature_involvedrelation` WHERE `quest` IN (%s);\n' % ids)
    for quest, book, item, (_spell, name, _text, _enchant) in zip(QUESTS, books, ARCANUM_ITEMS, BELT_ARCANA):
        (r1, c1), (r2, c2) = reagents[book]
        out.append(clone('quest_template', 'entry', quest, LIBRAM_QUEST_SOURCE, QUEST_COLUMNS))
        out.append('UPDATE `quest_template` SET `Title` = %s, `ReqItemId1` = %d, `ReqItemCount1` = 1, '
                   '`ReqItemId2` = %d, `ReqItemCount2` = 1, `ReqItemId3` = %d, `ReqItemCount3` = %d, '
                   '`ReqItemId4` = %d, `ReqItemCount4` = %d, `RewItemId1` = %d, `RewItemCount1` = 1, '
                   '`RewOrReqMoney` = -300000 WHERE `entry` = %d;\n'
                   % (esc(name), book, BLACK_DIAMOND, r1, c1, r2, c2, item, quest))
        out.append(insert('creature_questrelation', [dict(id=MATHREDIS, quest=quest)]))
        out.append(insert('creature_involvedrelation', [dict(id=MATHREDIS, quest=quest)]))
    return out


def write_sql():
    out = ['-- Zelda of Warcraft: the Black Vault, its librams and shirts, and the belt arcanums (build_black_vault.py)\n']
    out += item_sql() + loot_sql() + quest_sql()
    path = os.path.join(HERE, 'zelda-sql', '026_black_vault.sql')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(out))
    print('wrote', path, os.path.getsize(path), 'bytes')


# ------------------------------------------------------------------ the client: shirts and enchantments
def recolor(image, hue, sat, val):
    """The shirt's orange (and its gold trim) in the school's colour; its white, black and grey stay."""
    image = image.convert('RGBA')
    px = image.load()
    w, h = image.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            deg = hh * 360
            if (deg <= 55 or deg >= 340) and s > 0.30 and (deg >= 4 or v > 0.2):
                nr, ng, nb = colorsys.hsv_to_rgb(hue / 360, min(1, s * sat), min(1, v * val))
                px[x, y] = (int(nr * 255 + .5), int(ng * 255 + .5), int(nb * 255 + .5), a)
    return image


def load_blp(data):
    """A palette BLP2 (1- or 8-bit alpha), as Pillow misreads their alpha."""
    from PIL import Image
    _typ, comp, adepth, _atype, _mips = struct.unpack_from('<IBBBB', data, 4)
    w, h = struct.unpack_from('<II', data, 12)
    if comp != 1:
        return Image.open(io.BytesIO(data)).convert('RGBA')
    off = struct.unpack_from('<16I', data, 20)[0]
    pal = [struct.unpack_from('<4B', data, 148 + 4 * i) for i in range(256)]
    n = w * h
    idx = data[off:off + n]
    if adepth == 8:
        alpha = data[off + n:off + 2 * n]
    elif adepth == 1:
        bits = data[off + n:off + n + (n + 7) // 8]
        alpha = bytes(255 if bits[i >> 3] >> (i & 7) & 1 else 0 for i in range(n))
    else:
        alpha = bytes([255]) * n
    im = Image.new('RGBA', (w, h))
    im.putdata([(pal[i][2], pal[i][1], pal[i][0], alpha[k]) for k, i in enumerate(idx)])
    return im


def shirt_files(texture_dir):
    """{MPQ path: BLP bytes} for every shirt's textures, and {display id: {texture field: name}}."""
    from scarlet_horse import blp_raw1_alpha
    files, names = {}, {}
    for school, _item, _name, display, _col, _icon, hue, sat, val in SHIRTS:
        names[display] = {}
        for field, folder, stock, gendered in SHIRT_TEXTURES:
            base = 'ZeldaMartial%s_%s' % (school, stock.split('_')[-1])
            names[display][field] = base
            for suffix in (('_M', '_F') if gendered else ('_U',)):
                src = open(os.path.join(texture_dir, stock + suffix + '.blp'), 'rb').read()
                files['Item\\TextureComponents\\%s\\%s%s.blp' % (folder, base, suffix)] = \
                    blp_raw1_alpha(recolor(load_blp(src), hue, sat, val))
    return files, names


def patch_display(dbc_bytes, names):
    path = os.path.join('/tmp', 'vault-ItemDisplayInfo.dbc')
    open(path, 'wb').write(dbc_bytes)
    f, rows, strings = read_dbc(path)
    ours = {s[3] for s in SHIRTS}
    rows = [r for r in rows if r[0] not in ours]
    source = next(r for r in rows if r[0] == ORANGE_MARTIAL_LOOK)
    for _school, _item, _name, display, _col, icon, *_ in SHIRTS:
        row = list(source)
        row[0] = display
        row[5] = add_string(strings, icon)
        for field, name in names[display].items():
            row[field] = add_string(strings, name)
        rows.append(row)
    rows.sort(key=lambda r: r[0])
    return write_dbc(f, rows, strings)


# the head and leg arcanums Mathredis Firestar makes, changed in their stock enchantment rows (so a helm or
# legs already enchanted change too): {enchantment: (equip spells, name)}; texts: build_mastery.py
LESSER_ARCANA = [
    (1483, (7597,), 'Critical Hit +1%'),                    # Rumination: +150 mana -> +1% crit
    (1503, (15464,), '+1% Hit'),                            # Constitution: +100 health -> +1% hit
    (1504, (21469, 13669), '+1% Block and +1% Dodge'),      # Tenacity: +125 armor -> +1% block and dodge
    (1505, (18691,), '+20 All Resistances'),                # Resilience: +20 fire -> +20 every school
]


def patch_enchantments(path):
    """SpellItemEnchantment with ENCHANT_HIT_1: +1% hit (Increased Hit Chance 1, 15464), like 195's +1% crit."""
    f, rows, strings = read_dbc(path)
    rows = [r for r in rows if r[0] != ENCHANT_HIT_1]
    row = list(next(r for r in rows if r[0] == 195))
    row[0] = ENCHANT_HIT_1
    row[10] = 15464
    row[13] = add_string(strings, '+1% Hit')
    rows.append(row)
    for enchant, spells, name in LESSER_ARCANA:
        row = next(r for r in rows if r[0] == enchant)
        for k in range(3):
            row[1 + k] = 3 if k < len(spells) else 0
            row[4 + k] = row[7 + k] = 0
            row[10 + k] = spells[k] if k < len(spells) else 0
        row[13] = add_string(strings, name)
    rows.sort(key=lambda r: r[0])
    return write_dbc(f, rows, strings)


def build_patch(patch_in, patch_out, enchant_dbc, texture_dir):
    sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
    import mpq
    a = mpq.Archive(patch_in)
    names_in = [n for n in a.read('(listfile)').decode('latin1').split('\r\n') if n and n != '(listfile)']
    files = {n: a.read(n) for n in names_in}
    textures, names = shirt_files(texture_dir)
    files.update(textures)
    files['DBFilesClient\\ItemDisplayInfo.dbc'] = patch_display(files['DBFilesClient\\ItemDisplayInfo.dbc'], names)
    enchant = patch_enchantments(enchant_dbc)
    files['DBFilesClient\\SpellItemEnchantment.dbc'] = enchant
    mpq.write_archive(patch_out, files)
    server = os.path.join(os.path.dirname(os.path.abspath(patch_out)), 'server-SpellItemEnchantment.dbc')
    with open(server, 'wb') as fh:
        fh.write(enchant)
    print('wrote', patch_out, os.path.getsize(patch_out), 'bytes, and', server)


if __name__ == '__main__':
    write_sql()
    if len(sys.argv) == 5:
        build_patch(*sys.argv[1:])
