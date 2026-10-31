# Zelda of Warcraft - the companions' story: who they are, where they are, and every quest.
# build_content.py turns this into zelda-sql/001_companions.sql, which the server applies to the
# world database by itself at startup.
#
# Text markers the game fills in: $N the hero's name, $C class, $R race, $B a line break.

# ------------------------------------------------------------------------------------ people
# Story characters who start the chains. (entry, name, subname, display, faction, equipment,
# level, (map, x, y, z, orientation), greeting)
STORY_NPCS = [
    (190001, 'Bishop Aldous Grey', 'Cathedral of Light', 7008, 12, 0, 55,
     (0, -8529.0, 856.5, 106.6, 3.7),
     "These old bones have watched over the Cathedral for sixty winters, $N. "
     "Lately they have been watching the door, hoping a certain young acolyte walks back through it."),
    (190002, 'Widow Carrow', None, 1692, 12, 238, 30,
     (0, -10512.5, 1048.5, 60.6, 4.9),
     "Sentinel Hill is safe enough, they say. I said that about Moonbrook once, before the Defias came."),
    (190003, 'Elder Sentinel Ilthara', 'Sentinel Army', 2865, 80, 2930, 45,
     (1, 9851.0, 1030.0, 1304.9, 2.0),
     "Ishnu-alah, $N. Forgive me if I seem distracted - my niece has a talent for vanishing."),
    (190004, 'Elder Grimtusk', 'Earthen Ring', 3846, 29, 3464, 50,
     (1, 291.0, -4728.0, 13.2, 2.5),
     "The spirits of Durotar are restless, young one. And so is a certain stubborn girl I once taught."),
    (190005, 'Gravekeeper Hollis', None, 1582, 68, 1568, 30,
     (0, 2265.5, 247.0, 33.7, 3.4),
     "Brill's dead keep me busy. Brill's living keep me nervous. And there is one who is... in between."),
]

# The four companions. Each has a spawn per chapter of her story; all share the companion script.
# (entry, chapter name, level, (map, x, y, z, o), wander yards, show (quest, state), hide (quest, state))
# state 0 = quest taken or done, 1 = quest rewarded; quest 0 = always.
COMPANIONS = {
    'lyra': dict(
        name='Lyra Ashford', subname='Acolyte of the Light', display=1295, equipment=6267, unit_class=8,
        greeting="Oh! H-hello. I'm Lyra. Sorry, I was... reading. I'm always reading. Did you need something?",
        about="I'm an acolyte of the Cathedral. I love old churches - every one of them has a story carved into "
              "its stones, if you're patient enough to read it.$B$BPeople say I'm shy. I just... think before I "
              "speak. And then I think some more. And then the moment's gone.$B$BLately I keep wondering about "
              "things I shouldn't. Like why a noble lady at court gets letters sealed with black dragon wax.",
        stages=[
            (190101, 'Captive', 18, (36, -64.5, -853.0, 16.9, 2.0), 0, (0, 1), (90102, 1)),
            (190102, 'Cathedral of Light', 20, (0, -8552.5, 832.5, 106.6, 2.2), 2, (90102, 1), (90103, 1)),
            (190103, 'Darkshire', 28, (0, -10548.5, -1112.5, 31.5, 3.0), 2, (90103, 1), (90115, 0)),
            (190104, "Morgan's Vigil", 55, (0, -8372.5, -2755.5, 187.1, 4.0), 2, (90115, 0), (90109, 0)),
            (190105, 'Stormwind Keep', 60, (0, -8445.5, 333.0, 122.6, 5.4), 0, (90109, 0), (0, 1)),
        ]),
    'faelin': dict(
        name='Faelin Swiftbreeze', subname='Huntress', display=9937, equipment=10604, unit_class=2,
        greeting="Hey! Hi! You look like someone who goes places. I go places too. Want to go places together?",
        about="Faelin Swiftbreeze, huntress, explorer, and - according to my aunt - professional worry-maker!$B$B"
              "Ten thousand years my people spent under the same trees. I want to see EVERYTHING before the next "
              "ten thousand.$B$BBut lately... something's off. Darkshore's water whispers. The cultists on the beach "
              "talk about gods who sleep under the sand. I want to know what they're dreaming about.",
        stages=[
            (190201, 'Auberdine', 15, (1, 6584.5, 489.0, 8.3, 2.5), 3, (0, 1), (90114, 1)),
            (190202, 'Astranaar', 30, (1, 2791.5, -296.0, 107.2, 5.5), 3, (90114, 0), (90211, 0)),
            (190203, 'Cenarion Hold', 58, (1, -6748.5, 827.0, 57.4, 3.5), 3, (90211, 0), (0, 1)),
        ]),
    'durza': dict(
        name='Durza Stormcaller', subname='Shaman of the Earthen Ring', display=3897, equipment=4049, unit_class=2,
        greeting="What. ...Sorry. Long day. Long YEAR. What do you want?",
        about="I'm Durza. My mother was the finest fire-speaker in Durotar. A fire spirit went mad and took her, "
              "and the elders said 'the elements are in balance'. BALANCE.$B$BNow the fire won't listen to me, the "
              "earth groans in Desolace and something under Blackrock Mountain is screaming. Everyone says I'm "
              "too angry.$B$B...Maybe. But someone has to find out who is making the elements suffer. And hit them.",
        stages=[
            (190301, 'Razor Hill', 12, (1, 282.5, -4720.5, 13.3, 5.0), 3, (0, 1), (90416, 1)),
            (190302, 'Shadowprey Village', 50, (1, -1588.5, 3076.0, 49.0, 3.0), 3, (90416, 0), (90304, 0)),
            (190303, 'Kargath', 57, (0, -6682.0, -2166.0, 244.2, 2.3), 3, (90304, 0), (0, 1)),
        ]),
    'vesper': dict(
        name='Vesper Duskhollow', subname='Forsaken Warlock', display=10550, equipment=11055, unit_class=8,
        greeting="Hello, living thing. Or not-quite-living thing. I don't judge. Much.",
        about="Vesper. I died in Lordaeron when the plague came, and I woke up in a field of corpses, which I "
              "found... clarifying.$B$BThe Scourge took everything. My family, my name, my favorite cloak. I study "
              "the shadows because they are the only thing the Lich King cannot command.$B$BOne day I will stand "
              "in his floating necropolis and tell his lieutenant exactly what I think of him. It will be a long speech.",
        stages=[
            (190401, 'Brill', 10, (0, 2258.0, 240.0, 33.7, 0.5), 3, (0, 1), (90211, 1)),
            (190402, 'The Sepulcher', 40, (0, 548.0, 1590.5, 130.1, 0.8), 2, (90211, 0), (90404, 0)),
            (190403, 'The Bulwark', 56, (0, 1764.5, -726.5, 60.0, 2.5), 2, (90404, 0), (90405, 0)),
            (190404, "Light's Hope Chapel", 60, (0, 2307.5, -5352.5, 91.7, 2.4), 2, (90405, 0), (0, 1)),
        ]),
}

# Creatures that are no longer in the world: Elara Starfall (190701) is now a real character the
# playerbots AI plays (ZeldaEnsureElaraBot, llm_character_card.txt), not a creature.
RETIRED_ENTRIES = [190701]
# Quests no longer in the story: Faelin's Sunken Temple chapter (90204) is Durza's now (90310).
RETIRED_QUESTS = [90204]

# ------------------------------------------------------------------------------------ items
# Quest items: (entry, name, display, description, dropped by creature)
QUEST_ITEMS = [
    (190501, 'Black-Sealed Ledger', 3020, 'Defias accounts, sealed with black dragon wax.', 639),
    (190502, 'Sealed Courtly Missive', 7233, 'Lady Prestor\'s seal. Addressed to Lord Ello Ebonlocke, Darkshire.', 0),
    (190503, "Gath'Ilzogg's Orders", 3411, 'Orders written in a fine, noble hand. In Orcish.', 334),
    (190504, 'Prestor Correspondence', 3020, 'Letters between the Scarlet Crusade and "a friend at court".', 3977),
    (190505, "Wyrmthalak's Dispatch", 3411, '"The Lady\'s plans in Stormwind proceed. The whelps must be ready."', 9568),
    (190506, 'Blood of the Black Champion', 16325, 'Still warm. It smells of smoke and lies.', 10363),
    (190511, 'Whispering Idol', 13703, 'A small black idol. If you hold it to your ear, it hums.', 2339),
    (190512, 'Nightmare Shard', 19223, 'A sliver of a green dragon\'s corrupted dream.', 5709),
    (190521, 'Searing Blade Pact', 3411, 'A pact with something that lives in the fire below Orgrimmar.', 11520),
    (190522, 'Corrupted Earth Shard', 13703, 'The earth itself, sick and weeping.', 12201),
    (190523, "Thaurissan's Brand", 9116, 'A brand of living fire, still burning with the Firelord\'s favor.', 9019),
    (190531, "Arugal's Grimoire", 7264, 'Arugal\'s notes on calling beings from beyond death.', 4275),
    (190532, 'Phylactery Fragment', 7277, 'Part of a lich\'s phylactery. It is very cold.', 7358),
    # Linken's sword (the end of this file): what It's Dangerous to Go Alone gives, and what the dungeon
    # shards make of it
    (190533, 'Hilt of the Sword of Mastery', 34171, 'All that is left of Linken\'s sword. It is warm, as if it '
             'were waiting.', 0),
    (190534, 'Shard-Bound Hilt', 34170, 'The hilt, bound with the light of every dungeon. It hums like a held '
             'breath.', 0),
]

# ------------------------------------------------------------------------------------ quests
# Each quest: id, level, min level, type ('' normal, 'dungeon', 'raid'), zone, giver, turn-in,
# title, details, objectives, request (while in progress), reward text, kills [(creature,count,text)],
# items [(item,count)], start item, reputation (faction, value), extra reward item
Q = []
def quest(**kw):
    Q.append(kw)

