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
            (190103, 'Darkshire', 28, (0, -10548.5, -1112.5, 31.5, 3.0), 2, (90103, 1), (90106, 1)),
            (190104, "Light's Hope Chapel", 55, (0, 2294.5, -5338.0, 90.9, 5.3), 2, (90106, 1), (90109, 0)),
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
            (190201, 'Auberdine', 15, (1, 6584.5, 489.0, 8.3, 2.5), 3, (0, 1), (90203, 0)),
            (190202, 'Astranaar', 30, (1, 2791.5, -296.0, 107.2, 5.5), 3, (90203, 0), (90205, 0)),
            (190203, 'Cenarion Hold', 58, (1, -6748.5, 827.0, 57.4, 3.5), 3, (90205, 0), (0, 1)),
        ]),
    'durza': dict(
        name='Durza Stormcaller', subname='Shaman of the Earthen Ring', display=3897, equipment=4049, unit_class=2,
        greeting="What. ...Sorry. Long day. Long YEAR. What do you want?",
        about="I'm Durza. My mother was the finest fire-speaker in Durotar. A fire spirit went mad and took her, "
              "and the elders said 'the elements are in balance'. BALANCE.$B$BNow the fire won't listen to me, the "
              "earth groans in Desolace and something under Blackrock Mountain is screaming. Everyone says I'm "
              "too angry.$B$B...Maybe. But someone has to find out who is making the elements suffer. And hit them.",
        stages=[
            (190301, 'Razor Hill', 12, (1, 282.5, -4720.5, 13.3, 5.0), 3, (0, 1), (90303, 0)),
            (190302, 'Shadowprey Village', 45, (1, -1588.5, 3076.0, 49.0, 3.0), 3, (90303, 0), (90304, 0)),
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
            (190401, 'Brill', 10, (0, 2258.0, 240.0, 33.7, 0.5), 3, (0, 1), (90403, 0)),
            (190402, 'The Sepulcher', 38, (0, 548.0, 1590.5, 130.1, 0.8), 2, (90403, 0), (90404, 0)),
            (190403, 'The Bulwark', 56, (0, 1764.5, -726.5, 60.0, 2.5), 2, (90404, 0), (90405, 0)),
            (190404, "Light's Hope Chapel", 60, (0, 2307.5, -5352.5, 91.7, 2.4), 2, (90405, 0), (0, 1)),
        ]),
    'elara': dict(
        name='Elara Starfall', subname='Wandering Mage', display=3292, equipment=5497, unit_class=8,
        faction=250, text_base=900700,     # friendly to every hero, at war with monsters
        greeting="Oh, hello! Elara Starfall, mage, adventurer, and occasional accidental arsonist. Lovely to meet you!",
        about="I'm a mage of the Stormwind Mage Quarter - well, technically I'm 'on sabbatical', which is what "
              "the Kirin Tor call it when you set fire to a library. A small library. A very flammable one.$B$B"
              "So now I walk! Goldshire, the Tower of Azora, Lakeshire, Darkshire, Sentinel Hill... I keep notes on "
              "everything: the rocks, the birds, the gnolls, the pie. Especially the pie.$B$BIf you ever want "
              "company on the road, just ask. I'm very good with fire. And with talking. Mostly with talking.",
        stages=[
            # she does not stay here: she roams between Goldshire, the Mage Quarter, the Tower of Azora,
            # Lakeshire, Darkshire and Sentinel Hill on her own (zelda_companions.cpp)
            (190701, 'Wandering', 25, (0, -9460.0, 62.0, 56.6, 1.5), 0, (0, 1), (0, 1)),
        ]),
}

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
      kills=[(334, 1, None)], items=[(190503, 1)], rep=(72, 250))

quest(id=90106, level=38, min=32, kind='dungeon', zone=10, giver=190103, ender=190103,
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
             "I'm going to Light's Hope Chapel in the Plaguelands to pray. When you are stronger, much stronger, "
             "come find me there. We'll finish this together.",
      kills=[(3977, 1, None)], items=[(190504, 1)], rep=(72, 350))

