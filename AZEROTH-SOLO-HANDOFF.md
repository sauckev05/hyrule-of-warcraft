# Azeroth Solo / Zelda of Warcraft — handoff for a new Claude chat

Paste this into a new chat (or point it at this file in the repo) to continue the project.
Written 2026-10-16. The previous chat lost its link to the PC after Claude was reinstalled.

## What this is

Two linked projects in the GitHub repo **sauckev05/hyrule-of-warcraft**:

- **Azeroth Solo** (`solo-wow/`): an offline, single-player WoW 1.12.1 server for Windows —
  CMaNGOS Classic + Playerbots + SoloCraft scaling, portable MariaDB, one-click scripts.
- **Zelda of Warcraft**: Zelda-style gameplay built into that server (core C++ patch + world
  database content + addons), played with the **Benilla** client (Rust, `zelda-wow/benilla`).

## How it is built (CI, GitHub Actions)

- `build-solo-wow.yml` (runs on push to `solo-wow/**`): jobs **server** (Windows, builds
  mangosd from CMaNGOS + `solo-wow/patches/solocraft.patch`), **database** (loads every
  `solo-wow/content/zelda-sql/*.sql` into a real world DB; fails on any SQL error) and
  **package**. Publishes release **azeroth-solo-latest**, asset `AzerothSolo-Windows.zip`.
  Pinned: CMANGOS_SHA 8ec338a1, PLAYERBOTS_SHA da4419af, CLASSICDB_SHA ec4f5961.
- Compile errors are pushed to branch `ci-logs-solo` (`errors.txt`); SQL errors to `ci-logs-solo-db`.
- `build-zelda-wow.yml`: builds the Benilla client, release **zelda-wow-latest** (`ZeldaWoW-Windows.zip`).
- Core changes: work in a CMaNGOS checkout at CMANGOS_SHA with the patch applied, then export
  with `git add -A && git diff --cached > solo-wow/patches/solocraft.patch`.
- Main Zelda core files: `src/game/Chat/ZeldaCommands.cpp/.h`,
  `src/game/AI/ScriptDevAI/scripts/world/zelda_companions.cpp`, plus hooks in Player.cpp,
  Unit.cpp, Creature.cpp, Spell*.cpp, LootMgr, World.cpp, AuctionHouseBot.cpp.
- Content generators (`solo-wow/content/`, Python) write `zelda-sql/`:
  `build_content.py`+`story.py` → 001_companions; `build_sets.py`+`sets.py` → 002_sets (+ ZeldaHUD
  setsdata.lua); `build_reagents.py` → 003; `build_vendors.py` → 004; 005_hosiery is now a
  removal script; `build_mastery.py` → 006_mastery (+ client patch-Z.MPQ);
  `build_warrior_gear.py` → 007_warrior_gear. The server applies changed SQL files at startup.
- `solo-wow/tools/mpq.py`: pure-Python MPQ reader/writer used to build `patch-Z.MPQ`.

## The PC (Windows, GTX 1060 6 GB)

- Everything is under `E:\wow\New folder\`:
  - `AzerothSolo\` — server: `server\mangosd.exe`, `server\mangosd.conf`, `server\aiplayerbot.conf`,
    `server\zelda-sql\`, `mariadb\`, `mariadb-data\`, `PLAY.bat`, `STOP.bat`, `UPDATE.bat`
  - `SoloCraft 1.12.1\` — the game client (patch files go in `Data\`)
  - `ZeldaWoW\benilla.exe` — the Benilla client; its addons are in `ZeldaWoW\benilla-config\AddOns\`
  - `_download\srvNN\` — downloaded server builds (UPDATE.bat copies the newest)
- Accounts: PLAYER (normal), ADMINISTRATOR (GM). Characters on PLAYER: **Kale** (main),
  **Ruuka** (orc shaman), **Morwenna** (undead priest), **Lianne** (human priest),
  **Faelenna** (night elf druid) — the four become level 25 with class spells on first login.
- Installed now: server build srv30 (mangosd md5 dc0c7df7...).

## Pending: not installed yet

`ZeldaUpdate.zip` (sent in the old chat; same files are in release azeroth-solo-latest):
stop the server, extract it into `E:\wow\New folder`, run `ZeldaUpdate\INSTALL.bat`. It installs:

1. **Sword of Mastery**: Linken's Sword of Mastery → epic *Unfinished Sword of Mastery*
   (Quel'Serrar's blade with a blue glow); using it while carrying Quel'Serrar forges the
   legendary *Sword of Mastery* (item 191001: Grand Marshal's Longsword look, 138-207 / 2.90,
   +25 all stats, 2% hit and crit for melee and spells, holy strike + heal 150-300, ~15% two
   extra attacks). Custom spells 40001-40007. Needs `patch-Z.MPQ` in the client's Data folder.
2. **Warrior's world**: ~5,800 items no longer drop, sell, reward, get taught or appear on
   the AH bot — raid-only items (Quel'Serrar kept), cloth (not cloaks/shirts) and leather,
   mail from level 40, staves, wands, relics, other classes' gear. Owned copies stay.
   Table `zelda_removed_item` holds the list.
3. **Kokiri Spaulders / Leggings** now drop in the Stockade (Targorr the Dread, Kam Deepfury).

## What the Zelda layer does (current features)

Warrior-style combat for every class, Spin Attack with charge bar, boomerang, bow, shield
raise, dodge roll; run 1.3x, sprint 2x after 15 s running; faster swimming that slows as breath
runs out; Navi fairy companion (follows, 25% heal every 10 s in combat, self-revive every 5 min,
level-gated errand quests 90501-90515 with scaling rewards); four story companions (Lyra,
Faelin, Durza, Vesper) with quest chapters; four dungeon armor sets (levels 20/30/40/50,
100% boss drops, 2/3/6-piece bonuses: crit, crit damage, weapon damage, knockback, extra swing,
spin rage, heal on kill); heart pieces; Beedle vendors that repair inside dungeons and raids;
auto-sell junk and white gear at vendors; dungeon death releases you alive at the entrance at
5% health; dungeons reset when you leave; gathering loot x5, ore veins mine once; crafting
needs only your own profession's reagents; cross-faction friendly; auto-loot; bonus BoE in
treasure chests; quest items always drop. Settings are the `Zelda.*` lines in mangosd.conf.

## Removed on purpose (do not bring back)

The hosiery boutique and items (190900-190949, vendor 190660), and the AI-played characters
(Elara, Sylwen, Zagra, bot accounts RNDBOT0-2) with their Ollama/LLM chat. The server deletes
any leftovers at startup. AI chat is off (`AiPlayerbot.LLMEnabled = 0`); Ollama is still
installed on the PC with models in `E:\.ollama` (unused).

## Open items

- Lag / distorted view while running and turning the camera in Benilla: never diagnosed.
- Ideas discussed, not started: a custom raid built on an existing map (e.g. a Zelda-style
  temple on a copied dungeon map), and recolored item looks via patch-Z.MPQ.