# =========================================================== LYRA - the Lady in the Keep
quest(id=90101, level=18, min=14, kind='', zone=1519, giver=190001, ender=190002,
      title='Where Has Lyra Gone?',
      details="You have kind eyes, $N. Perhaps you will help an old man.$B$BThree weeks ago a young acolyte of "
              "ours, Lyra Ashford, went to Westfall to bring bread and prayers to the farmers the Defias left "
              "homeless. She is a shy thing - she would sooner read a hymnal than speak to a stranger - but her "
              "heart is braver than she knows.$B$BShe has not come home.$B$BHer last letter was posted from Sentinel "
              "Hill, where she lodged with a widow named Carrow. Find Widow Carrow. Ask her what became of our Lyra.",
      objectives="Speak with Widow Carrow at Sentinel Hill in Westfall.",
      request=None,
      reward="You're asking after Lyra? Oh, thank the Light somebody is. She was such a dear - always "
             "apologizing, always curious about everything...$B$BSit down. You'll want to hear this sitting down.",
      kills=[], items=[], rep=(72, 150))

quest(id=90102, level=21, min=17, kind='dungeon', zone=40, giver=190002, ender=190001,
      title='The Ship in the Dark',
      details="Lyra kept asking questions. Where the Defias got their coin, who bought their stolen iron, why "
              "their leaders wore such fine boots. Curious little thing.$B$BOne night she followed a cart of "
              "stolen goods to Moonbrook. The Defias took her. A farmhand saw them drag her down into the old "
              "mine beneath Moonbrook - the Deadmines, where VanCleef keeps his ship.$B$BGet her out, $N. And if "
              "you find whatever she was so curious about, bring it back to the Bishop. She'd want him to know.",
      objectives="Free Lyra Ashford from the Deadmines and recover the Black-Sealed Ledger from Edwin VanCleef. "
                 "Return to Bishop Aldous Grey in the Cathedral of Light.",
      request="Is she... is our Lyra safe?",
      reward="She is alive. Light be praised, she is alive - she came to me this morning, soot on her robes, "
             "trembling like a leaf and talking a mile a minute.$B$BAnd this ledger... these are payments, $N. "
             "Large ones. And the seal is black dragon wax. Lyra will want to speak with you. She is in the "
             "Cathedral now, pretending to read.",
      kills=[(190101, 1, 'Lyra Ashford freed')], items=[(190501, 1)], rep=(72, 250))

quest(id=90103, level=22, min=18, kind='', zone=1519, giver=190102, ender=1749,
      title='A Name in the Ledger',
      details="Y-you're the one who... thank you. Really. I don't know how to say it properly. I was so scared "
              "down there.$B$BBut I heard things. The Defias kept talking about 'the Lady in the Keep' who pays "
              "for everything. And the ledger is sealed with black dragon wax... I looked it up. Three times.$B$B"
              "I'm probably wrong. I'm usually wrong. But Lady Katrana Prestor advises the King, and she knows "
              "every noble seal in the kingdom. Could you... ask her about it? I'm too nervous to go to the Keep.",
      objectives="Ask Lady Katrana Prestor in Stormwind Keep about the black dragon seal.",
      request=None,
      reward="A black wax seal? How very... theatrical. Bandits do love their little affectations.$B$BYou were "
             "right to bring this to me, $N. The court cannot have common thugs playing at nobility. Leave the "
             "ledger with me. I shall see to it personally.$B$B*Her smile does not reach her eyes.*",
      kills=[], items=[], rep=(72, 150))

quest(id=90104, level=24, min=20, kind='', zone=1519, giver=1749, ender=190103,
      title='A Favor for the Court',
      details="You have been useful, $N. I reward usefulness.$B$BTake this missive to Lord Ello Ebonlocke in "
              "Darkshire. It concerns the... security of the roads. Do not open it - the seal is the King's own, "
              "and breaking it would be treason.$B$BA small errand for a great kingdom. Off you go.",
      objectives="Deliver the Sealed Courtly Missive to Darkshire in Duskwood.",
      request="Did you... did you bring it here? To Darkshire?",
      reward="$N! I - I followed you. I'm sorry! I couldn't stop thinking about the seal, so I came to Darkshire "
             "to pray at the chapel and wait.$B$BLet me see that letter. Please.$B$B...The wax is fake. It's not "
             "the King's seal at all. And it isn't addressed to Lord Ebonlocke. It's addressed to someone called "
             "Gath'Ilzogg. In Orcish.",
      kills=[], items=[(190502, 1)], start_item=190502, rep=(72, 150))

quest(id=90105, level=27, min=22, kind='', zone=10, giver=190103, ender=190103,
      title="Ink Like Dragon's Blood",
      details="Gath'Ilzogg is the Blackrock warlord camped at Stonewatch Keep in Redridge. Why would a lady of "
              "the court write to a Blackrock orc? Unless... unless she isn't really a lady at all.$B$BI know how "
              "that sounds. I'm just an acolyte. But please - Gath'Ilzogg will have more letters. If we find them, "
              "maybe someone will believe me.$B$BI'll stay here and pray for you. I'm, um, very good at praying.",
      objectives="Slay Gath'Ilzogg at Stonewatch Keep in Redridge and bring his orders to Lyra in Darkshire.",
      request="Did you find anything? Anything at all?",
      reward="The handwriting... it's the same as the missive. The same flourishes, the same fine ink. She "
             "gives orders to the Blackrock clan.$B$BI'm scared, $N. But I'm more scared of what happens if "
             "nobody does anything.",
      kills=[(334, 1, None)], items=[(190503, 1)], rep=(72, 250), next=90112)

quest(id=90112, level=26, min=22, kind='dungeon', zone=717, giver=190103, ender=190103, prev=90105,
      title='The Riot in the Stockade',
      details="Gath'Ilzogg's orders mention 'the friend in the Stockade' three times. Three! I underlined them.$B$B"
              "The prisoners in Stormwind's Stockade have taken the whole prison. The guards say it's just a riot, "
              "but the riot is led by Bazil Thredd - a Defias lieutenant who was supposed to hang a month ago. "
              "Somebody kept him alive. Somebody with a very fine pen.$B$BPlease, $N. Put an end to Bazil Thredd. "
              "If the Lady's friends can open a prison from the inside, nobody in Stormwind is safe.",
      objectives="Slay Bazil Thredd in the Stormwind Stockade, then return to Lyra in Darkshire.",
      request="Did he say who freed him? People always say who freed them. Don't they?",
      reward="He had a pardon in his pocket. A royal pardon, $N, signed for the King - in the same flowing hand "
             "as the missive.$B$BShe can make criminals walk free with a stroke of her pen. And no one asks "
             "why.$B$B*Lyra smooths the paper with trembling fingers.* I'm keeping this. Evidence. Stone by stone.",
      kills=[(1716, 1, None)], items=[], rep=(72, 250), next=90113)

quest(id=90113, level=28, min=22, kind='dungeon', zone=209, giver=190103, ender=190103, prev=90112,
      title='The Wolves of Silverpine',
      details="I wrote to every scholar I could think of about black dragons who wear human faces. Only one "
              "ever wrote back: Archmage Arugal, before he went mad in Shadowfang Keep.$B$BHe said the Kirin "
              "Tor knew of 'a lady of the black brood' and that his notes would prove it. Then the worgen came, "
              "and he never wrote again.$B$BI know Silverpine is terribly far. And full of wolves. And Forsaken. "
              "But if Arugal's proof is still in that keep... please, $N. Stop him, and bring back whatever he knew.",
      objectives="Slay Archmage Arugal in Shadowfang Keep, then return to Lyra in Darkshire.",
      request="I read his letter again. He signed it 'the Wolf Mage'. That should have worried me sooner.",
      reward="'The Lady of the Black Brood takes the shape of a noblewoman. She will seek the ear of the boy "
             "king.' Written ten years ago, $N. TEN YEARS.$B$BI can't do this with books alone anymore. We need "
             "help - someone who knows the old, hidden things of this world.$B$BI think I know who to ask.",
      kills=[(4275, 1, None)], items=[], rep=(72, 250), next=90114)

quest(id=90114, level=30, min=30, kind='', zone=331, giver=190103, ender=190202, prev=90113,
      title='A Huntress in Ashenvale',
      details="When I was little the Cathedral sent me to Darnassus to copy hymns. A night elf girl there - Faelin "
              "Swiftbreeze - kept dragging me out of the library to chase owls. She said the world was a puzzle "
              "box and I was the only one who read the instructions.$B$BShe wrote to me last month from Astranaar. "
              "She hears whispers in idols and nightmares in the water, and nobody believes her either.$B$BWe "
              "should look out for each other, the people nobody believes. Go to Ashenvale and find her, $N. Tell "
              "her Lyra sent you. And... tell her I still have the owl feather.",
      objectives="Find Faelin Swiftbreeze in Astranaar, in Ashenvale.",
      request=None,
      reward="LYRA sent you? Little Lyra, who hid behind the hymn books? Ha! I KNEW she'd get into trouble "
             "eventually!$B$B*Faelin takes the letter and her grin fades as she reads.*$B$BBlack dragons in "
             "Stormwind... and whispers here in the woods. Okay. Okay! If you're helping Lyra, you're helping me. "
             "I've got a LOT of creepy things for us to look at.",
      kills=[], items=[], rep=(69, 250), next=90208)

quest(id=90106, level=38, min=32, kind='dungeon', zone=10, giver=190103, ender=190103, prev=90114, next=90115,
      title='Sermons of the Scarlet',
      details="I've been reading everything about the old black dragons. The Brood of Deathwing. They can take "
              "the shape of mortals, $N. They whisper in courts. They turn the faithful against each other.$B$B"
              "The Scarlet Crusade has a great cathedral in Tirisfal - I always dreamed of seeing it. But Bishop "
              "Grey says their High Inquisitor, Whitemane, receives money from 'a friend at court'.$B$BIf the same "
              "friend pays the Crusade AND the Blackrock... Please, go to the Scarlet Monastery. Find out.",
      objectives="Defeat High Inquisitor Whitemane in the Scarlet Monastery Cathedral and bring the Prestor "
                 "Correspondence to Lyra in Darkshire.",
      request="I lit a candle for you every night. It's a little silly. I did it anyway.",
      reward="'To our faithful friend at court, the Lady K.' It's her. It's really her.$B$BShe pays the Crusade "
             "to hunt the living and the Blackrock to raid the roads. She wants Stormwind weak.$B$BI need to think. "
             "And you need to grow stronger, $N - much stronger. What we're facing doesn't fall to one brave "
             "afternoon.$B$BCome back to me when the world has tested you. I'll keep reading.",
      kills=[(3977, 1, None)], items=[(190504, 1)], rep=(72, 350))

