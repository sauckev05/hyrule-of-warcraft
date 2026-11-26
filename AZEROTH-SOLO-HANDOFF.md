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
  (Zelda.EnemyMeleeDamageRate, now 4); see the 2026-10-24 notes for elites and dungeons.
- The red swing trail (a Heroic Strike SPELL_GO) is skipped for combo swings: its cast animation
  replaced the client-played combo swing.
- Charged attack by stance: Defensive Stance + shield = Shield Slam (spell 23922, damage = 75% of the shield
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
- Arena challenge (core ArenaUpdate in ZeldaCommands.cpp, content build_arena.py -> 014_arena.sql):
  Short John Mithril's Arena Grandmaster (7838) is twelve fights in the Gurubashi pit. Stage 1
  starts when a hero with no Arena Master trinket steps into the pit; later stages need 7838 taken
  (stage = trinkets + 1). Each stage spawns elite challengers (190960-190965, level = hero +
  bonus, health/damage scaled per stage, in batches), with champions on stages 4/7/9/11
  (190970-190972) and Grand Champion Zul'gor (190973) on 12. When all fall, the Arena Treasure
  Chest (179697, its loot always has an Arena Master) appears in the middle; once the trinket is
  looted a 10 s countdown starts the next stage. Leaving the pit or dying resets the run.
- Arena Grand Master (19024) has no use effect any more: when a blow would leave its wearer under
  10% health, Aura of Protection rises by itself and absorbs 750 (ZeldaModifyIncomingDamage,
  Zelda.ArenaGrandMasterCooldown 300 s).
- Navi heals 10% (Zelda.NaviHealPercent = 10) and her revive is custom spell 40009 "Navi's
  Light" (006 + patch-Z: clone of Use Soulstone 3026, 10% health/mana, resurrection visual 41).
- No chat window: ZeldaHUD chat.lua hides ChatFrame1-7, their tabs and the menu button, and
  shows skill-ups, system lines (not the hidden Z*: lines), loot, money, XP, reputation,
  whispers and NPC emotes in UIErrorsFrame in their chat colours. Enter still opens the chat box.
- Companion story rework (story.py): each girl hands the hero to the next at 30/40/50, and each
  chapter runs through her armor set's dungeons into raid attunements.
  Lyra: Deadmines 90102 ... Gath'Ilzogg 90105, Stockade 90112, Shadowfang 90113, -> Faelin 90114
  (30), Scarlet 90106, -> Helendis Riverhorn 90115 (50, starts the Onyxia chain 4182), LBRS 90107
  and UBRS 90108 at Morgan's Vigil, 90109 after The Great Masquerade (6403), Onyxia 90110 after
  Drakefire Amulet (6502), BWL 90111.
  Faelin (Astranaar): WC 90208, BFD 90203, RFK 90209, Gnomeregan 90210, -> Vesper 90211 (40);
  then Silithus 90205 (opens AQ) / AQ20 90206 / AQ40 90207 at Cenarion Hold. 90204 retired.
  Vesper (Sepulcher): SM Graveyard 90412, Library 90413, Armory 90414, Cathedral 90415, RFD 90403,
  -> Durza 90416 (50); Scholomance 90404, Stratholme 90405, -> Archmage Angela Dosantos 90417
  (casts 28006: the real Naxxramas flag 9378), Naxx 90406.
  Durza (Shadowprey): Uldaman 90309, ZF 90308, Maraudon 90303, Sunken Temple 90310, BRD 90304/90305
  at Kargath, -> Lothos Riftwaker 90311 (then the real Attunement to the Core 7848), Ragnaros
  90306. ZeldaAlternateQuestDone: BWL opens after 90110, Naxx after 90417, MC needs 7848.
- Stats (heroes all scale as warriors, Zelda.WarriorSpellStats): intellect gives spell power, 2 per
  point (Zelda.IntellectSpellPower; SpellBaseDamage/HealingBonusDone, magic schools); spirit gives
  spell crit at the warrior's agility-to-crit rate (UpdateSpellCritChance). Gear melee crit and hit
  (item-cast MOD_CRIT_PERCENT / MOD_HIT_CHANCE auras, any slot) also count for spells
  (Zelda.GearCritForSpells; ZeldaState.gearSpellCrit, m_modSpellHitChance). The Combat Stats panel
  shows Spell Power (ZSTATS field 11).
- Guard key (3): with a shield `.zshield on` raises it (80% less from the front, as before); with
  only a weapon it is a parry stance: every melee swing and melee ability from the front is parried
  (ZeldaParryHolds in RollMeleeOutcomeAgainst / MeleeSpellHitResult). Benilla `ZeldaGuardAnim(kind,
  held)` (creature_anim/zelda_swing.rs ZeldaGuard, driver.rs): a press plays ShieldBlock (24) or the
  weapon's parry (20-23); while held the clip stops at 40% (GUARD_POSE) and holds; release plays the
  rest, so a click plays the whole clip.
- Mana potions (spell category 4 with mana energize) give Potion Shield 40010 (absorb = the mana,
  20 s) instead of mana, drinkable at any mana (EffectEnergize, Spell::CheckCast); patch-Z rewrites
  the mana potion tooltips (DESCRIPTION_EDITS).
- Potion slot (ZeldaControls potion.lua): right-click a healing/mana potion in the bags to slot it
  (not drunk; not at vendor/bank/mail/AH/trade), key 6 (ZELDA_POTION, keys version 6) or a click
  drinks one; per-character in ZeldaControlsDB.potion.
- Mount slot (ZeldaControls mount.lua, key 7 ZELDA_MOUNT): right-click a mount item (generated list of
  every item whose spell has aura 78) to slot it; 7 sends `.zmount <item>` - the server dismounts
  when mounted, otherwise uses that bag item itself (CanUseItem, CastItemUseSpell).
- Key 8 (subscreen.lua ZELDA_INVENTORY): character sheet + all bags + key ring together. The key
  ring is always 16 slots (Benilla ui_items keyring_size; the server always had 16).
- Key 9 (ZELDA_SUBSCREEN): the Subscreen, one screen at a time - Spellbook, Talents, Quest Log,
  World Map, Main Menu - with a title bar; Left/Right arrows are rebound to ZELDA_SUB_PREV/NEXT
  while it is open (restored on close); 9 or Escape closes it. Keys version 7 adds 7/8/9 only.
- No action bar (ZeldaHUD actionbar.lua, enforced every 0.25 s): MainMenuBarArtFrame (art, micro
  and bag buttons), ActionButton1-12, the bonus/multi/pet bars are hidden; MainMenuExpBar sits at the
  bottom edge with ReputationWatchBar above it; ShapeshiftBarFrame is reparented under the buffs
  (TOPRIGHT -170, -125). Q / E (ZELDA_STANCE_PREV/NEXT, keys version 8) cycle the stances with wrap.
- Harder enemies: Zelda.EnemyMeleeDamageRate 4 (world normals), Zelda.EliteMeleeDamageRate 6 (tried 4 and 2 on 2026-11-21, back to 6; set in the PC mangosd.conf too; raids included since then). SoloCraft: since 2026-11-21 every dungeon and raid scales as a ten-player dungeon (ratio 0.5 in SoloCraftFactor), not by instance_template.maxPlayers
- 2026-11-20: every enemy blow and spell on the hero xN on top (Zelda.EnemyDamageRate; tried 3, 2, 1.5 - back to 1 = off, also set in the PC mangosd.conf): melee/ranged swings, weapon abilities, spells and DoTs; not raids, not Heavy Blow 40011 / Charged Bolt 40012 (ZeldaEnemyDamageMultiplier).
  (world elites/bosses), SoloCraft.DungeonHealth 0.65 / DungeonDamage 0.9 with raid exponents
  1.08 / 0.79 (raids as before). Heavy blows (ZeldaEnemyMechanics in ZeldaPlayerUpdate, one windup
  at a time per hero): enemies fighting the hero cast Heavy Blow 40011 (2 s Slam windup, dummy) in
  melee or, casters out of melee, Charged Bolt 40012; "winds up a heavy blow - raise your shield!"
  on screen. ZeldaHeavyBlowLands (EffectDummy): roll or out of reach = dodged; shield in front =
  blocked + 2 s stagger (7922); parry (melee) = parried + 1.5 s stagger; else 20/30/40% of max
  health (normal/elite/boss: Zelda.HeavyBlowNormal/Elite/Boss; boss = world boss or dungeon elite
  with HealthMultiplier >= 5) and a melee blow knocks down (5164). Intervals 14-20 / 9-14 / 7-10 s.
- Beedle: the 'end' spot beside each final boss is gone; where a creature spot 40-70 yd from the
  boss on its floor, on the way in, exists (16 dungeons/raids) Beedle stands there ('boss door'),
  elsewhere only the entrance and middle Beedles remain (dungeon_vendors.json, 004_vendors).
- No natural health regeneration for heroes, in or out of combat (Zelda.NaturalHealthRegen = 0,
  Player::RegenerateHealth skips the spirit regen); bandages, potions, food, Navi, set effects and
  health-regen auras from items still heal.
- Healing and mana potions: at most 10 of each kind, stacking to 10 (015_potion_limit.sql).
- Riding (016_mounts.sql): Apprentice Riding 400 g, regular mounts 50 g; epic training and mounts
  unchanged. Mount speeds (build_mastery MOUNT_SPEED, 006 + patch-Z Spell.dbc): every MOUNTED spell's
  MOD_INCREASE_MOUNTED_SPEED effect 2 goes 59 -> 149 (+150%) and 99 -> 199 (+200%).
- Reputation x10: Rate.Reputation.Gain = 10 (quests, kills); BattleGround::RewardReputationToTeam
  now follows the rate too.
- Honor: rank points never decay (Zelda.HonorRankDecay = 0, ObjectMgr::DistributeRankPoints), so
  ranks only go up.
- PvP rank rewards from rank 7 (requiredhonorrank >= 11, armor and weapons) are in
  zelda_removed_item (007_warrior_gear.sql, PVP_RANK_GEAR in build_warrior_gear.py): no vendor sells
  them, no loot or AH bot listing.
- Auction houses restock every in-game day (Zelda.AuctionDailyRestock, ZeldaGameDayIndex from
  Zelda.DayLengthMinutes): AuctionHouseBot::Update expires the bot's unbid auctions and refills
  (up to 900 sell passes).
- Pawnbroker Grizzle Pawnwick (190652, guids 9103101-7, npc_zelda_pawnbroker in
  zelda_companions.cpp, texts 902001/2): beside every potion goblin; gossip lists the newest 28 of
  everything sold since login (Player::AddItemToBuyBackSlot -> ZeldaRecordSold, keeps random
  property and permanent enchant), bought back for what the vendor paid; a normal buyback also
  takes it off the list; cleared at each login.
- Solo battlegrounds (Zelda.SoloBattlegrounds; ZeldaSoloBattleground in ZeldaPlayerUpdate, content
  build_battlegrounds.py -> 017_battlegrounds.sql): BattleGroundQueue starts in testing mode (one
  hero starts a battleground) and BattleGround::Update skips the premature finish. Inside, the
  cross-faction friendliness is lifted. Every 40-45 s each base sends a wave of elite soldiers
  (Stormpike 190980 / Frostwolf 190981, level = hero's) that march to the other base (their respawn
  coords are the enemy base, so after each fight they go on; idle ones are re-sent every 2 s), at
  most 32 alive. Warsong Gulch: Silverwing Warden 190982 / Warsong Warlord 190983 beside the flags;
  Arathi Basin: an Ironhide Brute 190984 (hostile to all) at each banner; guards come back 3 / 5 min
  after falling. Alterac Valley: waves from Vanndar to Drek'Thar and back, its own NPCs as usual.
- One-time gifts (Zelda.Gifts, default "Kale:6975"): Kale gets a Whirlwind Axe back (bags, else
  mail from Navi), marker gift:<item>.
- Potion goblin Fizzbang Bottlecork (190651, guids 9103001-7, build_vendors.py -> 004_vendors):
  healing and mana potions of every rank; beside Short John Mithril above the Gurubashi Arena pit,
  and between the alchemy vendors of the Stormwind, Ironforge, Darnassus, Orgrimmar, Thunder Bluff
  and Undercity alchemy shops.
- Armor set bonuses: new types 8 stun (% chance a melee hit stuns 1 s, Charge Stun 7922; not world
  bosses) and 9 weapon_flat (+N weapon damage via UNIT_MOD_DAMAGE_MAINHAND/OFFHAND TOTAL_VALUE, on
  the character sheet). Zora Scale (30): 2-piece +5 weapon damage, 6-piece 4% stun instead of
  knockback. Kokiri, Scarlet Crusade and Hylian Knight: their 5% weapon damage is +5 weapon damage.
  Set crit also counts as spell crit.

## What the Zelda layer does (current features)

Warrior-style combat for every class, Spin Attack with charge bar, boomerang, bow, shield
raise, dodge roll; run 1.3x, sprint 2x after 15 s running; faster swimming that slows as breath
runs out; Navi fairy companion (follows, 10% heal every 10 s in combat, self-revive at 10% every 5 min,
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

## Update 2026-11-25: Galahad, the young hero (installed)

- Kale was renamed **Galahad** once at startup (core `once:galahad`): face 0, hair style 6 (geoset 7)
  in golden blond 6, clean shaven, same skin. Config name lists (Zelda.Gifts etc.) say Galahad.
- Human male *players* wear display 17560 (`build_hero.py`): HumanMaleHero.m2 (slimmer/younger body B
  on the same skeleton; every cloak draws the split cape 1504, lengthened to mid-calf), CreatureModelData
  2400, CreatureSoundData 2300, SoundEntries 20000-20088 = the voice sped up 26% with reverb under
  Sound\Character\ZeldaHero; young face 0 in all skins (CharSections). ChrRaces human male -> 17560
  (client patch-Z and the server's data\dbc ChrRaces/CreatureDisplayInfo/CreatureModelData;
  backups in data\dbc-before-hero). NPC humans are unchanged. Benilla's roll grunt uses the new voice.
- Each new spur stack plays the mount's idle call (`zelda_mount_sound`, 025, `build_mount_sounds.py`).
- Journeyman Riding (200% mounts, spell 33392) costs 2000 gold (016).
- Tuned (installed 2026-11-25 evening): the voice is dry (no reverb); facial hair style 0 for human
  male players is a bare face (see-through FacialLower/UpperHairHeroNone.blp); attachment points
  follow the slim skin, shoulder pads at 0.78 and the helm at 1.08 (one-key global-sequence scale
  tracks on bones 83/84/87); display 17560 scale 0.93 (shorter). Backups: patch-Z.before-herotune.MPQ.bak,
  data\dbc-before-hero\CreatureDisplayInfo.before-herotune.dbc.
- Then (installed): display scale 0.90 and the head, hair and helm at 0.97 (HERO_SCALE / HERO_HEAD in
  build_hero.py). Backups: patch-Z.before-herohead.MPQ.bak, CreatureDisplayInfo.before-herohead.dbc.
- Then (installed): shoulder pads at 0.90 (SHOULDER_PAD_SCALE; 0.86 before). Backups: patch-Z.before-shoulders.MPQ.bak, patch-Z.before-shoulders15.MPQ.bak.
- Then (installed): shoulder pads back to 1.0 (normal size); gauntlet cuffs 402-404 and boot tops 502-504
  pushed out 15% from the limb axis (ARMOUR_BULK; 25% before). Backups: patch-Z.before-armour.MPQ.bak, patch-Z.before-armour15.MPQ.bak.
- Then (installed): the cuff/boot bulk undone (ARMOUR_BULK 1.0); shoulder pads stay at 1.0.
  Backup of the 15% version: patch-Z.before-armourback.MPQ.bak.
- Spur fix (installed 2026-11-25 night, commit 4aa59f73): Benilla no longer starts the forward roll's
  dash when key 5 is pressed on a mount (it held the mount to roll speed for 0.65 s each spur);
  spur circles sit just above the enemy charge-up bar (spur.lua, anchored to ZeldaTargetAnchor);
  one spur drops every 3 sec (ZELDA_SPUR_DECAY_MS 3000). Backups: mangosd.before-spurfix.exe,
  benilla.before-spurfix.exe, spur.lua.before-spurfix.bak.
- Key 5 (installed 2026-11-25 night, bf5f3f22): ZeldaControls tracks the held movement keys; key 5
  rolls that way (back = .zflip 5, left/right = .zroll l|r 5, else .zroll f 5); in the saddle any
  key-5 press spurs; one spur every 1.5 s at most (ZELDA_SPUR_COOLDOWN_MS).
- Double jump (installed 2026-11-25 night, 2f3d175d): Benilla relaunches at jump speed on a second
  jump press in the air (once a flight; not mounted/swimming), sending a JUMP; the hero plays clip 155
  (port_flip.py: the night elf male's flipping JumpStart retargeted onto the human male, from 100 ms)
  via ZeldaSwingAnim step 7. Also: the face smoothed harder (young_face v2) and a smaller pointed nose
  (NOSE in build_hero.py). Backups: patch-Z.before-doublejump.MPQ.bak, benilla.before-doublejump.exe.
  Patch-Z is built locally: rebuild_hero.py (installed patch-Z of 2026-11-25 + build_hero files).
- Cloak and eyes (installed 2026-11-25 late, da492698): every cape is the full cloak A1 (build_hero
  CAPE_STYLE 'full': 1502 over the backs of the shoulders, narrower under them, to 0.40); the nose
  reshape skips the eyes (only uv u<0.1, v<0.9); key 5 + A/D side-rolls only with the right mouse
  button held (IsMouselooking). Backups: patch-Z.before-cloak.MPQ.bak, ZeldaControls.lua.before-cloak.bak.
- Then (installed): cloak T1 (CAPE_SHOULDER 0.34, CAPE_PROFILE: a gentle waist taper widening to the
  hem; T2 was the stronger hourglass). Backup: patch-Z.before-T1.MPQ.bak.
- Now (installed 2026-11-25, e079e857): cloak T2 (CAPE_SHOULDER 0.32, CAPE_PROFILE half-widths
  0.22 → 0.17 at the waist → 0.46 at the hem). patch-Z md5 14ab2470…; backup of T1:
  patch-Z.before-T2.MPQ.bak (b05fc6fa…).
- Now (installed 2026-11-25, 82685d2a): the full cloak with a worn hem, a scarf and thinner shoulders.
  - W3 hem: CAPE_TATTER, 6 deep uneven tears; tips at CAPE_FULL_BOTTOM 0.10. The T2 shape is kept down
    to CAPE_PROFILE_BOTTOM 0.40, then flares on (CAPE_FLARE). The hem border keeps its scale (CAPE_BORDER_V).
  - S1 scarf: CAPE_COWL, two wraps round the neck under the helm, over the cape's yoke at the back.
    Weighted to bones 22/48 and drawn in the cloak's submesh with the cape's texture.
  - N1 shoulders: CAPE_SHOULDER 0.29; CAPE_PROFILE starts 0.20, waist 0.165.
  - Both extras are added by _cape_extras: new vertices appended, one shared triangle list, 1502 repointed.
  - patch-Z md5 fbe89d32…; backup: patch-Z.before-N1.MPQ.bak (T2, 14ab2470…).
- Now (installed 2026-11-25, 0abcf898): the F3 scarf and N3 shoulders. These replace the S1 scarf and N1 shoulders; the W3 hem stays.
  - The scarf is CAPE_COWL shape 'mound' (_mound_geometry). For each direction round the neck, a ring
    point is dropped onto the body or the cape yoke (the front stops at foot_min_z 1.56 on the chest).
    The cloth rises from there to a lip just under the helm. At its foot it takes that surface's bone
    weights, blending to 22/48 at the top.
  - Settings blend from front to back. The front has S1's two rolls (ridges, v_bands 2) in S1's colours;
    the back is wide like M3. The old roll shape is still in the code ('layers', _cowl_layer).
  - N3 shoulders: CAPE_SHOULDER 0.235; CAPE_PROFILE starts 0.17, waist 0.155.
  - patch-Z md5 79522d14…; backup: patch-Z.before-F3.MPQ.bak (N1 + S1, fbe89d32…).
- Now (installed 2026-11-25, 4ed799a4): N2 shoulders (CAPE_SHOULDER 0.26; CAPE_PROFILE starts 0.185, waist 0.16).
  The scarf's back now rises to top_z 1.82, neck (0.10, 0.085), up under the helm's back edge; F3's 1.77
  left the neck showing under some helms. patch-Z md5 6ff083fa…; backup: patch-Z.before-N2.MPQ.bak (N3 + F3, 79522d14…).
- Now (installed 2026-11-26, 7b0b17c0): spur sounds, the R2 scarf front, and the upper back kept under the cloak.
  - Spur sounds: each new red circle plays two sounds, both picked by circle number.
    - The mount's next attack sound: zelda_mount_attack in 025, from build_mount_sounds.py. Each file
      is its own single-file SoundEntries row (20200+) in patch-Z (mount_attack_sounds.json).
      Mounts with no attack sounds fall back to their zelda_mount_sound call.
    - The hero's grunt: ZELDA_SPUR_VOICES 20190-20192 (roll C, backflip A, side roll B).
  - Scarf front: R2, two soft round rolls (round 0.7, ridges 0.02).
  - Upper back: CAPE_COVER_BACK adds 1501's triangles to submesh 0. With a cape on, 1501 is hidden,
    and the cloak's yoke no longer covered that spot (a see-through gap).
  - Getting builds: the artifact blob host is blocked from both the cloud box and the PC. Take
    mangosd.exe from the azeroth-solo-latest release asset (gh api .../releases/assets/<id>, octet-stream).
  - md5s: patch-Z 733fcd19…, mangosd 6d1b6cf3…, 023 2f897425…, 025 3c79023e….
  - Backups: *.before-spursounds.* (patch-Z, mangosd.exe, 023/025 .sql.bak).
- Now (installed 2026-11-26, bfc55db8): L2 long tabard and a thinner scarf front.
  - Tabard: TABARD_LONG L2. Front hem at 0.20, back at 0.24, flare 0.3.
  - The front is slit from its second row (_tabard_geometry twins the middle vertices). With calm, the
    front hangs from the pelvis (21), not its swinging chain (24/52/67), and each half leans fully to
    its thigh (25/26) at the hem.
  - Scarf front thinner, same width: bulge 0.04, front_bulge 0.15, ridges 0.014/0.016.
  - Preview tip: tabard textures are palette BLPs with 8-bit alpha, which PIL misreads (tabtex/blp8.py).
  - patch-Z md5 405093d8…; backup: patch-Z.before-L2.MPQ.bak (733fcd19…).
