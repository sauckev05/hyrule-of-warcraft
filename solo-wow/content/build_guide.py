#!/usr/bin/env python3
"""Zelda of Warcraft - Navi's gameplay guide, a beginner's guide behind her third option.

Writes zelda-sql/023_navi_guide.sql: one npc_text page per topic. The menu itself (the topics'
titles and their order) is Navi's gossip script, zelda_companions.cpp (NAVI_GUIDE), which shows
page GUIDE_TEXT_BASE + n for topic n (0 is the guide's own greeting).

Text markers: $N the hero's name, $B a line break.
"""
import os

from build_content import insert, npc_text

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE_TEXT_BASE = 900620

PAGES = [
    # 0: the guide's greeting
    "Hey! Listen! You want to learn how everything works? I know LOTS of things!$B$BPick something and I'll "
    "explain it. You can always come back and ask again.",

    # 1: controls
    "Your keys, $N! The number pad's 1-9 do the same thing.$B$B"
    "1 - Sword. Tap to swing (three swings make a combo). Hold, then let go, for your stance's charge attack.$B"
    "2 - Bow, gun or crossbow. Hold to charge a Charged Shot.$B"
    "3 - Shield. Hold to raise it. Without a shield you hold your weapon up to parry.$B"
    "4 - Boomerang.$B"
    "5 - Roll forward. Shift+Q and Shift+E roll to the sides, Shift+S is a backflip.$B"
    "6 - Potion slot. Right-click a healing or mana potion to put it there.$B"
    "7 - Mount slot. Right-click a mount to put it there.$B"
    "8 - Your character and all your bags.$B"
    "9 - The Subscreen: spellbook, talents, quest log and menu. Left and Right turn the page.$B$B"
    "Tap Shift to lock on to an enemy, and tap it again to let go. Q and E change your stance. M opens the map.",

    # 2: combat
    "Fighting! My favorite part. Well, watching it.$B$B"
    "Swing with 1. Your third swing in a row is a special strike. Hold 1 and let go when the bar turns green "
    "for a charge attack - the Spin Attack costs 50 rage.$B$B"
    "Rage comes from hitting and being hit. You need it for your charge attacks.$B$B"
    "Strong enemies - elites, rares and bosses - wind up a Heavy Blow or a Charged Bolt. Watch the orange bar "
    "over their health that says BLOCK! Raise your shield (3) to block it, and a blocked Heavy Blow leaves "
    "them staggered. Parry it and you only take half. Or roll away!$B$B"
    "Rolling (5) dodges EVERYTHING while you're in the air, but only from the ground.$B$B"
    "The boomerang (4) stops whatever an enemy is casting, any enemy, and stuns or disarms it. It flies "
    "30 yards and is ready 3 seconds after it hits.$B$B"
    "A Charged Shot (hold 2) does double damage and always crits. You stand still while you draw.",

    # 3: stances and weapons
    "Warriors fight in three stances. Q and E switch between them.$B$B"
    "Battle Stance - any weapon. Your charge attack is the Spin Attack, which hits everyone around you. With "
    "two weapons it hits twice as many times.$B$B"
    "Defensive Stance - a one-handed weapon and a shield (taking the stance picks them from your bags). Your "
    "charge attack is Shield Slam: it hits as hard as your shield's armor, then stuns enemies in front and "
    "silences their spells for 2 seconds.$B$B"
    "Berserker Stance - a two-handed weapon (picked from your bags too). Your charge attack is Leaping "
    "Strike: twice your attack power, through all armor, on every enemy in front. Each one that lands gives "
    "Berserker's Fury, up to 10 stacks of 10% more attack power and spell power.$B$B"
    "All one-handed weapons swing every 2.70 seconds and all two-handers every 4.00, so pick by damage!",

    # 4: levels and experience
    "You grow stronger by gaining experience - the purple bar at the bottom.$B$B"
    "You get experience from finishing quests and defeating enemies. Fill the bar and you reach the next "
    "level: more health, better stats, and a talent point from level 10.$B$B"
    "Enemies inside dungeons and raids give half the experience, but they drop much better treasure.$B$B"
    "Enemies far below your level give little or nothing, so keep moving to new places!$B$B"
    "Worthy foes sometimes drop a Piece of Heart. Bring me four and you'll get a whole new heart. That "
    "means you get tougher!",

    # 5: stats
    "Your stats! Press 8 - the Combat Stats panel sits beside your character sheet.$B$B"
    "Strength - attack power: harder hits with every weapon and charge attack.$B"
    "Agility - more critical strikes, dodges and armor.$B"
    "Stamina - more health.$B"
    "Intellect - here it gives spell power, so your healing and magic hit harder.$B"
    "Spirit - you recover health faster.$B"
    "Armor - less damage from physical blows.$B$B"
    "Spell power also makes the magic in your gear stronger: every spell an item casts, like a weapon's "
    "chance on hit or a trinket's use, gets 45% of it.$B$B"
    "Critical strikes hit for double. Your hit chance decides how often you miss.",

    # 6: talents
    "Talents make you special!$B$B"
    "From level 10 you get one talent point every level. Press 9 and turn to Talents to spend them.$B$B"
    "Each tree has rows. Put 5 points into a tree to open its next row. Read a talent's tooltip to see what "
    "every point does.$B$B"
    "Some favorites: Toughness makes your shield stronger, and your Shield Slam with it. Bleeding Edge makes "
    "enemies bleed. Deep Wounds bleeds them when you crit. The weapon specializations give counterattacks, "
    "enrages and a Shield Cleave, depending on what you hold.$B$B"
    "Changed your mind? A class trainer can reset your talents for some gold.",

    # 7: inventory and equipping
    "Press 8 to open your character and all your bags at once.$B$B"
    "To put something on, right-click it in your bag, or drag it onto its slot on your character. Hover over "
    "an item in your bags to see what you're wearing in that slot next to it.$B$B"
    "Grey junk and plain white gear are sold for you at vendors. Sold something by mistake? A pawnbroker buys "
    "it back until you log out.$B$B"
    "You carry up to 10 of each potion, and potions have no cooldown. Mana potions turn into a shield that "
    "absorbs damage! Right-click one to put it on key 6.$B$B"
    "Right-click a mount to put it on key 7. Swinging your sword while riding gets you off.$B$B"
    "Loot is picked up for you automatically.",

    # 8: items and weapon types
    "Items come in colors: grey is junk, white is common, green is uncommon, blue is rare, purple is epic, "
    "and orange is legendary!$B$B"
    "One-handed weapons: swords, axes, maces, daggers and fist weapons. Two-handed weapons: swords, axes, "
    "maces, polearms and staves. Ranged weapons on key 2: bows, guns, crossbows and thrown weapons.$B$B"
    "You can hold a one-hander with a shield, two one-handers at once, or one big two-hander. Each stance "
    "wants its own.$B$B"
    "Wear several pieces of the same armor set to get set bonuses - the tooltip lists them.$B$B"
    "Some weapons have a 'Chance on hit' or 'Use' effect. Those grow with your spell power.$B$B"
    "Clear a whole dungeon and you get its Crystal Shard. Collect them - someone might need them one day!",

    # 9: dungeons and raids
    "Dungeons are the best adventures!$B$B"
    "Ask any innkeeper for the dungeon list and they'll send you to the dungeon's meeting stone.$B$B"
    "Inside, the bar under the minimap shows how many enemies you've defeated. Click it to find the ones "
    "still standing. Defeat all of them and you get the dungeon's Crystal Shard!$B$B"
    "Enemies you defeat stay defeated, and the dungeon keeps waiting for you until you ask me to reset "
    "everything.$B$B"
    "If you fall inside a dungeon, you come back at its entrance.$B$B"
    "Press M inside for the dungeon map. And watch for those Heavy Blows!",

    # 10: getting around
    "Getting around Azeroth!$B$B"
    "Run without stopping for 15 seconds and you start sprinting, twice as fast. You swim fast too, until "
    "you run out of breath.$B$B"
    "Ride a mount (key 7) for long trips, or take a flight master's gryphon or wind rider between towns.$B$B"
    "Every town is friendly to you, Alliance and Horde alike, so you can go anywhere and talk to anyone.$B$B"
    "The Kirin Tor mages in Stormwind's Wizard's Sanctum and outside Dalaran send you between the two.",

    # 11: Navi
    "That's me! Navi!$B$B"
    "Once you wear my light, I follow you everywhere. While you fight, I heal a tenth of your health every "
    "10 seconds.$B$B"
    "If you fall, my light brings you back with some of your health and mana. After that I need 5 minutes "
    "to rest before I can do it again.$B$B"
    "I can also reset every dungeon and raid for you, so their enemies come back for another try.$B$B"
    "And I give you errands along the way. Hey! Listen! They're important!",
]


def main():
    texts = [npc_text(GUIDE_TEXT_BASE + n, text) for n, text in enumerate(PAGES)]
    ids = ', '.join(str(t['ID']) for t in texts)
    out = ['-- Zelda of Warcraft: Navi\'s gameplay guide (build_guide.py)\n',
           'DELETE FROM `npc_text` WHERE `ID` IN (%s);\n' % ids,
           insert('npc_text', texts)]
    path = os.path.join(HERE, 'zelda-sql', '023_navi_guide.sql')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(out))
    print('wrote', path, os.path.getsize(path), 'bytes,', len(texts), 'pages')


if __name__ == '__main__':
    main()
