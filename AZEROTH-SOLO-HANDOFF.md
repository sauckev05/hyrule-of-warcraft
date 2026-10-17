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
  `build_warrior_gear.py` → 007_warrior_gear; 008_teleporters is hand-written;
  `build_blackfathom.py` → 009_blackfathom (needs a world dump without 009 applied).
  The server applies changed SQL files at startup.
- `solo-wow/tools/mpq.py`: pure-Python MPQ reader/writer used to build `patch-Z.MPQ`.
  `build_mastery.py` can rebuild patch-Z.MPQ from the DBCs inside an existing patch-Z.MPQ (it also
  clears Execute's target aura state so the client lets it be pressed on any target).

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
- Installed now: the 2026-10-17 build (see "Update 2026-10-16 evening" below). srv30 is kept as
  `server\mangosd.before-update.exe`.

## Update 2026-10-16 evening (installed)

- Rage gains halved from every source (`Zelda.RageGainRate`, 0.5; in Unit::ModifyPower).
- Kills inside dungeons and raids give half experience (`Zelda.DungeonXPRate`, 0.5; Player::GiveXP).
- Execute works on any target at full rage (`Zelda.FullRageExecute`); otherwise the server still
  wants the target under 20% (Spell::CheckCast). The client side is patch-Z.MPQ (Spell.dbc field 17).
- Two Kirin Tor portal mages (190670 Wizard's Sanctum basement, 190671 beside Archmage Ansirem
  Runeweaver outside sealed Dalaran) teleport between the two (008_teleporters).
- Blackfathom Deeps is level 30-35: enemies 30-34, bosses 31-35 (Aku'mai 35), world-drop tables of
  the new level, BFD-only boss drops raised by their boss's level change (009_blackfathom).
- Zora Treads (190716) drop from Aku'mai instead of Bazil Thredd; copies in bags/bank were removed
  once at startup (marker `once:zora-treads-bfd` in characters.ai_playerbot_db_store).
- Spin Attack always costs its full 50 rage: its own hits give no rage back (t_spinNoRage).
- Sword combo (Link's): right slash, left slash, special strike (Special1H/2H). The ZeldaControls
  addon keeps the combo count and lock (ZeldaControls_SwingTime: weapon speed x0.25, finisher
  x0.35) and sends `.zslash <step> <clientAnimates>`; the server (SlashDurationMs) enforces the same
  lock silently and sends the hits with HITINFO_NOACTION when the client animates. Benilla plays
  the swing via the `ZeldaSwingAnim(step, seconds)` Lua global (creature_anim/zelda_swing.rs; its
  per-race right/left variation table was measured from the 1.12 character models).
- Two-handed swings take 1.5x as long; the hero cannot move (turning allowed) while a swing plays
  (Benilla: ZeldaSwingHold read as a root in player/controller.rs). Slash/spin reach halved.
- Earlier ZeldaUpdate.zip (Sword of Mastery, warrior's world, Kokiri in the Stockade) is installed.

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