quest(id=90115, level=54, min=50, kind='', zone=46, giver=190103, ender=9562, prev=90106,
      title='The Dragonkin Menace',
      details="You've grown so strong, $N. I can see it from across the square.$B$BI've had letters from Morgan's "
              "Vigil, in the Burning Steppes. Helendis Riverhorn - a night elf who studies dragonkin - says black "
              "dragons are gathering at Blackrock Spire in numbers nobody has seen since the Second War. And she "
              "says they take their orders from Stormwind.$B$BShe's the first person who has ever written that "
              "sentence besides me.$B$BGo to her. Help her. I'm coming too - I'll meet you at the Vigil. I'm "
              "done hiding in chapels.",
      objectives="Speak with Helendis Riverhorn at Morgan's Vigil in the Burning Steppes.",
      request=None,
      reward="An acolyte from Darkshire wrote to me months ago about a lady in the Keep. I thought she was mad. "
             "Now the dragonkin are massing on the Spire and I do not think so anymore.$B$BYou have come at the "
             "right time, $N. There is a great deal to do, and almost no one I trust to do it.",
      kills=[], items=[], rep=(72, 250), next=4182)

quest(id=90107, level=55, min=50, kind='dungeon', zone=46, giver=190104, ender=190104, prev=90115,
      title='Brood of the Black Spire',
      details="You came! I... I hoped you would. I've grown a little braver out here. The Vigil's scouts let me "
              "help in the infirmary.$B$BI've been reading Scarlet letters for months. They all point to "
              "Blackrock Spire. Overlord Wyrmthalak commands the orcs of the lower spire, and he reports to "
              "someone in Stormwind.$B$BBring me his dispatches, $N. Every piece we find is a stone in the wall "
              "of truth.",
      objectives="Slay Overlord Wyrmthalak in Lower Blackrock Spire and bring his dispatch to Lyra at "
                 "Morgan's Vigil.",
      request="Please be careful in the Spire. Dragons don't forgive.",
      reward="'The Lady's plans in Stormwind proceed. The whelps must be ready.'$B$BWhelps. Dragon whelps. "
             "$N... she's not a lady who works with dragons. She IS a dragon.$B$B*Lyra sits down very suddenly.*",
      kills=[(9568, 1, None)], items=[(190505, 1)], rep=(529, 250))

quest(id=90108, level=59, min=55, kind='dungeon', zone=46, giver=190104, ender=190104, next=0,
      title="The Champion's Blood",
      details="The old books say a black dragon's disguise can be broken by the blood of her own champion. "
              "In Upper Blackrock Spire, General Drakkisath commands the Black Dragonflight's guard.$B$BIf we "
              "bring his blood back, I can make a ward. A ward that shows what someone truly is.$B$BI'm going to "
              "Stormwind with it. I'm going to stand in front of the King. Me. Lyra Ashford. Who used to hide in "
              "the library.$B$B...Please get the blood before I lose my nerve.",
      objectives="Slay General Drakkisath in Upper Blackrock Spire and bring the Blood of the Black Champion "
                 "to Lyra at Morgan's Vigil.",
      request="I've been practicing what to say to the King. I keep stammering on 'Your Majesty'.",
      reward="It's done. The ward is ready. It glows when I hold it near anything dragon-born.$B$BHelendis says "
             "Marshal Windsor has a plan to unmask her before the whole court. When he moves, I'll be there - "
             "ward in my sleeve. Help him, $N. Whatever it takes.",
      kills=[(10363, 1, None)], items=[(190506, 1)], rep=(529, 350))

quest(id=90109, level=60, min=58, kind='', zone=1519, giver=190104, ender=190105, prev=6403, next=90110,
      title='Unmasking the Lady',
      details="You did it. Marshal Windsor walked into the Keep and showed the whole court what she is.$B$BI "
              "was there, $N, at the back, by the pillars. When she changed, my ward blazed like the sun - Bolvar "
              "saw it, the guards saw it, EVERYONE saw it.$B$BShe called you a whelp and fled to her lair. I'm "
              "going to the Keep to stand beside the Highlord. Meet me there. We are not done with her.",
      objectives="Speak with Lyra in Stormwind Keep.",
      request=None,
      reward="Windsor gave his life for the truth. I'm going to make sure the whole kingdom remembers it.$B$B"
             "Bolvar has the Dragon's Eye - a stone Windsor took from her. The dragonkin of the Spire carry "
             "amulets that let them walk through her fires. If the Eye can be made into one... you can follow "
             "her home.",
      kills=[], items=[], rep=(72, 500))

quest(id=90110, level=60, min=58, kind='raid', zone=2159, giver=190105, ender=190105, prev=6502,
      title='The Brood Mother',
      details="Onyxia. That's her name. Daughter of Deathwing. She has whispered in Stormwind's ear for years.$B$B"
              "Her lair is in Dustwallow Marsh, south of Theramore. The amulet will carry you past the flames at "
              "the entrance - the Drakefire Amulet Haleh made from the Dragon's Eye.$B$BEnd it, $N. For Bolvar. For the Defias farmers who lost everything. For every "
              "shy girl who was told she was imagining things.",
      objectives="Slay Onyxia in her lair in Dustwallow Marsh, then return to Lyra in Stormwind Keep.",
      request="I can't stop looking at the empty spot beside the throne.",
      reward="It's over. It's really over.$B$B*Lyra hugs you, then immediately apologizes for hugging you.*$B$B"
             "Thank you, $N. You believed me when no one else did.$B$B...I found something in her chambers, "
             "though. Letters. Talk to me when you're ready.",
      kills=[(10184, 1, None)], items=[], rep=(72, 1000))

quest(id=90111, level=60, min=60, kind='raid', zone=2677, giver=190105, ender=190105,
      title='Shadow Wings',
      details="I found something in Onyxia's chambers. Letters to her brother. 'Lord Victor Nefarius', who "
              "rules the top of Blackrock Spire. Nefarian.$B$BHe breeds monsters from the blood of every dragon "
              "flight in his lair above the Spire. Blackwing Lair. With Onyxia gone, he will be furious - and "
              "careless.$B$BThe way into his lair is through the Orb of Command at the top of the Spire. It knows "
              "the scent of Onyxia's killer now. It will let you pass.",
      objectives="Slay Nefarian in Blackwing Lair, then return to Lyra in Stormwind Keep.",
      request="I've been reading about chromatic dragons. I wish I hadn't.",
      reward="Both of Deathwing's children... gone. Because of you.$B$BI used to think heroes were people in "
             "books. Now I know one. I hope you'll still visit me at the Cathedral. I'll... I'll have tea ready.",
      kills=[(11583, 1, None)], items=[], rep=(72, 1500))

# =========================================================== FAELIN - the Old Gods
quest(id=90201, level=12, min=9, kind='', zone=141, giver=190003, ender=190201,
      title='Tracks Too Big for Teldrassil',
      details="My niece, Faelin Swiftbreeze, believes the world is a puzzle box made for her personal "
              "amusement.$B$BLast week she found 'tracks too big for Teldrassil' and took the boat to Darkshore to "
              "follow them. Alone. Again.$B$BShe is a fine huntress, $N, but she runs toward trouble the way other "
              "elves run toward moonwells. Take the boat from Rut'theran to Auberdine and see that she has not "
              "gotten herself eaten.",
      objectives="Find Faelin Swiftbreeze in Auberdine, in Darkshore.",
      request=None,
      reward="My AUNT sent you? Ha! Of course she did. She thinks I'm going to get eaten.$B$BI'm not going to "
             "get eaten. Probably. Okay, maybe a little. But you have to see what I found!",
      kills=[], items=[], rep=(69, 150))

quest(id=90202, level=17, min=13, kind='', zone=148, giver=190201, ender=190201,
      title='Whispers on the Shore',
      details="So the tracks were just a giant bear. Disappointing. BUT while I was following them I found "
              "THESE people!$B$BThey call themselves the Twilight's Hammer. They camp on the beach north of here, "
              "chanting at the waves. And they carry little black idols that HUM, $N. Hum! Like someone is "
              "talking from very, very far down.$B$BBring me one of those idols. And thin out the cultists while "
              "you're at it - they keep throwing rocks at my birds.",
      objectives="Slay 6 Twilight Disciples and 6 Twilight Thugs on the Darkshore coast and bring a Whispering "
                 "Idol to Faelin in Auberdine.",
      request="Did you get one? Did it hum at you? Was it creepy? I bet it was creepy.",
      reward="*Faelin holds the idol to her ear and goes very still.*$B$B...It's saying a name. It's saying "
             "something about 'the deeps'.$B$BOkay. That's creepy. That's REALLY creepy. I love it. I mean, I hate "
             "it. I love hating it.",
      kills=[(2338, 6, None), (2339, 6, None)], items=[(190511, 1)], rep=(69, 250))

quest(id=90208, level=30, min=30, kind='dungeon', zone=718, giver=190202, ender=190202, prev=90114,
      title='Dreams in the Barrens',
      details="Okay, first creepy thing. Down in the Barrens there's a cave called the Wailing Caverns. A druid "
              "named Naralex went in there to heal the land by dreaming - and he's been having a NIGHTMARE ever "
              "since. His own disciples turned into these snake-druids, the Druids of the Fang.$B$BThe idol hums "
              "louder when I hold it facing south. It's the same voice, $N. Something is talking into Naralex's "
              "dream.$B$BTake out Lord Serpentis and that big thing in the deepest pool - Mutanus. If the "
              "nightmare's voice stops there, we'll know where it came from.",
      objectives="Slay Lord Serpentis and Mutanus the Devourer in the Wailing Caverns, then return to Faelin "
                 "in Astranaar.",
      request="Did you see Naralex? Is he okay? Was he snoring? I bet nightmares snore.",
      reward="Naralex woke up? And the first thing he said was 'it whispers from beneath'?$B$B*Faelin presses "
             "the idol to her ear.* ...Quieter. But not gone. The voice isn't IN the Barrens. It's just passing "
             "through, like water in a pipe.$B$BSo where's the other end of the pipe? I have a guess. A wet guess.",
      kills=[(3673, 1, None), (3654, 1, None)], items=[], rep=(69, 250), next=90203)

