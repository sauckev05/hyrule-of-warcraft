"""Zelda of Warcraft: the Sword of Mastery.

Linken's Sword of Mastery (the reward of Linken's quests, item 11902) becomes the epic *Unfinished
Sword of Mastery*: Quel'Serrar's blade with a blue glow instead of its green one. Like Jang'thraze
and Sang'thraze becoming Sul'thraze, using it while carrying Quel'Serrar forges the two into the
legendary *Sword of Mastery* (191001): the look of the Grand Marshal's Longsword, 138-207 damage at
2.90 speed, +25 to every stat, 2% hit and 2% critical strike with melee attacks and spells (heals
included), a holy strike that burns the enemy for 150-300 and heals the wielder as much, and about
a 15% chance per swing of two extra attacks.

Writes
  - zelda-sql/006_mastery.sql: the spells (spell_template) and the two swords (item_template)
  - patch-Z.MPQ (when given the client's ItemDisplayInfo.dbc and Spell.dbc): the blue-glow look
    and the new spells' names and tooltips, for the client's Data folder (both clients load it)

The client patch also clears the target aura state of Execute, so the client lets it be pressed on
any target; the server still asks for the target under 20% health, or full rage (Zelda.FullRageExecute).

usage: build_mastery.py [<ItemDisplayInfo.dbc> <Spell.dbc> <output patch-Z.MPQ> [<shard icon .blp>]]
  (the shard icon is Interface\\Icons\\INV_Enchant_ShardGlimmeringLarge.blp from interface.MPQ)
  (the two .dbc files may come from the client's MPQs or from an existing patch-Z.MPQ)
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))

UNFINISHED = 11902          # Linken's Sword of Mastery
QUEL_SERRAR = 18348
MASTERY = 191001            # the Sword of Mastery
GRAND_MARSHAL_LONGSWORD = 12584

QUEL_SERRAR_LOOK = 30994    # Quel'Serrar's ItemDisplayInfo
UNFINISHED_LOOK = 60101     # the same with a blue glow
BLUE_GLOW = 42              # ItemVisuals: the blue glow of Azuresong Mageblade and Glacial Blade
MASTERY_LOOK = 31966        # Grand Marshal's Longsword

STR, AGI, STA, INT, SPI = 4, 3, 7, 5, 6
EXTRA_ATTACKS = 15494       # Ironfoe's Fury of Forgewright: 2 extra attacks on the next swing

# custom spells: (id, cloned from, name, tooltip text, changes)
#   changes: {spell_template column: value}, and copy_effect1_to_2 to add a second aura like the first
SPELLS = [
    (40001, 11654, 'Forge the Sword of Mastery',
     "Combines the Unfinished Sword of Mastery and Quel'Serrar to forge the legendary Sword of Mastery.",
     dict(EffectItemType1=MASTERY, Reagent1=0, ReagentCount1=0, Reagent2=QUEL_SERRAR, ReagentCount2=1)),
    (40002, 25912, 'Light of Mastery',
     'Burns the enemy with holy light for 150 to 300 Holy damage and heals you for 150 to 300.',
     dict(EffectBasePoints1=149, EffectDieSides1=151, EffectBaseDice1=1)),
    (40003, 25914, 'Light of Mastery', '', dict(EffectBasePoints1=149, EffectDieSides1=151, EffectBaseDice1=1)),
    (40004, 15465, 'Mastery of the Blade', 'Improves your chance to hit with melee attacks and spells by 2%.',
     dict(copy_effect1_to_2=True, EffectApplyAuraName2=55)),
    (40005, 7598, 'Mastery of the Blade',
     'Improves your chance to get a critical strike with melee attacks, spells and heals by 2%.',
     dict(copy_effect1_to_2=True, EffectApplyAuraName2=57)),
    (40006, 25912, 'Light of Linken',
     'Burns the enemy with holy light for 75 to 150 Holy damage and heals you for 75 to 150.',
     dict(EffectBasePoints1=74, EffectDieSides1=76, EffectBaseDice1=1)),
    (40007, 25914, 'Light of Linken', '', dict(EffectBasePoints1=74, EffectDieSides1=76, EffectBaseDice1=1)),
    # Berserker Stance's charged attack (ZeldaCommands.cpp, ZeldaLeapingStrike): a plain melee-class
    # physical strike whose damage the server sets (twice the attack power); it crits like melee
    (40008, 2816, 'Leaping Strike', 'Leaps forward, striking every enemy in front of you for twice your attack power.', {}),
    # Navi's revive (ZeldaCommands.cpp, ZeldaNaviResurrection): a soulstone-style self resurrection that
    # brings you back with 10% of your health and mana, in a priest's resurrection light
    (40009, 3026, "Navi's Light", "Navi's light brings you back to life with 10% of your health and mana.",
     dict(EffectBasePoints1=9, SpellVisual=41, SpellIconID=121)),
    # a mana potion's mana as an absorb shield (ZeldaManaPotionShield); the core sets the amount
    (40010, 23506, 'Potion Shield', 'Absorbs $s1 damage.  Lasts $d.', dict(tooltip='Absorbs $s1 damage.')),
    # the enemies' telegraphed attacks (ZeldaEnemyMechanics): a two-second windup whose dummy effect
    # the core resolves - blocked, parried, dodged or landing for a share of the hero's health
    (40011, 1464, 'Heavy Blow', 'A slow, crushing blow. Raise your shield, parry, or roll away!',
     dict(CastingTimeIndex=5, Effect1=3, EffectBasePoints1=0, EffectImplicitTargetA1=6, DmgClass=0, ManaCost=0,
          PowerType=0, InterruptFlags=0, EquippedItemClass=-1, SpellFamilyName=0, SpellFamilyFlags=0,
          Attributes=16, AttributesEx=0, AttributesEx3=0)),
    (40012, 17393, 'Charged Bolt', 'A slow, heavy bolt. Raise your shield or roll away!',
     dict(Effect1=3, EffectBasePoints1=0, EffectDieSides1=0, EffectImplicitTargetA1=6, DmgClass=0, ManaCost=0,
          InterruptFlags=0, School=6, SpellFamilyName=0, SpellFamilyFlags=0)),
    # the Vanquisher's Sword's equip effect (ZeldaCritHeal): each melee critical strike heals $s1% of
    # the hero's maximum health
    (40018, 9335, "Vanquisher's Mercy", 'Your melee critical strikes heal you for $s1% of your maximum health.',
     dict(EffectApplyAuraName1=4, EffectBasePoints1=4, EffectMiscValue1=0)),
] + [
    # Mace Specialization's armor crush (ZeldaAfterMeleeHit): each mace hit lowers the enemy's armor by
    # the talent's points in percent, stacking up to five times - one spell per rank (40013 = rank 1
    # ... 40017 = rank 5), so every stack counts its full amount
    (40012 + rank, 11971, 'Crushing Blows', 'Lowers armor by $s1% per stack, up to 5 stacks.',
     dict(EffectApplyAuraName1=101, EffectBasePoints1=-(rank + 1), EffectDieSides1=1, EffectMiscValue1=1, DmgClass=0,
          PowerType=0, ManaCost=0, EquippedItemClass=-1, SpellFamilyName=0, SpellFamilyFlags=0,
          tooltip='Armor reduced by $s1% per stack.'))
    for rank in range(1, 6)
]

# stock items changed in place: {item entry: {item_template column: value}}
ITEM_EDITS = {
    # Vanquisher's Sword: 65-120 at 2.70 speed, its attack power kept, Vanquisher's Mercy added
    10823: dict(dmg_min1=65, dmg_max1=120, delay=2700, spellid_2=40018, spelltrigger_2=1, spellcharges_2=0,
                spellcooldown_2=-1, spellcategory_2=0, spellcategorycooldown_2=-1),
}

# stock spell texts changed in the client (patch-Z only): mana potions are shields now
DESCRIPTION_EDITS = {sid: 'Shields you, absorbing $s1 damage for 20 sec.'
                     for sid in (437, 438, 2023, 11903, 17530, 17531, 21395, 21396)}
# Dual Wield Specialization (warrior and rogue): melee hit while two weapons are held, not off-hand
# damage (ZeldaDualWieldHit); a dummy aura whose $s1 is the rank
DUAL_WIELD_SPEC = (23584, 23585, 23586, 23587, 23588, 13715, 13848, 13849, 13851, 13852)
for _n, _sid in enumerate(DUAL_WIELD_SPEC):
    DESCRIPTION_EDITS[_sid] = 'Increases your chance to hit with melee attacks by $s1% while dual wielding.'
# Mace Specialization: its stun stays, and every mace hit also crushes armor (Crushing Blows, 40013)
MACE_SPEC = (12284, 12701, 12702, 12703, 12704)
for _n, _sid in enumerate(MACE_SPEC):
    DESCRIPTION_EDITS[_sid] = ('Gives you a $h%% chance to stun your target for 3 sec with a Mace. Every hit with a '
                               'mace also lowers the target\'s armor by %d%%, stacking up to 5 times.' % (_n + 1))

# stock spells changed in place: {spell id: {spell_template column: value}}
SPELL_EDITS = {
    7381: dict(EffectBasePoints1=9),    # Berserker Stance Passive: 10% critical strike instead of 3%
}
for _n, _sid in enumerate(DUAL_WIELD_SPEC):
    SPELL_EDITS[_sid] = dict(EffectApplyAuraName1=4, EffectBasePoints1=_n % 5)   # SPELL_AURA_DUMMY, rank - 1

# helmet looks whose hair stayed visible: {ItemDisplayInfo id: (male, female HelmetGeosetVisData)}
HELM_HIDES_HAIR = {
    4415: (248, 306),       # Helm_Plate_A_01Crusader: the Helm of the Scarlet Crusade (sets.py)
}

# mounts (an aura 78 MOUNTED spell with its aura 32 MOD_INCREASE_MOUNTED_SPEED in effect 2): the
# regular ones go 150% faster instead of 60%, the epic ones 200% instead of 100%
MOUNT_SPEED = {59: 149, 99: 199}
MOUNT_AURA, MOUNT_SPEED_AURA = 78, 32

EFFECT_GROUPS = ['Effect', 'EffectDieSides', 'EffectBaseDice', 'EffectDicePerLevel', 'EffectRealPointsPerLevel',
                 'EffectBasePoints', 'EffectMechanic', 'EffectImplicitTargetA', 'EffectImplicitTargetB',
                 'EffectRadiusIndex', 'EffectApplyAuraName', 'EffectAmplitude', 'EffectMultipleValue',
                 'EffectChainTarget', 'EffectItemType', 'EffectMiscValue', 'EffectTriggerSpell',
                 'EffectPointsPerComboPoint', 'DmgMultiplier']

SPELL_COLUMNS = ['Id', 'School', 'Category', 'CastUI', 'Dispel', 'Mechanic', 'Attributes', 'AttributesEx', 'AttributesEx2',
    'AttributesEx3', 'AttributesEx4', 'Stances', 'StancesNot', 'Targets', 'TargetCreatureType',
    'RequiresSpellFocus', 'CasterAuraState', 'TargetAuraState', 'CastingTimeIndex', 'RecoveryTime',
    'CategoryRecoveryTime', 'InterruptFlags', 'AuraInterruptFlags', 'ChannelInterruptFlags', 'ProcFlags',
    'ProcChance', 'ProcCharges', 'MaxLevel', 'BaseLevel', 'SpellLevel', 'DurationIndex', 'PowerType',
    'ManaCost', 'ManaCostPerlevel', 'ManaPerSecond', 'ManaPerSecondPerLevel', 'RangeIndex', 'Speed',
    'ModalNextSpell', 'StackAmount', 'Totem1', 'Totem2', 'Reagent1', 'Reagent2', 'Reagent3', 'Reagent4',
    'Reagent5', 'Reagent6', 'Reagent7', 'Reagent8', 'ReagentCount1', 'ReagentCount2', 'ReagentCount3',
    'ReagentCount4', 'ReagentCount5', 'ReagentCount6', 'ReagentCount7', 'ReagentCount8', 'EquippedItemClass',
    'EquippedItemSubClassMask', 'EquippedItemInventoryTypeMask', 'Effect1', 'Effect2', 'Effect3',
    'EffectDieSides1', 'EffectDieSides2', 'EffectDieSides3', 'EffectBaseDice1', 'EffectBaseDice2',
    'EffectBaseDice3', 'EffectDicePerLevel1', 'EffectDicePerLevel2', 'EffectDicePerLevel3',
    'EffectRealPointsPerLevel1', 'EffectRealPointsPerLevel2', 'EffectRealPointsPerLevel3',
    'EffectBasePoints1', 'EffectBasePoints2', 'EffectBasePoints3', 'EffectMechanic1', 'EffectMechanic2',
    'EffectMechanic3', 'EffectImplicitTargetA1', 'EffectImplicitTargetA2', 'EffectImplicitTargetA3',
    'EffectImplicitTargetB1', 'EffectImplicitTargetB2', 'EffectImplicitTargetB3', 'EffectRadiusIndex1',
    'EffectRadiusIndex2', 'EffectRadiusIndex3', 'EffectApplyAuraName1', 'EffectApplyAuraName2',
    'EffectApplyAuraName3', 'EffectAmplitude1', 'EffectAmplitude2', 'EffectAmplitude3',
    'EffectMultipleValue1', 'EffectMultipleValue2', 'EffectMultipleValue3', 'EffectChainTarget1',
    'EffectChainTarget2', 'EffectChainTarget3', 'EffectItemType1', 'EffectItemType2', 'EffectItemType3',
    'EffectMiscValue1', 'EffectMiscValue2', 'EffectMiscValue3', 'EffectTriggerSpell1', 'EffectTriggerSpell2',
    'EffectTriggerSpell3', 'EffectPointsPerComboPoint1', 'EffectPointsPerComboPoint2',
    'EffectPointsPerComboPoint3', 'SpellVisual', 'SpellIconID', 'ActiveIconID', 'SpellPriority', 'SpellName',
    'SpellName2', 'SpellName3', 'SpellName4', 'SpellName5', 'SpellName6', 'SpellName7', 'SpellName8',
    'Rank1', 'Rank2', 'Rank3', 'Rank4', 'Rank5', 'Rank6', 'Rank7', 'Rank8', 'ManaCostPercentage',
    'StartRecoveryCategory', 'StartRecoveryTime', 'MaxTargetLevel', 'SpellFamilyName', 'SpellFamilyFlags',
    'MaxAffectedTargets', 'DmgClass', 'PreventionType', 'StanceBarOrder', 'DmgMultiplier1', 'DmgMultiplier2',
    'DmgMultiplier3', 'MinFactionId', 'MinReputation', 'RequiredAuraVision', 'IsServerSide',
    'AttributesServerside']
ITEM_COLUMNS = ['entry', 'class', 'subclass', 'name', 'displayid', 'Quality', 'Flags', 'BuyCount', 'BuyPrice', 'SellPrice',
    'InventoryType', 'AllowableClass', 'AllowableRace', 'ItemLevel', 'RequiredLevel', 'RequiredSkill',
    'RequiredSkillRank', 'requiredspell', 'requiredhonorrank', 'RequiredCityRank',
    'RequiredReputationFaction', 'RequiredReputationRank', 'maxcount', 'stackable', 'ContainerSlots',
    'stat_type1', 'stat_value1', 'stat_type2', 'stat_value2', 'stat_type3', 'stat_value3', 'stat_type4',
    'stat_value4', 'stat_type5', 'stat_value5', 'stat_type6', 'stat_value6', 'stat_type7', 'stat_value7',
    'stat_type8', 'stat_value8', 'stat_type9', 'stat_value9', 'stat_type10', 'stat_value10', 'dmg_min1',
    'dmg_max1', 'dmg_type1', 'dmg_min2', 'dmg_max2', 'dmg_type2', 'dmg_min3', 'dmg_max3', 'dmg_type3',
    'dmg_min4', 'dmg_max4', 'dmg_type4', 'dmg_min5', 'dmg_max5', 'dmg_type5', 'armor', 'holy_res',
    'fire_res', 'nature_res', 'frost_res', 'shadow_res', 'arcane_res', 'delay', 'ammo_type',
    'RangedModRange', 'spellid_1', 'spelltrigger_1', 'spellcharges_1', 'spellppmRate_1', 'spellcooldown_1',
    'spellcategory_1', 'spellcategorycooldown_1', 'spellid_2', 'spelltrigger_2', 'spellcharges_2',
    'spellppmRate_2', 'spellcooldown_2', 'spellcategory_2', 'spellcategorycooldown_2', 'spellid_3',
    'spelltrigger_3', 'spellcharges_3', 'spellppmRate_3', 'spellcooldown_3', 'spellcategory_3',
    'spellcategorycooldown_3', 'spellid_4', 'spelltrigger_4', 'spellcharges_4', 'spellppmRate_4',
    'spellcooldown_4', 'spellcategory_4', 'spellcategorycooldown_4', 'spellid_5', 'spelltrigger_5',
    'spellcharges_5', 'spellppmRate_5', 'spellcooldown_5', 'spellcategory_5', 'spellcategorycooldown_5',
    'bonding', 'description', 'PageText', 'LanguageID', 'PageMaterial', 'startquest', 'lockid', 'Material',
    'sheath', 'RandomProperty', 'block', 'itemset', 'MaxDurability', 'area', 'Map', 'BagFamily',
    'ScriptName', 'DisenchantID', 'FoodType', 'minMoneyLoot', 'maxMoneyLoot', 'Duration', 'ExtraFlags']

# Spell.dbc (1.12.1, 173 fields): where the spell_template columns sit
DBC_FIELD = {'Reagent1': 42, 'Reagent2': 43, 'ReagentCount1': 50, 'ReagentCount2': 51, 'SpellVisual': 115,
             'SpellIconID': 117, 'School': 1, 'Attributes': 6, 'AttributesEx': 7, 'AttributesEx3': 9, 'CastingTimeIndex': 18, 'InterruptFlags': 21, 'PowerType': 31,
             'ManaCost': 32, 'RangeIndex': 36, 'EquippedItemClass': 58, 'SpellFamilyName': 160,
             'SpellFamilyFlags': 161, 'DmgClass': 164}
SQL_ONLY = ('copy_effect1_to_2', 'tooltip')
for _i, _g in enumerate(EFFECT_GROUPS[:-1]):
    for _k in (1, 2, 3):
        DBC_FIELD['%s%d' % (_g, _k)] = 61 + _i * 3 + (_k - 1)
for _k in (1, 2, 3):
    DBC_FIELD['DmgMultiplier%d' % _k] = 166 + _k
DBC_NAME, DBC_RANK, DBC_DESCRIPTION, DBC_TOOLTIP = 120, 129, 138, 147
DBC_TARGET_AURA_STATE = 17
EXECUTE_RANKS = (5308, 20658, 20660, 20661, 20662)


def sql_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


# ------------------------------------------------------------------ server SQL
def clone(table, key, new_id, source_id, columns):
    rest = [c for c in columns if c != key]
    cols = ', '.join('`%s`' % c for c in rest)
    return ('DELETE FROM `%s` WHERE `%s` = %d;\n' % (table, key, new_id) +
            'INSERT INTO `%s` (`%s`, %s) SELECT %d, %s FROM `%s` WHERE `%s` = %d;\n'
            % (table, key, cols, new_id, cols, table, key, source_id))


def spell_sql():
    out = []
    for sid, source, name, text, changes in SPELLS:
        out.append(clone('spell_template', 'Id', sid, source, SPELL_COLUMNS))
        sets = ['`SpellName` = %s' % sql_str(name)]
        if changes.get('copy_effect1_to_2'):
            sets += ['`%s2` = `%s1`' % (g, g) for g in EFFECT_GROUPS]
        sets += ['`%s` = %d' % (k, v) for k, v in changes.items() if k not in SQL_ONLY]
        out.append('UPDATE `spell_template` SET %s WHERE `Id` = %d;\n' % (', '.join(sets), sid))
    for sid, changes in SPELL_EDITS.items():
        out.append('UPDATE `spell_template` SET %s WHERE `Id` = %d;\n'
                   % (', '.join('`%s` = %d' % kv for kv in changes.items()), sid))
    # epic first, so a regular mount raised to 149 is not raised again
    for old, new in sorted(MOUNT_SPEED.items(), reverse=True):
        out.append('UPDATE `spell_template` SET `EffectBasePoints2` = %d WHERE `EffectApplyAuraName2` = %d AND '
                   '`EffectBasePoints2` = %d AND %d IN (`EffectApplyAuraName1`, `EffectApplyAuraName3`);\n'
                   % (new, MOUNT_SPEED_AURA, old, MOUNT_AURA))
    return ''.join(out)


def spells_sql(slots):
    """item_template columns for the five item spells: (spell, trigger, ppm, charges)"""
    sets = []
    for n in range(1, 6):
        spell, trigger, ppm, charges = slots[n - 1] if n <= len(slots) else (0, 0, 0, 0)
        sets.append('`spellid_%d` = %d, `spelltrigger_%d` = %d, `spellppmRate_%d` = %s, `spellcharges_%d` = %d, '
                    '`spellcooldown_%d` = -1, `spellcategory_%d` = 0, `spellcategorycooldown_%d` = -1'
                    % (n, spell, n, trigger, n, ppm, n, charges, n, n, n))
    return ', '.join(sets)


def stats_sql(stats):
    sets = []
    for n in range(1, 11):
        t, v = stats[n - 1] if n <= len(stats) else (0, 0)
        sets.append('`stat_type%d` = %d, `stat_value%d` = %d' % (n, t, n, v))
    return ', '.join(sets)


def item_sql():
    out = []
    # the Unfinished Sword of Mastery: Linken's reward, now epic, in Quel'Serrar's shape
    out.append('UPDATE `item_template` SET `name` = %s, `Quality` = 4, `displayid` = %d, `ItemLevel` = 70, '
               '`dmg_min1` = 120, `dmg_max1` = 160, `dmg_type1` = 0, `delay` = 2600, `DisenchantID` = 0, '
               '`MaxDurability` = 125, %s, %s, `description` = %s WHERE `entry` = %d;\n'
               % (sql_str('Unfinished Sword of Mastery'), UNFINISHED_LOOK,
                  stats_sql([(AGI, 15), (STR, 15), (INT, 15), (SPI, 15), (STA, 15)]),
                  spells_sql([(40006, 2, 2.0, 0),                 # holy light, 75-150
                              (EXTRA_ATTACKS, 2, 1.15, 0),        # 2 extra attacks, about 5% of swings
                              (40001, 0, 0, -1)]),                # use: forge it with Quel'Serrar (used up)
                  sql_str("Linken's blade, waiting for a worthy steel to make it whole."), UNFINISHED))
    # the Sword of Mastery, made from the Grand Marshal's Longsword's row
    out.append(clone('item_template', 'entry', MASTERY, GRAND_MARSHAL_LONGSWORD, ITEM_COLUMNS))
    out.append('UPDATE `item_template` SET `name` = %s, `Quality` = 5, `Flags` = 0, `displayid` = %d, '
               '`ItemLevel` = 80, `RequiredLevel` = 60, `requiredhonorrank` = 0, `RequiredCityRank` = 0, '
               '`RequiredReputationFaction` = 0, `RequiredReputationRank` = 0, `AllowableClass` = -1, '
               '`AllowableRace` = -1, `BuyPrice` = 0, `SellPrice` = 250000, `bonding` = 1, `maxcount` = 1, '
               '`dmg_min1` = 138, `dmg_max1` = 207, `dmg_type1` = 0, `delay` = 2900, `MaxDurability` = 125, '
               '`DisenchantID` = 0, %s, %s, `description` = %s WHERE `entry` = %d;\n'
               % (sql_str('Sword of Mastery'), MASTERY_LOOK,
                  stats_sql([(STR, 25), (AGI, 25), (STA, 25), (INT, 25), (SPI, 25)]),
                  spells_sql([(40004, 1, 0, 0),                  # 2% hit, melee and spells
                              (40005, 1, 0, 0),                  # 2% crit, melee and spells (heals too)
                              (40002, 2, 2.0, 0),                # holy light, 150-300
                              (EXTRA_ATTACKS, 2, 3.1, 0)]),      # 2 extra attacks: 15% of swings at 2.90
                  sql_str("Linken's courage and Quel'Serrar's steel, made one."), MASTERY))
    return ''.join(out)


def write_sql():
    path = os.path.join(HERE, 'zelda-sql', '006_mastery.sql')
    edits = ''.join('UPDATE `item_template` SET %s WHERE `entry` = %d;\n'
                    % (', '.join('`%s` = %s' % (k, v) for k, v in cols.items()), entry)
                    for entry, cols in ITEM_EDITS.items())
    text = '-- Zelda of Warcraft: the Sword of Mastery (generated by build_mastery.py)\n' + spell_sql() + item_sql() + edits
    with open(path, 'w', newline='\n') as f:
        f.write(text)
    print('wrote', path, len(text), 'bytes')


# ------------------------------------------------------------------ client patch
def read_dbc(path):
    d = open(path, 'rb').read()
    magic, n, f, rs, ss = struct.unpack('<4s4I', d[:20])
    assert magic == b'WDBC' and rs == f * 4, path
    rows = [list(struct.unpack('<%dI' % f, d[20 + i * rs:20 + (i + 1) * rs])) for i in range(n)]
    return f, rows, bytearray(d[20 + n * rs:])


def add_string(strings, s):
    if not s:
        return 0
    off = len(strings)
    strings += s.encode() + b'\0'
    return off


def write_dbc(f, rows, strings):
    out = bytearray(b'WDBC' + struct.pack('<4I', len(rows), f, f * 4, len(strings)))
    for r in rows:
        out += struct.pack('<%dI' % f, *[v & 0xFFFFFFFF for v in r])
    return bytes(out + strings)


def patch_display(path):
    f, rows, strings = read_dbc(path)
    rows = [r for r in rows if r[0] != UNFINISHED_LOOK]     # rebuilding from an older patch-Z.MPQ
    byid = {r[0]: r for r in rows}
    row = list(byid[QUEL_SERRAR_LOOK])
    row[0] = UNFINISHED_LOOK
    row[22] = BLUE_GLOW
    rows.append(row)
    # helmets that showed the hair through them: the plate helms' usual hair-and-ears covering
    # (HelmetGeosetVisData, male / female, ItemDisplayInfo fields 12-13)
    for display, vis in HELM_HIDES_HAIR.items():
        byid[display][12], byid[display][13] = vis
    # the dungeon clears' Crystal Shards (shards.py)
    import shards
    shards.add_displays(rows, lambda text: add_string(strings, text))
    rows.sort(key=lambda r: r[0])
    return write_dbc(f, rows, strings)


def patch_spells(path):
    f, rows, strings = read_dbc(path)
    assert f == 173, f
    ours = {sp[0] for sp in SPELLS}
    rows = [r for r in rows if r[0] not in ours]          # rebuilding from an older patch-Z.MPQ
    byid = {r[0]: r for r in rows}
    top = max(byid)
    # Execute can be pressed on any target: the server allows it under 20% health or at full rage
    for rank in EXECUTE_RANKS:
        byid[rank][DBC_TARGET_AURA_STATE] = 0
    for sid, changes in SPELL_EDITS.items():
        for k, v in changes.items():
            byid[sid][DBC_FIELD[k]] = v
    for sid, source, name, text, changes in SPELLS:
        assert sid > top, sid
        row = list(byid[source])
        row[0] = sid
        if changes.get('copy_effect1_to_2'):
            for g in EFFECT_GROUPS:
                a = DBC_FIELD['%s1' % g]
                row[a + 1] = row[a]
        for k, v in changes.items():
            if k not in SQL_ONLY:
                row[DBC_FIELD[k]] = v & 0xFFFFFFFF
                if k == 'SpellFamilyFlags':
                    row[DBC_FIELD[k] + 1] = 0           # the flags' upper half
        row[DBC_NAME] = add_string(strings, name)
        row[DBC_RANK] = 0
        row[DBC_DESCRIPTION] = add_string(strings, text)
        row[DBC_TOOLTIP] = add_string(strings, changes['tooltip']) if 'tooltip' in changes else 0
        rows.append(row)
    for sid, text in DESCRIPTION_EDITS.items():
        byid[sid][DBC_DESCRIPTION] = add_string(strings, text)
    aura = DBC_FIELD['EffectApplyAuraName1']
    bp2 = DBC_FIELD['EffectBasePoints2']
    for row in rows:
        if row[aura + 1] == MOUNT_SPEED_AURA and MOUNT_AURA in (row[aura], row[aura + 2]) and row[bp2] in MOUNT_SPEED:
            row[bp2] = MOUNT_SPEED[row[bp2]]
    return write_dbc(f, rows, strings)


def build_patch(display_dbc, spell_dbc, out_mpq, shard_icon=None):
    import mpq
    import shards
    files = {'DBFilesClient\\ItemDisplayInfo.dbc': patch_display(display_dbc),
             'DBFilesClient\\Spell.dbc': patch_spells(spell_dbc)}
    if shard_icon:
        files.update(shards.icon_files(open(shard_icon, 'rb').read()))
    mpq.write_archive(out_mpq, files)
    print('wrote', out_mpq, os.path.getsize(out_mpq), 'bytes')


if __name__ == '__main__':
    write_sql()
    if len(sys.argv) in (4, 5):
        build_patch(*sys.argv[1:])
