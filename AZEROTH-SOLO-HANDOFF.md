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
  `build_dungeons.py` → 009_blackfathom and 011_wailing_caverns (needs a world dump without them);
  010_dungeon_teleports is generated once from mmaps-checked spots (see its header).
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
- Two-handed swings take 1.5x as long. Flurry no longer hastes a hero's auto attack; instead every
  combo swing is its percentage faster (ZeldaFlurryPercent / the addon's FlurryPercent). Slash/spin
  reach halved. (Standing still while swinging was tried and removed.)
- Normal and rare (non-elite) enemy creatures' melee/ranged attacks on heroes hit 3x
  (Zelda.EnemyMeleeDamageRate); elites/bosses unchanged. In dungeons SoloCraft's 0.55 still applies.
- The red swing trail (a Heroic Strike SPELL_GO) is skipped for combo swings: its cast animation
  replaced the client-played combo swing.
- Charged attack by stance: Defensive Stance + shield = Shield Slam (spell 23922, damage = shield
  armor) on enemies in front + 2 s stun (Charge Stun 7922, duration overridden); Berserker Stance =
  Leaping Strike (custom spell 40008 in 006_mastery/patch-Z, melee class, damage 2x attack power) on
  one enemy in front, the client playing Special2H (ZeldaSwingAnim step 4); otherwise Spin Attack.
- ZeldaHUD stats.lua: a Combat Stats panel beside the character sheet, filled from `.zstats`
  (server reply "ZSTATS:..." hidden from chat).
- Innkeeper dungeon list (gossip menu 50238): each entry teleports to that dungeon's meeting
  stone (dbscripts_on_gossip 900700-900718); WC/BFD list conditions follow their new levels.
- Wailing Caverns is level 28-33 (Mutanus 33), loot scaled; Zora Fin Pauldrons drop from Mutanus
  (moved from Agathelos, Razorfen Kraul).
- Wailing Caverns event fix (core, wailing_caverns.cpp): the Disciple's JustRespawned marks his event FAIL on spawn, so the intro (a /say at the entrance) never played; now each Fanglord death shows "Fanglords slain: N of 4" and the fourth tells every player to return to the Disciple at the entrance. The instance script also counts Fanglord deaths itself (OnCreatureDeath) besides their EventAI.
- Dungeon clears (core ZeldaClear*, content shards.py -> 012_dungeon_clears.sql + patch-Z): every
  dungeon/raid (SM and Dire Maul per wing, by position boxes in `zelda_dungeon_clear`) counts the
  hostile DB-spawned creatures it actually spawned (all its grids are force-loaded at instance
  creation; dead-on-load ones from saved respawn times). Killed creatures never respawn there
  (Zelda.DungeonNoRespawn, 30-day respawn). A counted enemy despawned alive counts as beaten.
  The client gets "ZDUNGEON:killed;total;name;raid" (hidden), ZeldaHUD dungeon.lua draws the bar
  under the minimap; click = `.zdungeon left` (nearest enemies still standing). 100% gives
  "Crystal Shard of <name>" (items 191100-191130, rare for dungeons, epic for raids, icons
  INV_Zelda_Shard_N in patch-Z, mail from Navi when bags are full), once per character
  (ai_playerbot_db_store key shard:<item>). One-time `once:retro-shards` mailed DM, Stockade,
  SFK, BFD, WC, RFK and Gnomeregan shards to the PLAYER account's non-hero characters.
- Dungeon map: inside a dungeon/raid, M (ToggleWorldMap, overridden in dungeon.lua) opens a big
  square map: a second Minimap frame (ZeldaDungeonMapView) and the Lua call ZeldaDungeonMap(on,
  zoom) put Benilla's minimap renderer in big mode (minimap/mod.rs ZeldaBigMap: radius 320/220/
  150/100 yd indoors, 1024 composite target, square mask, portal flood limited to the hero's
  floor, blips at corner-map size). MinimapCluster is hidden while it is open.
- Stances (warriors, Zelda.StanceWeapons): Berserker Stance Passive 7381 is +10% crit (006 +
  patch-Z). Taking Berserker Stance equips the best two-hander from the bags (or empties the
  hands); Defensive takes the best one-hander + shield (keeps a one-hander when there is no
  shield). Player::CanEquipItem refuses other weapons/shields in those stances
  (ZeldaStanceEquipBlocked). Leaping Strike now hits every enemy in front.
- Dual wield: the main hand deals half damage too (Zelda.DualWieldDamage, in
  Player::CalculateMinMaxDamage); the off hand keeps vanilla's 50%.
- Navi (190601) makes no creature sounds in Benilla (sound/mod.rs ZELDA_SILENT_ENTRIES).
- Personal crest (013_crest.sql, GuildHandler.cpp, ZeldaSetPersonalCrest, ZeldaHUD crest.lua, Benilla
  ui_tabard.rs TabardDesign.1): tabard vendors' option reads "Create crest."; without a guild the
  designer saves (10 g) a crest of one's own (ai_playerbot_db_store key 'crest'), sent to the client
  as hidden "ZCREST:a;b;c;d;e" (also on `.zcrest`, asked at world entry); Benilla paints it on our
  own tabard when we have no guild emblem. Guild Tabard 5976 is the Universal Tabard, 250 g.
- Installed 2026-10-23 (commit 31e5df44): benilla.exe, mangosd.exe, patch-Z.MPQ (2,038,192 bytes),
  ZeldaHUD dungeon.lua/toc, zelda-sql 006 + 012; backups *.before-clears.exe.
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
