#!/usr/bin/env python3
"""Zelda of Warcraft - Sul'thraze the Lasher, earned instead of combined.

Writes zelda-sql/022_sulthraze.sql, which the server applies to the world database at startup.

  - Zul'Farrak: Chief Ukorz Sandscalp always drops Jang'thraze the Protector. Antu'sul no longer
    drops Sang'thraze the Deflector: he always drops Antu'sul's Hex Idol, which starts The
    Deflector's Echo.
  - The Deflector's Echo: at the summit of Jintha'Alor, by the Vilebranch altar, Zan'thraze the
    Hexblade (level 53 elite) rises when the hero comes near (the core summons him:
    ZeldaCommands.cpp, "Sul'thraze"). Killing him finishes the quest at once; the reward is
    Sang'thraze.
  - Sang'thraze starts The Rite of Sul'thraze: slay Jammal'an the Prophet in the Sunken Temple,
    then, with both blades, use the Altar of Jammal'an where he stood. Ten seconds of ritual call
    the Atal'ai; when they fall, the blades are one - Sul'thraze the Lasher.
  - The two blades no longer combine by themselves (Jang'thraze's Call of Sul'thraze is gone).
  - Sul'thraze's spell (build_mastery.py, SPELL_EDITS 11658): 25% on a hit, 210 Shadow plus all of
    the wielder's spell power, the target deals 15% less damage, and 1000 more Shadow damage over
    15 sec.
"""
import os

from build_content import esc, insert
from build_mastery import CREATURE_COLUMNS, clone

HERE = os.path.dirname(os.path.abspath(__file__))

JANG_THRAZE, JANG_THRAZE_OLD = 11086, 9380
SANG_THRAZE = 9379
SUL_THRAZE = 9372
UKORZ, ANTU_SUL = 7267, 8127
JAMMALAN = 5710

HEX_IDOL = 190540
QUEST_ECHO, QUEST_RITE = 90540, 90541
HEXBLADE = 191200
AMANZASI_GUARD = 2648              # the Hexblade's template: a Vilebranch Aman'zasi Guard, grown up
RITUAL_ALTAR = 191210
RITUAL_ALTAR_GUID = 5400190
# where Jammal'an the Prophet stands in the Sunken Temple; the altar takes his place when he falls
JAMMALAN_SPOT = (109, -426.67749, -85.73757, -88.14072, 3.2114058)
ALTAR_DISPLAY = 327                # the Jintha'Alor altar's stone

ZONE_HINTERLANDS, ZONE_SUNKEN_TEMPLE = 47, 1477


def quest_row(qid, level, min_level, kind, zone, title, details, objectives, request, reward, kills, items,
              reward_item, start_item):
    row = dict(entry=qid, Method=2, ZoneOrSort=zone, MinLevel=min_level, MaxLevel=255, QuestLevel=level,
               Type=kind, RequiredRaces=0, RequiredClasses=0, SuggestedPlayers=0, QuestFlags=0, SpecialFlags=0,
               PrevQuestId=0, NextQuestId=0, NextQuestInChain=0, SrcItemId=start_item,
               SrcItemCount=1 if start_item else 0, Title=title, Details=details, Objectives=objectives,
               OfferRewardText=reward, RequestItemsText=request, EndText='',
               RewOrReqMoney=level * level * 8, RewMoneyMaxLevel=level * 90, DetailsEmote1=1, OfferRewardEmote1=2,
               IncompleteEmote=1, CompleteEmote=0, RewSpellCast=0)
    for n in range(1, 5):
        row['ObjectiveText%d' % n] = ''
        row['ReqItemId%d' % n] = 0
        row['ReqItemCount%d' % n] = 0
        row['ReqCreatureOrGOId%d' % n] = 0
        row['ReqCreatureOrGOCount%d' % n] = 0
    for n, (creature, count) in enumerate(kills, start=1):
        row['ReqCreatureOrGOId%d' % n] = creature
        row['ReqCreatureOrGOCount%d' % n] = count
    for n, (item, count) in enumerate(items, start=1):
        row['ReqItemId%d' % n] = item
        row['ReqItemCount%d' % n] = count
    for n in range(1, 7):
        row['RewChoiceItemId%d' % n] = 0
        row['RewChoiceItemCount%d' % n] = 0
    row['RewItemId1'] = reward_item
    row['RewItemCount1'] = 1
    row['RewRepFaction1'] = 0
    row['RewRepValue1'] = 0
    return row