quest(id=90203, level=31, min=30, kind='dungeon', zone=719, giver=190202, ender=190202, prev=90208,
      title='The Deeps Are Singing',
      details="'The deeps' - I figured it out! Blackfathom Deeps, the sunken temple on the Ashenvale coast. The "
              "cultists from Darkshore go there in boats at night.$B$BTheir leader is Twilight Lord Kelris, and "
              "they worship something called Aku'mai in the deepest pool. The Sentinels say Aku'mai is just a big "
              "hydra. I don't think a big hydra makes idols hum.$B$BGo get them. I'll be right here sharpening "
              "arrows. ...Or I'll come in after you. I'm not good at waiting.",
      objectives="Slay Twilight Lord Kelris and Aku'mai in Blackfathom Deeps, then return to Faelin in Astranaar.",
      request="You're back! You're wet! Tell me EVERYTHING.",
      reward="Kelris said WHAT before he died? 'The old ones stir beneath the sand'?$B$BSand. Sand, sand, "
             "sand... Tanaris? Silithus? Somewhere with a LOT of sand.$B$BAnd the Twilight's Hammer isn't just "
             "here. Kelris had letters from the Barrens. From Razorfen.",
      kills=[(4832, 1, None), (4829, 1, None)], items=[], rep=(69, 350), next=90209)

quest(id=90209, level=32, min=30, kind='dungeon', zone=491, giver=190202, ender=190202, prev=90203,
      title='Thorns That Whisper',
      details="Razorfen Kraul! The quilboar live inside the thorns of Agamaggan, a demigod who died there ten "
              "thousand years ago. The thorns still grow, $N. Something is still feeding them.$B$BKelris's "
              "letters were to Charlga Razorflank, the quilboar crone who rules the Kraul. She's been trading "
              "with the Twilight's Hammer - idols for thorns. Thorns for idols! Why would cultists want magic "
              "thorns?$B$BI don't know. I want to know. Make her tell you. Or, you know. Don't make her tell you. "
              "She's not the talking type.",
      objectives="Slay Charlga Razorflank in Razorfen Kraul, then return to Faelin in Astranaar.",
      request="I tried to grow one of the thorns in a pot. It grew. Then it hissed at me. I put it outside.",
      reward="She was using the idols to make the thorns grow faster. The voice was telling her how.$B$B*Faelin "
             "frowns, which looks wrong on her face.*$B$BIt doesn't just whisper, $N. It TEACHES. It finds "
             "someone who wants something and it teaches them how to get it. And it always asks for something "
             "back.$B$BKelris's last letter mentioned one more 'pupil'. Under Dun Morogh.",
      kills=[(4421, 1, None)], items=[], rep=(69, 350), next=90210)

quest(id=90210, level=35, min=30, kind='dungeon', zone=721, giver=190202, ender=190202, prev=90209,
      title='Something Pushed Them Up',
      details="Gnomeregan! The gnomes say the troggs came boiling up out of the deep earth and took their city. "
              "Everybody blames Mekgineer Thermaplugg for flooding it with radiation to stop them.$B$BBut troggs "
              "don't just leave their caves, $N. Something PUSHED them up. Something under them.$B$BThermaplugg "
              "kept the Twilight's letters, and Kelris called him 'the eager pupil'. Find out what he was taught. "
              "Then stop him. He's a gnome who flooded his own city. I'm not going to cry over him.",
      objectives="Slay Mekgineer Thermaplugg in Gnomeregan, then return to Faelin in Astranaar.",
      request="Did the gnomes give you a medal? They gave me a pamphlet about radiation.",
      reward="'The one beneath the sands sleeps lightly. Dig, and you will hear him.' That's what "
             "he was taught. He dug, and the troggs came up to get away from whatever he woke.$B$BIt's in the "
             "south, $N. Under the sand. I'm sure of it now.$B$BI'm going to need help. A lot of help. And some "
             "of it from people who know about things that should stay dead...",
      kills=[(7800, 1, None)], items=[], rep=(69, 500), next=90211)

quest(id=90211, level=40, min=40, kind='', zone=130, giver=190202, ender=190402, prev=90210,
      title='The Warlock in the Sepulcher',
      details="So. Here's a thing I never thought I'd say: we need a Forsaken.$B$BThe voice talks to the "
              "living, but it ALSO talks to the dead - Thermaplugg's notes say the Scourge necromancers hear it "
              "too. And there's a Forsaken warlock in Silverpine who's been sending the Cenarion Circle very "
              "polite, very creepy letters about 'whispers among the restless dead'. Vesper Duskhollow.$B$BGo "
              "to the Sepulcher and find her, $N. I'll head south to Silithus with the Cenarion Circle and scout "
              "the sands. When you're ready - truly ready - come find me at Cenarion Hold. I'll have SO much to "
              "show you.",
      objectives="Find Vesper Duskhollow at the Sepulcher in Silverpine Forest.",
      request=None,
      reward="A night elf sent you? To me? How deliciously unexpected.$B$B*Vesper reads the letter, a faint "
             "smile on her grey lips.*$B$BThe huntress is right. The dead hear things. And lately the dead of "
             "Tirisfal hear a name - one I have hated for a very long time. Sit. We have work to do.",
      kills=[], items=[], rep=(68, 250), next=90412)

quest(id=90205, level=57, min=54, kind='', zone=1377, giver=190203, ender=190203, prev=90211,
      title='Silithid Rising',
      details="You came! Cenarion Hold is AMAZING. Bugs the size of houses! Sand everywhere! The Twilight's Hammer has "
              "camps all over Silithus, and the Geolords and Stonecallers are trying to wake something under the "
              "Scarab Wall.$B$BIf we break their circles, the Cenarion Circle can push to the gates. I talked to "
              "the commander. Well. I talked AT the commander. A lot. He said yes to make me stop.$B$BLet's go "
              "break some cultists!",
      objectives="Slay 5 Twilight Geolords and 5 Twilight Stonecallers in Silithus, then report to Faelin at "
                 "Cenarion Hold.",
      request="I counted the bugs today. I stopped at three hundred. There are more than three hundred.",
      reward="Their circles are broken! Without them holding the seal, the old magic on the Scarab Wall is "
             "failing...$B$BWait. Feel that? The ground's shaking. The GATES, $N!",
      kills=[(11881, 5, None), (11882, 5, None)], items=[], rep=(609, 500))

quest(id=90206, level=60, min=58, kind='raid', zone=1377, giver=190203, ender=190203,
      title='The Unscarred',
      details="The ruins inside the Scarab Wall are crawling with qiraji. Their general, Ossirian the "
              "Unscarred, guards the outer city. They say no blade has ever cut him.$B$BThe crystals in the ruins "
              "weaken him, if you're smart about it. I'm smart about it. You're smart about it. We're both "
              "smart.$B$BBring me back proof he's not unscarred anymore!",
      objectives="Slay Ossirian the Unscarred in the Ruins of Ahn'Qiraj, then return to Faelin at Cenarion Hold.",
      request="Is he scarred yet? He should be scarred.",
      reward="UNSCARRED. Ha! Not anymore!$B$BBut the whispers are louder now. The idol won't stop humming. "
             "Whatever is in the temple at the heart of Ahn'Qiraj... it's awake. And it knows our names.",
      kills=[(15339, 1, None)], items=[], rep=(609, 1000))

quest(id=90207, level=60, min=60, kind='raid', zone=1377, giver=190203, ender=190203,
      title='The Old God Wakes',
      details="C'Thun. That's the name the idol whispers. An Old God, older than the trees, older than "
              "the titans' order. Every whisper in Darkshore, every nightmare in the swamp - it's all him, "
              "dreaming in the dark.$B$BI'm not scared. I'm a LITTLE scared. I'm scared and excited and I "
              "haven't slept in three days.$B$BLet's end the dream, $N. Together.",
      objectives="Slay C'Thun in the Temple of Ahn'Qiraj, then return to Faelin at Cenarion Hold.",
      request="*Faelin is uncharacteristically quiet, clutching the silent idol.*",
      reward="It stopped. The idol stopped humming. For the first time in... I don't even know how long. It's "
             "just quiet.$B$B*Faelin laughs, then sits down in the sand.*$B$BBest. Adventure. EVER. Same time "
             "next Old God?",
      kills=[(15727, 1, None)], items=[], rep=(609, 1500))

# =========================================================== DURZA - the Firelord
quest(id=90301, level=9, min=6, kind='', zone=14, giver=190004, ender=190301,
      title="A Fire That Won't Listen",
      details="Lok'tar, young one. The fire spirits of Durotar have grown wild - they scorch the crops and lash "
              "out at the shamans who call them.$B$BOne of my old students, Durza Stormcaller, has taken this... "
              "personally. Her mother died to a maddened fire spirit, and Durza has more fury than wisdom.$B$B"
              "She is camped at the edge of Razor Hill, shouting at campfires. Go to her. Perhaps a stranger can "
              "reach her where an old teacher cannot.",
      objectives="Speak with Durza Stormcaller at Razor Hill.",
      request=None,
      reward="Grimtusk sent you? Of course he did. 'Patience, Durza. Balance, Durza.' Pfah.$B$B...Sorry. "
             "You came all this way. Fine. Listen.",
      kills=[], items=[], rep=(76, 150))

quest(id=90302, level=15, min=11, kind='dungeon', zone=14, giver=190301, ender=190301,
      title='The Searing Blade',
      details="The fire spirits aren't just wild. Someone is MAKING them wild.$B$BThere's a cult under Orgrimmar "
              "itself - the Searing Blade. They hide in Ragefire Chasm and bargain with a demon of flame called "
              "Taragaman. Their leader, Bazzalan, sends the fire spirits mad on purpose.$B$BI'd go myself, but "
              "the guards say I 'yell at the walls'. So you go. Kill them both. Bring me their pact.$B$B...Please.",
      objectives="Slay Taragaman the Hungerer and Bazzalan in Ragefire Chasm and bring the Searing Blade Pact to "
                 "Durza at Razor Hill.",
      request="Well? Are they dead?",
      reward="*Durza reads the pact and her hands start to shake.*$B$B'In service of the Firelord, who sleeps "
             "beneath the mountain.' The FIRELORD. Ragnaros.$B$BMy mother died because some cultists wanted "
             "to please a buried elemental lord. ...I need to hit something. Not you. Something.",
      kills=[(11520, 1, None), (11519, 1, None)], items=[(190521, 1)], rep=(76, 250))

