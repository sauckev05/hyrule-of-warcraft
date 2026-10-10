# Hyrule of Warcraft

Ocarina of Time's engine, movement and combat (via [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright), the PC port of the [zeldaret/oot](https://github.com/zeldaret/oot) decompilation), with World of Warcraft style RPG systems layered on top:

- Levels 1–60 with XP from kills, quests and zone discovery
- Strength / Agility / Stamina / Spirit / Armor, crits, level-difference combat math
- Enemy levels and nameplates with WoW con colors, target frame, floating combat text, chat/combat log
- Loot with WoW rarities, 8 gear slots, 20-slot backpack, vendor junk
- 30+ quests across child and adult Link, quest tracker, `!`/`?` quest markers
- Dungeons and a raid (Ganon's Castle) with Normal / Heroic / Mythic difficulty — all soloable
- Talents (Courage / Wisdom / Power trees) and professions (Herbalism, Mining, Skinning, Alchemy, Blacksmithing, Leatherworking)

All of the new code lives in `soh/soh/Enhancements/Azeroth/` plus two small hooks in `z_collision_check.c` and `z_player.c`.

## Getting the game (Windows)

1. Open the **Actions** tab of this repository and click the latest green **build-windows** run.
2. Download the **HyruleOfWarcraft-Windows** artifact at the bottom of the page and unzip it.
3. Run `soh.exe` and point it at your own Ocarina of Time ROM the first time. See `HOW TO PLAY.txt`.

No game assets are included in this repository. They are extracted from your own ROM on first launch.