QUESTS = [
    quest_row(
        QUEST_ECHO, 53, 45, 0, ZONE_HINTERLANDS, "The Deflector's Echo",
        "*The idol is carved with a curved blade and a mountain of stone terraces. Held close, it hisses in "
        "Zandali.*$B$BSang'thraze... the Deflector... not here. Antu'sul's kin gave it to the Vilebranch, "
        "and the Vilebranch gave it to their hexblade, who keeps it at the top of Jintha'Alor, beside the "
        "altar where the high priests make their offerings.$B$BClimb, $N. Climb to the summit of Jintha'Alor "
        "in the Hinterlands, and when Zan'thraze the Hexblade comes for you, take the blade from his hands.",
        "Climb to the summit of Jintha'Alor in the Hinterlands, where the Vilebranch hold their ritual, and slay "
        "Zan'thraze the Hexblade to claim Sang'thraze the Deflector.",
        "The summit, $N. Where the ritual fires burn.",
        "*Zan'thraze's grip loosens, and Sang'thraze slides free, humming.*",
        kills=[(HEXBLADE, 1)], items=[], reward_item=SANG_THRAZE, start_item=HEX_IDOL),
    quest_row(
        QUEST_RITE, 54, 48, 81, ZONE_SUNKEN_TEMPLE, "The Rite of Sul'thraze",
        "*Sang'thraze trembles in your hand, pulled toward something far to the south.*$B$BJang'thraze and "
        "Sang'thraze were one blade once: Sul'thraze the Lasher. The Atal'ai split it with blood magic, so "
        "that no one could wield its rage again, and only that same magic can make it whole.$B$BGo down into "
        "the Sunken Temple in the Swamp of Sorrows. Slay Jammal'an the Prophet, and where he stood, perform the "
        "rite with both blades in hand. The Atal'ai will not let it happen quietly.",
        "Slay Jammal'an the Prophet in the Sunken Temple. Then, with Jang'thraze the Protector and Sang'thraze "
        "the Deflector, use the Altar of Jammal'an to perform the rite, and defeat the Atal'ai who answer it.",
        "Jammal'an's altar, and both blades.",
        "*The two blades draw together, and the rage that split them closes like a wound.*",
        kills=[(JAMMALAN, 1)], items=[(JANG_THRAZE, 1), (SANG_THRAZE, 1)], reward_item=SUL_THRAZE, start_item=0),
]

# Zan'thraze the Hexblade: Mortal Strike, Whirlwind and a Demoralizing Shout, enraged at 30%
# (id, event type, flags, params 1-4, spell, target, comment); target 1 the victim, 0 himself
HEXBLADE_AI = [
    (19120001, 0, 1, (6000, 9000, 10000, 14000), 16856, 1, 'Mortal Strike'),
    (19120002, 0, 1, (12000, 16000, 18000, 22000), 15589, 0, 'Whirlwind'),
    (19120003, 0, 1, (3000, 5000, 25000, 30000), 16244, 0, 'Demoralizing Shout'),
    (19120004, 2, 0, (30, 0, 0, 0), 8599, 0, 'Enrage at 30% HP'),
]