quest(id=90309, level=50, min=50, kind='dungeon', zone=1337, giver=190302, ender=190302, prev=90416,
      title='The Earth Remembers',
      details="So the dead girl sent you. Fine. She's strange, but she's right - the elements are screaming "
              "everywhere at once, and it's not just fire.$B$BStart with the earth. In the Badlands there's a "
              "titan vault called Uldaman. The dwarves dug it open and woke its keeper, Archaedas - a stone giant "
              "who thinks every living thing is an intruder. Now the earth spirits for a hundred miles howl in "
              "their sleep.$B$BPut him back to sleep, $N. Hard. Then come back here and tell me if the ground "
              "stops shaking.",
      objectives="Defeat Archaedas in Uldaman, then return to Durza in Shadowprey Village, Desolace.",
      request="The earth here keeps grumbling. Like an old man who can't find his pipe.",
      reward="*Durza kneels and lays her palm on the ground for a long time.*$B$B...Quieter. One voice "
             "quieter. But there's a hum under all of it, $N, the same one in the fire. Like someone pulling all "
             "the elements by a string.$B$BThe Zandalari trolls in Tanaris claim to know things about strings. "
             "Let's see what they know.",
      kills=[(2748, 1, None)], items=[], rep=(76, 350), next=90308)

quest(id=90308, level=51, min=50, kind='dungeon', zone=1176, giver=190302, ender=190302, prev=90309,
      title='Sand and Blood',
      details="Zul'Farrak. The Sandfury trolls in Tanaris have been sacrificing prisoners to bind elemental "
              "spirits into their idols - their witch doctor Zum'rah raises the dead to guard them, and Chief "
              "Ukorz Sandscalp sells the bound spirits to anyone with gold.$B$BAnyone. Including a cult that "
              "serves the Firelord.$B$BI'm a shaman. Spirits aren't merchandise. Go remind them.",
      objectives="Slay Witch Doctor Zum'rah and Chief Ukorz Sandscalp in Zul'Farrak, then return to Durza in "
                 "Shadowprey Village.",
      request="Did you see the cages? I heard about the cages.",
      reward="Ukorz kept a ledger. Bound fire spirits - sold by the dozen - to buyers who signed with a burning "
             "hammer. The Dark Irons. Blackrock Mountain again.$B$BAnd one more name: Princess Theradras. Her "
             "caverns are right here in Desolace, poisoning the earth while the trolls sell the fire. Somebody "
             "is shaking the whole world at once.",
      kills=[(7271, 1, None), (7267, 1, None)], items=[], rep=(76, 350), next=90303)

quest(id=90303, level=52, min=50, kind='dungeon', zone=2100, giver=190302, ender=190302, prev=90308,
      title='Earth That Weeps',
      details="I've been training. Grimtusk says I'm 'less on fire'. I think that's a compliment.$B$BThe "
              "Earthen Ring sent word: the earth is sick here in Desolace. Princess Theradras, daughter of the "
              "earth elemental lord, has poisoned the caverns of Maraudon. The elements are all being twisted at "
              "once, $N. Fire, earth... it's like someone is shaking the whole world.$B$BDeal with her. And bring "
              "me a piece of that poisoned earth.",
      objectives="Defeat Princess Theradras in Maraudon and bring a Corrupted Earth Shard to Durza in "
                 "Shadowprey Village, Desolace.",
      request="The earth here cries at night. I can hear it. Can you?",
      reward="*Durza presses the shard to her forehead and closes her eyes.*$B$BIt's not the earth's fault. "
             "Something below Blackrock Mountain is pulling at all the elements like a whirlpool. Fire is "
             "loudest. The Firelord again.$B$BI'm not crying. The spirits are loud. That's all.",
      kills=[(12201, 1, None)], items=[(190522, 1)], rep=(76, 350), next=90310)

quest(id=90310, level=54, min=50, kind='dungeon', zone=1477, giver=190302, ender=190302, prev=90303,
      title='The Drowned Temple',
      details="One more before the mountain. In the Swamp of Sorrows the Atal'ai trolls are trying to call "
              "their blood god Hakkar back into the world from the Sunken Temple. Their prophet, Jammal'an, "
              "tears spirits out of the water and the earth to feed the summoning.$B$BAnd they've trapped a "
              "green dragon's shade down there - Eranikus. His nightmares leak into every spirit in the swamp.$B$B"
              "Stop the prophet. Free the dragon's shade. Bring me a piece of his nightmare - Faelin will want to "
              "see it. She says the nightmares and her whispers have the same voice.",
      objectives="Slay Jammal'an the Prophet and the Shade of Eranikus in the Sunken Temple and bring a Nightmare "
                 "Shard to Durza in Shadowprey Village.",
      request="I tried to go myself. Faelin's druid friends sat on me. Literally. A bear sat on me.",
      reward="*Durza holds the shard at arm's length.*$B$BUgh. It's cold, and it whispers. I'll send it to "
             "Faelin. She'll love it. She loves creepy things.$B$BThe spirits are calmer now, $N. All except "
             "fire. Fire still screams, and it screams from Blackrock Mountain. It's time. I'll meet you at "
             "Kargath, at the foot of the mountain.",
      kills=[(5710, 1, None), (5709, 1, None)], items=[(190512, 1)], rep=(76, 500), next=90304)

quest(id=90304, level=55, min=52, kind='dungeon', zone=1584, giver=190302, ender=190303, prev=90310,
      title='Embers of the Firelord',
      details="Blackrock Depths. The Dark Iron dwarves worship Ragnaros like a god. They keep his servants "
              "close: Lord Incendius, a fire lord who tortures elementals at his anvil, and Ambassador "
              "Flamelash, who speaks for Ragnaros at the Dark Iron court.$B$BKill them both. I'll meet you at "
              "Kargath in the Badlands, at the foot of the mountain.$B$BAnd $N... thank you for walking this road "
              "with me. Don't make it weird.",
      objectives="Slay Lord Incendius and Ambassador Flamelash in Blackrock Depths, then meet Durza at Kargath "
                 "in the Badlands.",
      request="I can feel the mountain from here. It's like standing next to a heartbeat.",
      reward="Incendius had my mother's spirit-bead on his anvil, $N. Her BEAD. He was using the spirits of "
             "dead shamans to bind his elementals.$B$B*Durza turns away for a long moment.*$B$BOne more. One "
             "more step and I can look the Firelord in the eye.",
      kills=[(9017, 1, None), (9156, 1, None)], items=[], rep=(76, 500))

quest(id=90305, level=58, min=52, kind='dungeon', zone=3, giver=190303, ender=190303,
      title='Heart of the Mountain',
      details="Emperor Dagran Thaurissan. His family summoned Ragnaros into this world and his throne room sits "
              "above the Firelord's prison. He carries a brand of living fire - Ragnaros's favor.$B$BTake it "
              "from him. With the brand, the elementals at the Molten Core will see us as servants of the "
              "Firelord until it is too late.$B$BFor my mother. For every spirit he enslaved.",
      objectives="Slay Emperor Dagran Thaurissan in Blackrock Depths and bring Thaurissan's Brand to Durza "
                 "at Kargath.",
      request="I keep hearing her voice in the fire. I don't know if that's good or bad.",
      reward="The brand burns cold in my hand. It knows we're coming.$B$BOne step left before we go down, $N. "
             "Just one.",
      kills=[(9019, 1, None)], items=[(190523, 1)], rep=(76, 750), next=90311)

quest(id=90311, level=60, min=55, kind='', zone=25, giver=190303, ender=14387, prev=90305,
      title='The Molten Bridge',
      details="The Core is sealed to anyone the mountain doesn't know. But there's a mage who keeps watch on "
              "the heights of Blackrock Mountain - Lothos Riftwaker. He studies the Molten Core and he can send "
              "those who are attuned to it straight down through the rock.$B$BGo to him on the Blackrock "
              "heights. He'll ask for a fragment of the Core itself - you'll find one by the portal deep "
              "in the Depths. Do what he asks, $N. Then come back to me.",
      objectives="Speak with Lothos Riftwaker above Blackrock Mountain.",
      request=None,
      reward="Another one who wishes to look upon the Firelord. The shaman sent you? She burns brightly, that "
             "one.$B$BBring me a fragment of the Core from the depths beneath the mountain, and I will attune "
             "you to its fires.",
      kills=[], items=[], rep=(76, 250), next=7848)

quest(id=90306, level=60, min=60, kind='raid', zone=2717, giver=190303, ender=190303, prev=7848,
      title='The Firelord',
      details="Ragnaros. The Firelord. The one who drove the fire spirits mad and the one my mother died "
              "fighting without knowing it.$B$BHe waits in the deepest chamber of the Molten Core, beneath "
              "Blackrock Depths. His Majordomo will summon him when his guards fall.$B$BI'm not angry anymore, "
              "$N. I'm just... ready. Let's go put out a fire.",
      objectives="Defeat Ragnaros in the Molten Core, then return to Durza at Kargath.",
      request="Is it done? Tell me it's done.",
      reward="*Durza holds her mother's bead up to the sky. It flickers, warm and steady.*$B$BShe's at peace. "
             "The fire spirits are singing again - I can hear them.$B$B...Thank you. I mean it. Now look away, "
             "because I'm about to cry and I'll hit you if you watch.",
      kills=[(11502, 1, None)], items=[], rep=(76, 1500))

