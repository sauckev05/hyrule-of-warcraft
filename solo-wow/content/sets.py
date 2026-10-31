"""Zelda of Warcraft armor sets: four dungeon sets (like the Tier 0.5 sets) for levels 20, 30, 40 and
50, each with 2, 3 and 6 piece bonuses that the server applies (ZeldaCommands.cpp, SetBonusType):

    1 crit          % critical strike chance
    2 crit_damage   % more critical strike damage
    3 weapon        % more weapon damage
    4 knockback     % chance a hit pushes the enemy back a step
    5 extra_swing   % chance a hit swings again at once
    6 spin_rage     rage the Spin Attack costs less
    7 heal_on_kill  % of health back on every kill (5% = one heart)
    8 stun          % chance a hit stuns the enemy for 1 second
    9 weapon_flat   flat weapon damage on every hit (shown on the character sheet)

Every piece drops from one dungeon boss (or, given as ((entry, chance), ...), from those enemies). Stats are rolled once (fixed seed) from the set's level.
"""

BONUS_TYPES = {'crit': 1, 'crit_damage': 2, 'weapon': 3, 'knockback': 4, 'extra_swing': 5, 'spin_rage': 6,
               'heal_on_kill': 7, 'stun': 8, 'weapon_flat': 9}

BONUS_TEXT = {
    'crit': 'Increases your chance to get a critical strike by %g%%.',
    'crit_damage': 'Your critical strikes deal %g%% more damage.',
    'weapon': 'Your weapon attacks deal %g%% more damage.',
    'knockback': 'Your melee hits have a %g%% chance to knock the enemy back.',
    'extra_swing': 'Your melee hits have a %g%% chance to swing again at once.',
    'spin_rage': 'Your Spin Attack costs %g less rage.',
    'heal_on_kill': 'Defeating an enemy restores %g%% of your health.',
    'stun': 'Your melee hits have a %g%% chance to stun the enemy for 1 sec.',
    'weapon_flat': '+%g Weapon Damage.',
}

DROP_CHANCE = 100         # % per kill: every piece always drops from its boss

# slot -> (InventoryType, stat budget factor)
SLOTS = {
    'head': (1, 1.0), 'shoulder': (3, 0.75), 'chest': (5, 1.0), 'hands': (10, 0.75), 'legs': (7, 1.0),
    'feet': (8, 0.75), 'tabard': (19, 0.4), 'shield': (14, 0.6), 'waist': (6, 0.75),
}