def main():
    out = ['-- Zelda of Warcraft: Sul\'thraze the Lasher, earned (build_sulthraze.py)\n']

    # Zul'Farrak's drops
    out.append('UPDATE `creature_loot_template` SET `ChanceOrQuestChance` = 100, `groupid` = 0 '
               'WHERE `entry` = %d AND `item` = %d;\n' % (UKORZ, JANG_THRAZE))
    out.append('DELETE FROM `creature_loot_template` WHERE `entry` = %d AND `item` IN (%d, %d);\n'
               % (ANTU_SUL, SANG_THRAZE, HEX_IDOL))
    out.append(insert('creature_loot_template', [dict(
        entry=ANTU_SUL, item=HEX_IDOL, ChanceOrQuestChance=100, groupid=0, mincountOrRef=1, maxcount=1,
        condition_id=0, comments="Zelda: The Deflector's Echo")]))

    # the idol that starts the first quest
    out.append('DELETE FROM `item_template` WHERE `entry` = %d;\n' % HEX_IDOL)
    out.append(insert('item_template', [dict(
        entry=HEX_IDOL, **{'class': 12}, subclass=0, name="Antu'sul's Hex Idol", displayid=13703, Quality=1,
        Flags=0, BuyCount=1, BuyPrice=0, SellPrice=0, InventoryType=0, AllowableClass=-1, AllowableRace=-1,
        ItemLevel=48, RequiredLevel=0, maxcount=1, stackable=1, bonding=1, startquest=QUEST_ECHO,
        description='It whispers of a blade carried to the summit of Jintha\'Alor.', Material=4, sheath=0)]))

    # the blades: no combining by hand, Sang'thraze starts the rite, Sul'thraze is epic
    out.append('UPDATE `item_template` SET `spellid_1` = 0, `spelltrigger_1` = 0 WHERE `entry` IN (%d, %d);\n'
               % (JANG_THRAZE, JANG_THRAZE_OLD))
    out.append('UPDATE `item_template` SET `startquest` = %d WHERE `entry` = %d;\n' % (QUEST_RITE, SANG_THRAZE))
    out.append('UPDATE `item_template` SET `Quality` = 4 WHERE `entry` = %d;\n' % SUL_THRAZE)
    # Sul'thraze's 210 Shadow (build_mastery.py, SPELL_EDITS 11658) grows by all of the wielder's spell power
    out.append('UPDATE `spell_template` SET `EffectBonusCoefficient1` = 1.0 WHERE `Id` = 11658;\n')

    # Zan'thraze the Hexblade
    out.append(clone('creature_template', 'Entry', HEXBLADE, AMANZASI_GUARD, CREATURE_COLUMNS))
    out.append('UPDATE `creature_template` SET `Name` = %s, `SubName` = %s, `MinLevel` = 53, `MaxLevel` = 53, '
               '`Rank` = 1, `Scale` = 1.5, `MinLevelHealth` = 15000, `MaxLevelHealth` = 15000, '
               '`DamageMultiplier` = 2.0, `LootId` = 0, `PickpocketLootId` = 0, `SkinningLootId` = 0, '
               '`MinLootGold` = 2500, `MaxLootGold` = 4000, `AIName` = \'EventAI\', `ScriptName` = \'\' '
               'WHERE `Entry` = %d;\n' % (esc("Zan'thraze the Hexblade"), esc("Keeper of Sang'thraze"), HEXBLADE))
    out.append('DELETE FROM `creature_ai_scripts` WHERE `creature_id` = %d;\n' % HEXBLADE)
    out.append(insert('creature_ai_scripts', [dict(
        id=sid, creature_id=HEXBLADE, event_type=etype, event_inverse_phase_mask=0, event_chance=100,
        event_flags=flags, event_param1=p[0], event_param2=p[1], event_param3=p[2], event_param4=p[3],
        event_param5=0, event_param6=0, action1_type=11, action1_param1=spell, action1_param2=target,
        action1_param3=0, action2_type=0, action2_param1=0, action2_param2=0, action2_param3=0, action3_type=0,
        action3_param1=0, action3_param2=0, action3_param3=0, comment="Zan'thraze the Hexblade - " + text)
        for sid, etype, flags, p, spell, target, text in HEXBLADE_AI]))

    # the Altar of Jammal'an: a goober over his spot, used for the rite (core: ZeldaGameObjectUse)
    m, x, y, z, o = JAMMALAN_SPOT
    out.append('DELETE FROM `gameobject_template` WHERE `entry` = %d;\n' % RITUAL_ALTAR)
    out.append('INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `faction`, `flags`, `size`, '
               '`data0`, `data1`) VALUES (%d, 10, %d, %s, 0, 0, 0.8, 0, 0);\n'
               % (RITUAL_ALTAR, ALTAR_DISPLAY, esc("Altar of Jammal'an")))
    out.append('DELETE FROM `gameobject` WHERE `id` = %d OR `guid` = %d;\n' % (RITUAL_ALTAR, RITUAL_ALTAR_GUID))
    import math
    out.append('INSERT INTO `gameobject` (`guid`, `id`, `map`, `spawnMask`, `position_x`, `position_y`, `position_z`, '
               '`orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecsmin`, '
               '`spawntimesecsmax`) VALUES (%d, %d, %d, 1, %.5f, %.5f, %.5f, %.7f, 0, 0, %.7f, %.7f, 25, 25);\n'
               % (RITUAL_ALTAR_GUID, RITUAL_ALTAR, m, x, y, z, o, math.sin(o / 2), math.cos(o / 2)))

    # the two quests, started by items (no giver) and finished by the core (no ender)
    out.append('DELETE FROM `quest_template` WHERE `entry` IN (%d, %d);\n' % (QUEST_ECHO, QUEST_RITE))
    out.append('DELETE FROM `creature_questrelation` WHERE `quest` IN (%d, %d);\n' % (QUEST_ECHO, QUEST_RITE))
    out.append('DELETE FROM `creature_involvedrelation` WHERE `quest` IN (%d, %d);\n' % (QUEST_ECHO, QUEST_RITE))
    out.append(insert('quest_template', QUESTS))

    path = os.path.join(HERE, 'zelda-sql', '022_sulthraze.sql')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(out))
    print('wrote', path, os.path.getsize(path), 'bytes')


if __name__ == '__main__':
    main()