# =========================================================== VESPER - the Scourge
quest(id=90401, level=8, min=5, kind='', zone=85, giver=190005, ender=190401,
      title='The Girl Among the Graves',
      details="There's a girl in my graveyard. Well, a Forsaken. Calls herself Vesper. She sits among the "
              "headstones every night, reading poetry to the dead and drawing circles in violet light.$B$BShe "
              "isn't hurting anyone. But the Deathguards are nervous, and nervous Deathguards stab first.$B$B"
              "Go talk to her, would you? Find out what she wants. She seems to like strangers better than "
              "the people she's met.",
      objectives="Speak with Vesper Duskhollow at the Brill graveyard.",
      request=None,
      reward="The gravekeeper sent you? He worries. It's endearing, in a damp sort of way.$B$BSit. The dead "
             "don't mind company, and neither do I. Tonight.",
      kills=[], items=[], rep=(68, 150))

quest(id=90402, level=24, min=18, kind='dungeon', zone=85, giver=190401, ender=190401,
      title="The Wolf Mage's Grimoire",
      details="I read to the dead because I am looking for something. The Scourge plague didn't just kill "
              "Lordaeron, it STAYED. The dead rise. The Lich King calls and they answer.$B$BBut not me. Not us. "
              "I want to know why.$B$BArchmage Arugal, mad as he is, studied how to call things back from beyond "
              "death. He hides in Shadowfang Keep, in Silverpine. Bring me his grimoire. I'll make tea. Nobody "
              "else here drinks tea anymore.",
      objectives="Slay Archmage Arugal in Shadowfang Keep and bring Arugal's Grimoire to Vesper in Brill.",
      request="Did he monologue? They always monologue.",
      reward="*Vesper turns the pages slowly, a faint smile on her grey lips.*$B$BOh, this is wonderful. "
             "Horrible, but wonderful. He was close. The plague binds souls through a lich's phylactery. Break "
             "the vessel, free the soul.$B$BThere's a lich in the Barrens. I want a piece of his phylactery.",
      kills=[(4275, 1, None)], items=[(190531, 1)], rep=(68, 250))

quest(id=90412, level=40, min=40, kind='dungeon', zone=796, giver=190402, ender=190402, prev=90211,
      title='The Bloodmage',
      details="The name the dead whisper is Kel'Thuzad. The Lich King's favorite. I want to know how his "
              "voice reaches so far, and the Scarlet Crusade - of all people - have been hunting the same "
              "whispers in their Monastery in Tirisfal.$B$BThey keep their 'dangerous' prisoners in the graveyard "
              "wing, watched by a Bloodmage named Thalnos who died there and keeps on working anyway. A man after "
              "my own heart. If I had one.$B$BBring him down, $N, and let's see what the Crusade has been hiding "
              "in its crypts.",
      objectives="Slay Bloodmage Thalnos in the Scarlet Monastery Graveyard, then return to Vesper at the Sepulcher.",
      request="The Crusade hates my kind. I find it flattering, really. Such commitment.",
      reward="*Vesper flips through a burned journal.*$B$BThalnos was questioning plague survivors. Asking "
             "who heard a 'cold voice in their dreams'. The Crusade is hunting for the same voice we are, $N - "
             "they just burn everyone who hears it.$B$BTheir library will have the rest.",
      kills=[(4543, 1, None)], items=[], rep=(68, 250), next=90413)

quest(id=90413, level=41, min=40, kind='dungeon', zone=796, giver=190402, ender=190402, prev=90412,
      title='Forbidden Shelves',
      details="Arcanist Doan keeps the Scarlet Library, and he is the sort of librarian who burns books "
              "instead of lending them. He has records of every heretic they have 'cleansed' - and what those "
              "poor souls confessed before the fire.$B$BI want those confessions. Doan will not want to give "
              "them up. Persuade him. Permanently.",
      objectives="Slay Arcanist Doan in the Scarlet Monastery Library, then return to Vesper at the Sepulcher.",
      request="Did you find the poetry section? There's never a poetry section.",
      reward="Hundreds of confessions, and they all say the same thing. A cold voice. A floating city in the "
             "sky. A promise of eternal life.$B$BKel'Thuzad recruits, $N. He has been recruiting from inside "
             "the Crusade itself. The Armory will tell us who.",
      kills=[(6487, 1, None)], items=[], rep=(68, 250), next=90414)

quest(id=90414, level=42, min=40, kind='dungeon', zone=796, giver=190402, ender=190402, prev=90413,
      title='The Scarlet Champion',
      details="Herod, the Scarlet Champion, trains the Crusade's soldiers in the Armory. The confessions say "
              "he's the one who takes the 'difficult' prisoners away, and they never come back - not even as "
              "Scourge.$B$BSomeone is collecting them. Herod knows who. Go and ask him, loudly, with something "
              "sharp.",
      objectives="Slay Herod in the Scarlet Monastery Armory, then return to Vesper at the Sepulcher.",
      request="He whirls, I'm told. Do try not to be standing next to him when he whirls.",
      reward="Herod's orders came from the Cathedral itself. From High Inquisitor Whitemane and Commander "
             "Mograine.$B$BThe leaders of the Crusade - the people sworn to destroy the Scourge - are sending "
             "it prisoners. How delightfully hypocritical.",
      kills=[(3975, 1, None)], items=[], rep=(68, 350), next=90415)

quest(id=90415, level=44, min=40, kind='dungeon', zone=796, giver=190402, ender=190402, prev=90414,
      title='Rise, My Champion',
      details="The Cathedral, then. Commander Mograine guards the nave, and Whitemane... well. Whitemane "
              "has a habit of raising Mograine when he falls. Romantic, in a ghoulish way.$B$BEnd them both, "
              "$N. Whatever they are bargaining with, it ends with them.",
      objectives="Slay Scarlet Commander Mograine and High Inquisitor Whitemane in the Scarlet Monastery "
                 "Cathedral, then return to Vesper at the Sepulcher.",
      request="I lit a candle for the occasion. A black one. It seemed appropriate.",
      reward="Whitemane's letters are signed by a lich. Amnennar the Coldbringer, in Razorfen Downs - he "
             "trades her 'cures' for the plague in return for prisoners. There is no cure, of course. There "
             "is only Kel'Thuzad, collecting.$B$BOne more messenger to silence, and then we follow the thread "
             "upward.",
      kills=[(3976, 1, None), (3977, 1, None)], items=[], rep=(68, 350), next=90403)

quest(id=90403, level=45, min=40, kind='dungeon', zone=722, giver=190402, ender=190402, prev=90415,
      title='Cold Words in the Downs',
      details="Amnennar the Coldbringer. A lich of the Scourge, nesting among the quilboar of Razorfen Downs in "
              "the southern Barrens. He spreads the plague to the quilboar, raises them in the Lich King's name, "
              "and sells false hope to the Crusade.$B$BBring me a fragment of his phylactery. Do be careful. "
              "Liches are terribly rude.",
      objectives="Defeat Amnennar the Coldbringer in Razorfen Downs and bring a Phylactery Fragment to Vesper "
                 "at the Sepulcher in Silverpine Forest.",
      request="The Sepulcher's bats have names now. I named them. Don't tell anyone.",
      reward="*The fragment frosts Vesper's fingers. She doesn't seem to notice.*$B$BHe was a messenger. "
             "His phylactery hums with a single name: Kel'Thuzad. He hides in a floating citadel, they say, "
             "high above the Plaguelands.$B$BI am going to find him. And when I do, I am going to be VERY "
             "polite. Right up until the end.",
      kills=[(7358, 1, None)], items=[(190532, 1)], reward_item=191161, rep=(68, 350), next=90416)

quest(id=90416, level=50, min=50, kind='', zone=405, giver=190402, ender=190302, prev=90403,
      title='The Shaman Who Shouts at Fire',
      details="Before I go hunting liches, there is a debt to pay. Your huntress friend asked me to look into "
              "something: the elements themselves are screaming, all over Kalimdor, and the dead hear it too.$B$B"
              "There is an orc shaman in Desolace, at Shadowprey Village - Durza Stormcaller. She shouts at "
              "campfires, the trolls say, and the campfires shout back. She has been trying to find out who is "
              "torturing the elements, and nobody will help her because she is 'too angry'.$B$BI like angry "
              "people. They get things done. Go to her, $N. When you are stronger still, come back to me. "
              "Kel'Thuzad will keep. He is very patient. So am I.",
      objectives="Find Durza Stormcaller in Shadowprey Village, Desolace.",
      request=None,
      reward="A Forsaken sent you. A FORSAKEN.$B$B*Durza reads the letter twice, scowling.*$B$B...She writes "
             "nicely, for a corpse. And she's right. Fire, earth, water - all of them are crying, and nobody "
             "listens.$B$BFine. You're here. Don't waste my time and I won't waste yours.",
      kills=[], items=[], rep=(76, 250), next=90309)

quest(id=90404, level=58, min=52, kind='dungeon', zone=2057, giver=190402, ender=190403, prev=90416,
      title='The Dark Academy',
      details="Kel'Thuzad founded a school of necromancy in Caer Darrow: Scholomance. The headmaster, "
              "Darkmaster Gandling, still teaches its cruel lessons to the living and the dead.$B$BEnd the "
              "lessons, $N. Class dismissed. Permanently.$B$BI'll meet you at the Bulwark in the Western "
              "Plaguelands afterward. The smell there is exquisite.",
      objectives="Slay Darkmaster Gandling in Scholomance, then find Vesper at the Bulwark in the Western "
                 "Plaguelands.",
      request="Did you find his grading scale? I'm curious how one fails necromancy.",
      reward="Gandling's notes all end the same way: reports sent to the Baron in Stratholme, and from the "
             "Baron to the citadel in the sky.$B$BEvery thread leads to Kel'Thuzad. We pull one more.",
      kills=[(1853, 1, None)], items=[], rep=(529, 500))

quest(id=90405, level=60, min=55, kind='dungeon', zone=28, giver=190403, ender=190404,
      title="The Baron's Last Night",
      details="Baron Rivendare. Death knight. Master of Stratholme's slaughterhouse. He holds the key that "
              "lets Kel'Thuzad's servants come and go from the necropolis above.$B$BKill him, $N. With his "
              "seal broken, the Argent Dawn can take us up to Naxxramas itself.$B$BI'll be at Light's Hope "
              "Chapel. Yes, the paladins stare. I stare back. I'm better at it.",
      objectives="Slay Baron Rivendare in Stratholme, then meet Vesper at Light's Hope Chapel in the Eastern "
                 "Plaguelands.",
      request="The paladins keep offering to 'cleanse' me. I keep offering to curse them. We're at an impasse.",
      reward="The Baron's seal is broken. The Argent Dawn has agreed to take us to the necropolis.$B$B*Vesper "
             "looks up at the dark shape drifting over the Plaguelands.*$B$BHe's up there. Waiting. How "
             "lovely. I've been rehearsing my speech.",
      kills=[(10440, 1, None)], items=[], rep=(529, 1000), next=90417)