SETS = [
    dict(id=1, name='Kokiri Garb', level=20, subclass=3, material=5,
         bonuses=[(2, 'crit', 1), (3, 'knockback', 3), (6, 'extra_swing', 3), (6, 'weapon_flat', 5)],
         pieces=[
             # (entry, slot, name, display, boss entry, boss name)
             (190701, 'head', 'Kokiri Coif', 30091, 4275, 'Archmage Arugal (Shadowfang Keep)'),
             (190702, 'shoulder', 'Kokiri Spaulders', 9422, 1696, 'Targorr the Dread (The Stockade)'),
             (190703, 'chest', 'Kokiri Tunic', 13088, 639, 'Edwin VanCleef (The Deadmines)'),
             (190704, 'hands', 'Kokiri Gauntlets', 9414, 646, 'Mr. Smite (The Deadmines)'),
             (190705, 'legs', 'Kokiri Leggings', 9415, 1666, 'Kam Deepfury (The Stockade)'),
             (190706, 'feet', 'Kokiri Boots', 9412, 4278, 'Commander Springvale (Shadowfang Keep)'),
         ]),
    dict(id=2, name='Zora Scale', level=30, subclass=3, material=5,
         bonuses=[(2, 'weapon_flat', 5), (3, 'heal_on_kill', 5), (6, 'crit', 2), (6, 'crit_damage', 10), (6, 'stun', 4)],
         pieces=[
             (190711, 'head', 'Zora Crest', 15290, 4421, 'Charlga Razorflank (Razorfen Kraul)'),
             (190712, 'shoulder', 'Zora Fin Pauldrons', 25764, 3654, 'Mutanus the Devourer (Wailing Caverns)'),
             (190713, 'chest', 'Zora Scale Hauberk', 25763, 7800, 'Mekgineer Thermaplugg (Gnomeregan)'),
             (190714, 'hands', 'Zora Grips', 25761, 6235, 'Electrocutioner 6000 (Gnomeregan)'),
             (190715, 'legs', 'Zora Scale Leggings', 12453, 4832, 'Twilight Lord Kelris (Blackfathom Deeps)'),
             (190716, 'feet', 'Zora Treads', 25760, 4829, "Aku'mai (Blackfathom Deeps)"),
         ]),
    dict(id=3, name='Battlegear of the Scarlet Crusade', level=40, subclass=4, material=6,
         bonuses=[(2, 'crit', 2), (3, 'knockback', 5), (3, 'spin_rage', 10), (6, 'extra_swing', 5),
                  (6, 'crit_damage', 15), (6, 'weapon_flat', 5)],
         pieces=[
             (190721, 'head', 'Helm of the Scarlet Crusade', 4415, 4543, 'Bloodmage Thalnos (Scarlet Monastery Graveyard)'),
             (190722, 'feet', 'Sabatons of the Scarlet Crusade', 28383, 3983, 'Interrogator Vishas (Scarlet Monastery Graveyard)'),
             (190723, 'shoulder', 'Pauldrons of the Scarlet Crusade', 22531, 6487, 'Arcanist Doan (Scarlet Monastery Library)'),
             (190724, 'hands', 'Gauntlets of the Scarlet Crusade', 15816, 3974, 'Houndmaster Loksey (Scarlet Monastery Library)'),
             (190725, 'chest', 'Breastplate of the Scarlet Crusade', 34915, 3975, 'Herod (Scarlet Monastery Armory)'),
             # the old Scarlet Belt (10329) joins the set as the Belt of the Scarlet Crusade, a plate belt
             # now, always dropping from the Armory's last boss like the other pieces
             (10329, 'waist', 'Belt of the Scarlet Crusade', 27951, 3975, 'Herod (Scarlet Monastery Armory)'),
             (190726, 'legs', 'Legplates of the Scarlet Crusade', 34917, 3976, 'Scarlet Commander Mograine (Scarlet Monastery Cathedral)'),
             (190727, 'tabard', 'Tabard of the Crusade', 15817, 3977, 'High Inquisitor Whitemane (Scarlet Monastery Cathedral)'),
             (190728, 'shield', 'Shield of the Crusade', 23446, 4542, 'High Inquisitor Fairbanks (Scarlet Monastery Cathedral)'),
         ]),
    dict(id=4, name='Armor of the Hylian Knight', level=50, subclass=4, material=6,
         bonuses=[(2, 'weapon_flat', 5), (2, 'heal_on_kill', 5), (3, 'crit', 3), (3, 'spin_rage', 15),
                  (6, 'extra_swing', 6), (6, 'knockback', 6), (6, 'crit_damage', 20)],
         pieces=[
             (190731, 'head', "Hylian Knight's Helm", 27186, 7271, "Witch Doctor Zum'rah (Zul'Farrak)"),
             (190732, 'shoulder', "Hylian Knight's Pauldrons", 27378, 12201, 'Princess Theradras (Maraudon)'),
             (190733, 'chest', "Hylian Knight's Breastplate", 27372, 2748, 'Archaedas (Uldaman)'),
             (190734, 'hands', "Hylian Knight's Gauntlets", 27374, 4854, 'Grimlok (Uldaman)'),
             (190735, 'legs', "Hylian Knight's Legplates", 27377, 7267, "Chief Ukorz Sandscalp (Zul'Farrak)"),
             (190736, 'feet', "Hylian Knight's Greaves", 27376, 5710, "Jammal'an the Prophet (Sunken Temple)"),
         ]),
]