quest(id=90107, level=55, min=50, kind='dungeon', zone=139, giver=190104, ender=190104,
      title='Brood of the Black Spire',
      details="You came! I... I hoped you would. I've grown a little braver out here. The Argent Dawn let me "
              "help in the infirmary.$B$BI've been reading Scarlet letters for months. They all point to "
              "Blackrock Spire. Overlord Wyrmthalak commands the orcs of the lower spire, and he reports to "
              "someone in Stormwind.$B$BBring me his dispatches, $N. Every piece we find is a stone in the wall "
              "of truth.",
      objectives="Slay Overlord Wyrmthalak in Lower Blackrock Spire and bring his dispatch to Lyra at "
                 "Light's Hope Chapel.",
      request="Please be careful in the Spire. Dragons don't forgive.",
      reward="'The Lady's plans in Stormwind proceed. The whelps must be ready.'$B$BWhelps. Dragon whelps. "
             "$N... she's not a lady who works with dragons. She IS a dragon.$B$B*Lyra sits down very suddenly.*",
      kills=[(9568, 1, None)], items=[(190505, 1)], rep=(529, 250))

quest(id=90108, level=59, min=55, kind='dungeon', zone=139, giver=190104, ender=190104,
      title="The Champion's Blood",
      details="The old books say a black dragon's disguise can be broken by the blood of her own champion. "
              "In Upper Blackrock Spire, General Drakkisath commands the Black Dragonflight's guard.$B$BIf we "
              "bring his blood back, I can make a ward. A ward that shows what someone truly is.$B$BI'm going to "
              "Stormwind with it. I'm going to stand in front of the King. Me. Lyra Ashford. Who used to hide in "
              "the library.$B$B...Please get the blood before I lose my nerve.",
      objectives="Slay General Drakkisath in Upper Blackrock Spire and bring the Blood of the Black Champion "
                 "to Lyra at Light's Hope Chapel.",
      request="I've been practicing what to say to the King. I keep stammering on 'Your Majesty'.",
      reward="It's done. The ward is ready. It glows when I hold it near anything dragon-born.$B$BI'm ready "
             "too. I think. Let's go to Stormwind.",
      kills=[(10363, 1, None)], items=[(190506, 1)], rep=(529, 350))

quest(id=90109, level=60, min=58, kind='', zone=139, giver=190104, ender=190105,
      title='Unmasking the Lady',
      details="I'll go ahead to the Keep and wait by the throne with the ward hidden in my sleeve. Lady Prestor "
              "always stands at Bolvar's side.$B$BYou have to be the one to say it to her face, $N. She's afraid "
              "of you - I've seen how she watches you. If she reacts, the ward will blaze, and everyone will see.$B$B"
              "I'm not shaking. I'm... vibrating. With courage.",
      objectives="Confront Lady Katrana Prestor in Stormwind Keep, then speak with Lyra.",
      request="Did you... did you see her face?",
      reward="The ward blazed like the sun! Did you see it? Bolvar saw it. The guards saw it.$B$BShe just "
             "laughed, and called you a whelp, and walked out like she owned the city. Because she thinks she "
             "does.$B$BShe'll run to her lair. Take this - it is the amulet her own dragonkin carry to pass the "
             "fires of her nest. The Argent Dawn found it on Drakkisath's guard. It will let you follow her.",
      kills=[(1749, 1, 'Lady Katrana Prestor confronted')], items=[], reward_item=16309, rep=(72, 500))

quest(id=90110, level=60, min=58, kind='raid', zone=1519, giver=190105, ender=190105,
      title='The Brood Mother',
      details="Onyxia. That's her name. Daughter of Deathwing. She has whispered in Stormwind's ear for years.$B$B"
              "Her lair is in Dustwallow Marsh, south of Theramore. The amulet will carry you past the flames at "
              "the entrance.$B$BEnd it, $N. For Bolvar. For the Defias farmers who lost everything. For every "
              "shy girl who was told she was imagining things.",
      objectives="Slay Onyxia in her lair in Dustwallow Marsh, then return to Lyra in Stormwind Keep.",
      request="I can't stop looking at the empty spot beside the throne.",
      reward="It's over. It's really over.$B$B*Lyra hugs you, then immediately apologizes for hugging you.*$B$B"
             "Thank you, $N. You believed me when no one else did.",
      kills=[(10184, 1, None)], items=[], rep=(72, 1000))