quest(id=90417, level=60, min=58, kind='', zone=139, giver=190404, ender=16116, prev=90405, next=0,
      rew_spell_cast=28006,
      title='The Dread Citadel',
      details="The Argent Dawn's Archmage Angela Dosantos keeps the way to the necropolis. She can cloak you "
              "in arcane light, so the citadel's wards take you for one of its own and let you step inside.$B$B"
              "She makes most heroes pay for the privilege - in gold, in deeds, in years of service to the Dawn. "
              "But I have told her about you, $N. About Arugal's grimoire and the lich in the Downs and the Baron's "
              "last night.$B$BGo to her. She is expecting you.",
      objectives="Speak with Archmage Angela Dosantos at Light's Hope Chapel.",
      request=None,
      reward="Vesper Duskhollow speaks well of you, and Vesper speaks well of no one. You have done the Dawn's "
             "work already, hero - more of it than most who stand before me.$B$B*Angela raises her hands and "
             "cold blue light settles over you.*$B$BThe citadel will know you now. Go with the Light - and with "
             "your strange friend.",
      kills=[], items=[], rep=(529, 500))

quest(id=90406, level=60, min=60, kind='raid', zone=3456, giver=190404, ender=190404, prev=90417,
      title='The Lich in the Sky',
      details="You are attuned. Naxxramas will open for you. Kel'Thuzad waits in its frozen heart, beyond the spider wing, the plague wing, the "
              "military wing and the house of constructs.$B$BI won't pretend this doesn't frighten me. Even the "
              "dead can be afraid. Especially the dead.$B$BBut he took everything from me. Let's go take "
              "something back. His unlife, for instance.",
      objectives="Slay Kel'Thuzad in Naxxramas, then return to Vesper at Light's Hope Chapel.",
      request="*Vesper is staring at the sky, very still.*",
      reward="It's done. Kel'Thuzad is dust.$B$B*Vesper's voice is quiet.* I gave my speech. He didn't listen. "
             "They never listen.$B$BThank you, $N. You're the first living thing I've wanted to keep around. "
             "That's a compliment. The highest I give.",
      kills=[(15990, 1, None)], items=[], rep=(529, 1500))

# ------------------------------------------------------------------------------------ Katrana
# Lady Katrana Prestor's new conversations (npc_text 900500-900504), by chapter of Lyra's story.
KATRANA_TEXTS = {
    900500: "Another adventurer seeking an audience. How... quaint.$B$BThe Highlord is very busy, and I am "
            "busier. Stormwind runs on paperwork and patience, $N, and I have an endless supply of one of them.",
    900501: "Ah, my little courier. Darkshire's roads are so dreadfully dangerous these days, aren't they? "
            "I do hope my letter reached its... destination.$B$BRun along. The court has no further need of you.",
    900502: "You have been traveling a great deal, $N. Scarlet Monastery, I hear. Such a gloomy place for a holiday."
            "$B$BBe careful what stones you turn over. Some of them have teeth beneath.",
    900503: "*Her voice drops to a purr that does not sound entirely human.*$B$BYou and that mousy little "
            "acolyte have been very busy. Drakkisath was one of my favorites.$B$BLeave Stormwind while you still "
            "can, whelp.",
    900504: "*Lady Prestor's eyes flash red. For a moment her shadow on the wall is enormous, winged.*$B$BHow "
            "DARE you. In my court. Before my king.$B$BVery well. If you want to see what I truly am, come to "
            "Dustwallow Marsh. I will show you.",
}

# Companion gossip texts: greeting at 9001x1, "about" at 9001x0 + 10 (see the script).
CAPTIVE_TEXT = (900100, "*A young woman in torn acolyte robes is huddled against the hull, wrists bound with rope.*"
                        "$B$BP-please... are you with the Defias? You don't look like the Defias. You look... kind.")

# ------------------------------------------------------------------------------------ Navi
# Navi, a night elf spirit bound into a wisp, waits in every starting area. She gives the first of
# her quests at level 1; her reward, Navi's Light, keeps her at your side (zelda_companions.cpp
# npc_zelda_navi) and the server gives it its powers (heal in combat, rise again on death).
NAVI = dict(
    entry=190601, name='Navi', subname='Fairy of the Lost Woods', display=10045, scale=0.6,
    greeting="Hey! Listen! ...Oh! You can hear me? Nobody ever hears me!",
    about="I'm Navi! A long, long time ago I was a priestess of Elune. Now I'm a wisp. It's a long story. "
          "Okay, it's a short story, but it's sad, so I don't tell it.$B$BI'm looking for a hero. He wore green, "
          "he carried a sword that sang, and he got LOST. Very, very lost. His name was Linken.$B$BUntil I find "
          "him... I'll look after you instead! Hey! Listen! That's my job now!",
    spawns=[  # one in every starting area, beside its first quest giver
        (0, -8930.5, -133.0, 83.4, 4.0),      # Northshire Abbey
        (0, -6211.5, 331.5, 383.7, 4.0),      # Coldridge Valley
        (1, 10325.5, 829.5, 1326.5, 5.5),     # Shadowglen
        (1, -603.5, -4248.0, 38.9, 3.3),      # Valley of Trials
        (1, -2909.0, -254.0, 53.0, 3.5),      # Camp Narache
        (0, 1682.5, 1671.0, 135.8, 3.8),      # Deathknell
    ])

NAVI_ITEMS = [
    dict(entry=190601, name="Navi's Light", display=24730, quality=5, inventory=12, cls=4, subclass=0,
         description="Equip: Navi follows you. In combat she heals you for 10% of your health every 10 sec. "
                     "If you die, her light can bring you back with 10% of your health (once every 5 min). Hey! Listen!"),
    dict(entry=190602, name='Piece of Heart', display=6614, quality=1, inventory=0, cls=12, subclass=0,
         description='A quarter of something that wants to be whole.'),
]

quest(id=90501, level=1, min=1, kind='', zone=0, giver=190601, ender=190601,
      title='Hey! Listen!',
      details="Hey! Listen! HEY! Over here! Yes, you, the one with the face!$B$BI've been floating around this "
              "place for AGES waiting for someone who could hear me. You can! That means you've got a hero's "
              "heart in there somewhere.$B$BI'm looking for a lost hero, and it's dangerous to go alone. So "
              "here's the deal: I'll come with you. Wear my light and I'll keep you safe - I'll heal you when it "
              "hurts, and if you fall... well, I'll pull you back. Just not too often, okay? It's tiring!",
      objectives="Accept Navi's Light.",
      request=None,
      reward="Yay! Partners! Put my light on - a trinket slot is fine, I'm small.$B$BAnd if you ever hear "
             "'Hey! Listen!' in a dungeon... it's important. Probably.",
      kills=[], items=[], reward_item=190601, rep=(0, 0), next=0)

quest(id=90502, level=18, min=18, kind='', zone=0, giver=190601, ender=190601,
      title='Pieces of Heart',
      details="Hey! Listen! Every now and then when you defeat something strong, I can feel a little Piece of "
              "Heart fall out of the world. Courage that got scattered around.$B$BBring me four of them! When "
              "four come together they make you tougher - that's how it worked for my hero.$B$BAny worthy foe "
              "might drop one. Not the tiny ones. Those don't count. Sorry, tiny ones.",
      objectives="Collect 4 Pieces of Heart from worthy foes and give them to Navi.",
      request="Did you find any? They sparkle a little.",
      reward="Four pieces! Look, look - they're fitting together!$B$B*Navi spins in a happy circle.*$B$BThat's a "
             "whole heart! Take something nice from my stash. Heroes need gear!",
      kills=[], items=[(190602, 4)], rep=(0, 0), next=0)

quest(id=90503, level=47, min=47, kind='', zone=490, giver=190601, ender=8737,
      title='The Hero of Time',
      details="Hey! LISTEN! I felt it! Something far, far south, in a crater full of dinosaurs and steam - a "
              "heartbeat I know!$B$BIt's him. It's Linken! He's been lost in Un'Goro Crater all this time!$B$B"
              "Please, please, please take me to Marshal's Refuge. If he's forgotten me... well. I'll just have to "
              "remind him. Very loudly.",
      objectives="Find Linken in Un'Goro Crater.",
      request=None,
      reward="*Linken blinks at the little wisp at your side.*$B$B...Navi? I... I know that voice. I don't know "
             "how I know it. I washed up here with no memory and an old sword I can't remember using.$B$BThere "
             "is a gnome in Winterspring, Donova Snowden, who studies the strange fruit of this crater. She says "
             "an elixir made from it could show me who I was. Will you help me find my way back, friend?",
      kills=[], items=[], rep=(0, 0))