quest(id=90111, level=60, min=60, kind='raid', zone=1519, giver=190105, ender=190105,
      title='Shadow Wings',
      details="I found something in Onyxia's chambers. Letters to her brother. 'Lord Victor Nefarius', who "
              "rules the top of Blackrock Spire. Nefarian.$B$BHe breeds monsters from the blood of every dragon "
              "flight in his lair above the Spire. Blackwing Lair. With Onyxia gone, he will be furious - and "
              "careless.$B$BThe way into his lair is through the orb in the Spire. It knows the scent of Onyxia's "
              "killer now. It will let you pass.",
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

quest(id=90203, level=26, min=20, kind='dungeon', zone=148, giver=190201, ender=190202,
      title='The Deeps Are Singing',
      details="'The deeps' - I figured it out! Blackfathom Deeps, the sunken temple on the Ashenvale coast. The "
              "cultists go there in boats at night.$B$BTheir leader is Twilight Lord Kelris, and they worship "
              "something called Aku'mai in the deepest pool. The Sentinels say Aku'mai is just a big hydra. I don't "
              "think a big hydra makes idols hum.$B$BI'm going ahead to Astranaar to sharpen arrows. Meet me "
              "there when it's done! ...Or I'll come in after you. I'm not good at waiting.",
      objectives="Slay Twilight Lord Kelris and Aku'mai in Blackfathom Deeps, then find Faelin in Astranaar.",
      request="You're back! You're wet! Tell me EVERYTHING.",
      reward="Kelris said WHAT before he died? 'The old ones stir beneath the sand'?$B$BSand. Sand, sand, "
             "sand... Tanaris? Silithus? Somewhere with a LOT of sand.$B$BI need maps. And snacks. Mostly maps.",
      kills=[(4832, 1, None), (4829, 1, None)], items=[], rep=(69, 350))

quest(id=90204, level=52, min=45, kind='dungeon', zone=331, giver=190202, ender=190202,
      title='Nightmare Beneath the Swamp',
      details="Okay, so I've been busy. Very busy. I found out the idols aren't just Twilight's Hammer junk - the "
              "druids say green dragons have been having nightmares, and something is feeding on their dreams.$B$B"
              "One of them, Eranikus, is trapped in the Sunken Temple in the Swamp of Sorrows. His shade is "
              "twisted by whatever is down there. If we free his shade and take a shard of his nightmare, the "
              "druids can trace where it comes from.$B$BYou're going, right? You're totally going.",
      objectives="Defeat the Shade of Eranikus in the Sunken Temple and bring a Nightmare Shard to Faelin "
                 "in Astranaar.",
      request="I tried to go myself. The druids sat on me. Literally. A bear sat on me.",
      reward="The druids traced the shard. The nightmare, the whispers, the idols... they all come from the "
             "same place. Far south. Under the sands of Silithus.$B$BThere's an old elven war buried there. "
             "Ahn'Qiraj. And something that never died.$B$B...I'm going. Of course I'm going. Meet me at Cenarion "
             "Hold!",
      kills=[(5709, 1, None)], items=[(190512, 1)], rep=(609, 350))

quest(id=90205, level=57, min=54, kind='', zone=1377, giver=190202, ender=190203,
      title='Silithid Rising',
      details="Cenarion Hold is AMAZING. Bugs the size of houses! Sand everywhere! The Twilight's Hammer has "
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

quest(id=90303, level=47, min=40, kind='dungeon', zone=14, giver=190301, ender=190302,
      title='Earth That Weeps',
      details="I've been training. Grimtusk says I'm 'less on fire'. I think that's a compliment.$B$BThe "
              "Earthen Ring sent word: the earth is sick in Desolace. Princess Theradras, daughter of the earth "
              "elemental lord, has poisoned the caverns of Maraudon. The elements are all being twisted at "
              "once, $N. Fire, earth... it's like someone is shaking the whole world.$B$BI'm going to Shadowprey "
              "Village. Meet me there after you deal with her. And bring a piece of that poisoned earth.",
      objectives="Defeat Princess Theradras in Maraudon and bring a Corrupted Earth Shard to Durza in "
                 "Shadowprey Village, Desolace.",
      request="The earth here cries at night. I can hear it. Can you?",
      reward="*Durza presses the shard to her forehead and closes her eyes.*$B$BIt's not the earth's fault. "
             "Something below Blackrock Mountain is pulling at all the elements like a whirlpool. Fire is "
             "loudest. The Firelord again.$B$BI'm not crying. The spirits are loud. That's all.",
      kills=[(12201, 1, None)], items=[(190522, 1)], rep=(76, 350))

quest(id=90304, level=54, min=50, kind='dungeon', zone=405, giver=190302, ender=190303,
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
      reward="The brand burns cold in my hand. It knows we're coming.$B$BThe Molten Core is open to us now, $N. "
             "When you're ready - and only when you're ready - we go down.",
      kills=[(9019, 1, None)], items=[(190523, 1)], rep=(76, 750))

quest(id=90306, level=60, min=60, kind='raid', zone=3, giver=190303, ender=190303,
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

quest(id=90403, level=40, min=33, kind='dungeon', zone=85, giver=190401, ender=190402,
      title='Cold Words in the Downs',
      details="Amnennar the Coldbringer. A lich of the Scourge, nesting among the quilboar of Razorfen Downs in "
              "the southern Barrens. He spreads the plague to the quilboar and raises them in the Lich King's "
              "name.$B$BBring me a fragment of his phylactery. I'm moving to the Sepulcher in Silverpine - the "
              "air is better. Mustier. More atmospheric.$B$BDo be careful. Liches are terribly rude.",
      objectives="Defeat Amnennar the Coldbringer in Razorfen Downs and bring a Phylactery Fragment to Vesper "
                 "at the Sepulcher in Silverpine Forest.",
      request="The Sepulcher's bats have names now. I named them. Don't tell anyone.",
      reward="*The fragment frosts Vesper's fingers. She doesn't seem to notice.*$B$BHe was a messenger. "
             "His phylactery hums with a single name: Kel'Thuzad. The Lich King's favorite servant. He hides in "
             "a floating citadel, they say, high above the Plaguelands.$B$BI am going to find him. And when I do, "
             "I am going to be VERY polite. Right up until the end.",
      kills=[(7358, 1, None)], items=[(190532, 1)], rep=(68, 350))

quest(id=90404, level=58, min=52, kind='dungeon', zone=130, giver=190402, ender=190403,
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
      kills=[(10440, 1, None)], items=[], rep=(529, 1000))

quest(id=90406, level=60, min=60, kind='raid', zone=139, giver=190404, ender=190404,
      title='The Lich in the Sky',
      details="Naxxramas. Kel'Thuzad waits in its frozen heart, beyond the spider wing, the plague wing, the "
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
         description="Equip: Navi follows you. In combat she heals you for 25% of your health every 10 sec. "
                     "If you die, she can bring you back (once every 5 min). Hey! Listen!"),
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

# Linken's Sword of Mastery becomes a legendary blade and It's Dangerous to Go Alone gives only it.
LINKEN_SWORD = dict(entry=11902, quality=5, dmg_min=120, dmg_max=160, delay=2600, item_level=70,
                    stats=[(3, 15), (4, 15), (5, 15), (6, 15), (7, 15)],   # agility, strength, intellect, spirit, stamina
                    holy_spell=25912, holy_ppm=2.0,                         # Holy Shock (damage); the server sets 75-150 and heals as much
                    extra_attack_spell=15494, extra_attack_ppm=1.15,        # 2 extra attacks, about 5% of swings at 2.60 speed
                    durability=125)
LINKEN_FINAL_QUEST = 3962