# Navi's errands along the way: one for every few levels, offered only once you are that level.
NAVI_ERRANDS = [
    # (id, level, zone, creature, count, title, details, objectives text, request, reward)
    (90504, 15, 44, 442, 10, "Gohma's Children",
     "Hey! Listen! The spiders in Redridge Mountains - see the eyes? Those are Gohma eyes. Well, Gohma-ISH. "
     "One big eye would be worse, but lots of little eyes is still bad!$B$BClear out the Tarantulas before they "
     "grow up into something with a boss health bar.",
     "Slay 10 Tarantulas in Redridge Mountains.", "Are they gone yet? I can still feel them looking at me.",
     "No more eyes! Well... fewer eyes. You're getting good at this!"),
    (90505, 17, 44, 441, 10, "Volvagia's Little Cousins",
     "Hey! LISTEN! There are baby dragons in Redridge! Black ones! Don't let the cute fool you - I knew a dragon "
     "named Volvagia who was a cute baby once, and then he tried to eat a whole mountain.$B$BThin the Black Dragon "
     "Whelps out before they get any bigger.",
     "Slay 10 Black Dragon Whelps in Redridge Mountains.", "Careful, they bite! And they breathe fire! At the same time!",
     "Whew! You smell like smoke. Heroes always smell like smoke. It's fine!"),
    (90506, 20, 11, 1007, 12, "Moblin Raiders",
     "Hey! Listen! The gnolls in the Wetlands are SO much like the Moblins back home - big ears, big spears, "
     "zero manners.$B$BThe Mosshide Gnolls keep raiding the roads. A hero would stop them. You're a hero. So!",
     "Slay 12 Mosshide Gnolls in the Wetlands.", "Moblins - I mean gnolls - still on the road?",
     "The roads are safe again! I'm putting this on your list of good deeds. It's a long list. I keep it in my head."),
    (90507, 23, 10, 202, 10, "Stalfos!",
     "Hey... listen... do you hear rattling? That's Stalfos. Skeletons that get back UP. In Duskwood they call "
     "them Skeletal Horrors, which is honestly a better name.$B$BBreak 10 of them. And then don't turn your back on "
     "the pieces.",
     "Destroy 10 Skeletal Horrors in Duskwood.", "Did they stay down? They never stay down.",
     "They stayed down! ...I think. Let's not go back to check."),
    (90508, 25, 11, 1034, 12, "The Shadow's Army",
     "Hey! Listen! The Dragonmaw orcs in the Wetlands march like an army. Armies need a dark lord. I don't like "
     "that one bit - the last army like that was Ganon's.$B$BBreak their raiding parties: 12 Dragonmaw Raiders.",
     "Slay 12 Dragonmaw Raiders in the Wetlands.", "Any sign of who leads them? A big guy? Red hair? Evil laugh?",
     "No dark lord. Good. GOOD. Just orcs. Orcs are fine. Orcs are manageable."),
    (90509, 28, 267, 2374, 10, "Not the Zora",
     "Hey! Listen! Those Torn Fin murlocs on the Hillsbrad coast are NOT Zora. The Zora are graceful and polite and "
     "have a princess. These have... mud.$B$BSend 10 Torn Fin Muckdwellers back into the sea.",
     "Slay 10 Torn Fin Muckdwellers in Hillsbrad Foothills.", "Mrglglgl? ...Sorry. They're catchy.",
     "Ahh, the coast smells like the coast again instead of like murloc. Thank you!"),
    (90510, 30, 45, 2559, 10, "Cucco Revenge",
     "Hey! Listen! Rule number one in Hyrule: never, EVER hit a Cucco. They come back with friends.$B$BThe Highland "
     "Striders in Arathi are just very big Cuccos. Someone hit one. Now there are a lot of angry big birds. Calm "
     "10 of them down. Permanently. Sorry, birds!",
     "Slay 10 Highland Striders in the Arathi Highlands.", "Are they flocking? Please tell me they're not flocking.",
     "No flock! We survived the Cuccos! That's more than most heroes can say."),
    (90511, 32, 45, 2562, 10, "Moblin Brutes",
     "Hey! Listen! You know how the gnolls were like Moblins? The Boulderfist ogres in Arathi are like BIG Moblins. "
     "Like, Moblins who ate other Moblins.$B$BKnock 10 of them down. Use the Spin Attack. I love the Spin Attack.",
     "Slay 10 Boulderfist Ogres in the Arathi Highlands.", "Did you spin? Tell me you spun.",
     "You spun! I saw it! Okay I didn't see it, I was behind you, but I FELT it."),
    (90512, 35, 33, 686, 10, "Lizalfos of the Jungle",
     "Hey! Listen! In Stranglethorn there are Lashtail Raptors. Fast, clever, they jump at you from the side - "
     "just like Lizalfos! Watch their tails, block with your shield, then strike!$B$BDefeat 10 of them.",
     "Slay 10 Lashtail Raptors in Stranglethorn Vale.", "Shield up! Shield UP!",
     "Look at you! Block, dodge, strike! You fight like a real Hylian now."),
    (90513, 38, 15, 4412, 10, "Skulltulas in the Marsh",
     "Hey! LISTEN! Skulltulas! In Dustwallow Marsh! The Darkfang Creepers drop down from the trees when you're not "
     "looking - that is exactly what Skulltulas do!$B$BClear out 10 of them. And look UP.",
     "Slay 10 Darkfang Creepers in Dustwallow Marsh.", "Did you look up? Always look up.",
     "That's ten! Somewhere a family is cured of a curse because of this. Probably!"),
    (90514, 40, 3, 92, 10, "The Armos Awaken",
     "Hey! Listen! In the Badlands the stones walk around by themselves. Back home we had statues like that - the "
     "Armos. You'd walk past and THUNK, they'd wake up.$B$BPut 10 Rock Elementals back to sleep.",
     "Destroy 10 Rock Elementals in the Badlands.", "Are they still walking? Stones shouldn't walk.",
     "Statues are statues again! My wings feel lighter already."),
    (90515, 42, 440, 5617, 8, "Thieves of the Desert",
     "Hey! Listen! The Wastewander bandits in Tanaris remind me of the Gerudo - sand, blades, and a fortress full of "
     "stolen treasure. Except the Gerudo had honor, and these just have knives.$B$BTheir Shadow Mages lead them. "
     "Defeat 8 Wastewander Shadow Mages.",
     "Slay 8 Wastewander Shadow Mages in Tanaris.", "Watch for the ones casting - they're the leaders!",
     "The desert is a little safer now. And you... you're almost ready. I can feel it. Linken's heartbeat is getting closer."),
]
for (_id, _lvl, _zone, _mob, _n, _title, _details, _obj, _req, _rew) in NAVI_ERRANDS:
    quest(id=_id, level=_lvl, min=_lvl, kind='', zone=_zone, giver=190601, ender=190601, title=_title,
          details=_details, objectives=_obj, request=_req, reward=_rew, kills=[(_mob, _n, None)], items=[],
          rep=(0, 0), prev=90501, next=0)

# Linken's Sword of Mastery becomes a legendary blade. It's Dangerous to Go Alone gives only its hilt;
# the light of every dungeon (their 24 Crystal Shards, shards.py - not the raids') binds it, and the
# Black Anvil in Blackrock Depths forges it. The core checks and takes the shards (more items than the
# quest log's four) and finishes the last quest at the anvil (ZeldaCommands.cpp, ZeldaGameObjectUse).
LINKEN_SWORD_ENTRY = 11902   # the Unfinished Sword of Mastery (build_mastery.py)
LINKEN_FINAL_QUEST = 3962
LINKEN_HILT = 190533
LINKEN_SHARD_BOUND_HILT = 190534
LINKEN = 8737
BLACK_ANVIL_GO = 191170       # a goober over the stock Black Anvil (172911), live while the quest is
BLACK_ANVIL_SPOT = (230, 895.10614, -273.56369, -71.88760, 2.3736467, 0.9271837, 0.3746071)
# the dungeons whose shards the sword takes (shards.py, every one but the raids)
DUNGEONS = ("Ragefire Chasm, Wailing Caverns, the Deadmines, Shadowfang Keep, Blackfathom Deeps, the Stockade, "
            "Gnomeregan, Razorfen Kraul, the four wings of the Scarlet Monastery (Graveyard, Armory, Cathedral and "
            "Library), Razorfen Downs, Uldaman, Zul'Farrak, Maraudon, the Sunken Temple, Blackrock Depths, "
            "Blackrock Spire, the three wings of Dire Maul (East, North and West), Stratholme and Scholomance")

quest(id=90520, level=58, min=55, kind='', zone=490, giver=LINKEN, ender=LINKEN, prev=LINKEN_FINAL_QUEST, next=90521,
      title='The Light of Every Dungeon',
      details="That hilt... I know it the way I know my own hands. It's all that's left of my sword.$B$BThe blade "
              "wasn't steel, $N. It was light - the light that gathers in the deep places of the world, where heroes "
              "go and come back changed. When I lost my way, the light went out of it.$B$BYou've walked those deep "
              "places. Every one you clear leaves a Crystal Shard behind. Bring me a shard from every dungeon in "
              "the land, and the hilt with them. Not the great raids - their light is too wild for a sword. Just "
              "the dungeons. All of them.",
      objectives="Bring the Hilt of the Sword of Mastery and a Crystal Shard from every dungeon to Linken in "
                 "Un'Goro Crater: " + DUNGEONS + ".",
      request="Every dungeon, $N. The light has to be whole, or the blade will be too.",
      reward="*Linken sets the shards around the hilt. One by one they dim, and the hilt begins to glow.*$B$BIt "
             "remembers. Can you feel it? The light knows where it belongs.$B$BBut no fire here could hold it. "
             "There's only one forge in the world that burns hot enough - and only one hammer it will answer to...",
      kills=[], items=[(LINKEN_HILT, 1)], reward_item=LINKEN_SHARD_BOUND_HILT, rep=(0, 0))

quest(id=90521, level=60, min=55, kind='dungeon', zone=1584, giver=LINKEN, ender=LINKEN, prev=90520, next=0,
      title='Reforged in the Black Anvil',
      details="The Black Anvil, deep in Blackrock Depths. The Dark Irons forge their master's weapons on it, in "
              "fire stolen from the Firelord himself. It's the only anvil in the world that can take that much "
              "light.$B$BBut it won't wake for just anyone. It answers only to Ironfoe - the hammer of the Dark "
              "Iron emperor, Dagran Thaurissan. Take it from him, hold it in your hand, and strike the hilt on the "
              "anvil. It will take time - half a minute of steady blows.$B$BAnd $N... the forge has guardians. When "
              "the blade wakes, so will they. Fall, and the forge keeps it. Go - it's dangerous to go alone, but "
              "you've never really been alone, have you?",
      objectives="Take Ironfoe from Emperor Dagran Thaurissan in Blackrock Depths. With Ironfoe in hand, use the "
                 "Black Anvil to reforge Linken's sword from the Shard-Bound Hilt, then defeat the forge's "
                 "guardians without falling.",
      request="Ironfoe in your hand, the hilt on the Black Anvil. And stay standing, $N.",
      reward="The blade is whole again. It sings, just like I remember.",
      kills=[], items=[(LINKEN_SHARD_BOUND_HILT, 1)], reward_item=LINKEN_SWORD_ENTRY, rep=(0, 0))
