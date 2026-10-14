AZEROTH SOLO - World of Warcraft 1.12.1, offline and single-player
==================================================================

Everything runs on your own PC. No internet needed after downloading this folder.

1) FIRST TIME: double-click SETUP.bat
   - Finds your WoW 1.12.1 folder (it checks E:\wow\New folder\SoloCraft 1.12.1 first,
     otherwise it asks you to pick the folder that contains WoW.exe).
   - Builds the database (a few minutes).
   - Extracts maps from YOUR client files (10-30 minutes), and optionally movement maps
     (30-90 minutes, recommended). You can leave it running.
   - Points your client at your own PC and makes an "Azeroth Solo" desktop shortcut.

2) TO PLAY: double-click PLAY.bat (or the desktop shortcut)
   - Starts the database, login server and world server, then opens WoW.
   - Log in with   Account: PLAYER   Password: PLAYER
   - When you quit WoW, the servers save and shut down by themselves.
     (Use "Exit Game" in the WoW menu so your character is saved cleanly.)

3) STOP.bat stops all servers if something was left running.

SOLO-FRIENDLY DUNGEONS AND RAIDS (SoloCraft)
  Monsters inside instances are scaled for one player:
    5-player dungeons   ~45% health, ~55% damage
    10-player (UBRS)    ~24% health, ~37% damage
    20-player (ZG/AQ20) ~13% health, ~26% damage
    40-player raids     ~7% health,  ~17% damage
  Raids stay the hardest content. To change the difficulty, edit the SoloCraft.* lines at the
  end of server\mangosd.conf (lower = easier, SoloCraft.Enable = 0 = original group difficulty).

PLAYERBOT COMPANIONS (optional)
  A few raid bosses have mechanics that need more than one person. Bring AI companions:
  create extra characters on the PLAYER account, then in game type
     .bot add <CharacterName>        (logs that character in as a bot)
     /invite <CharacterName>         (invite it to your party)
  Bots follow you, fight and heal. Whisper "help" to a bot for its commands.

THE SWORD OF MASTERY
  Linken's quests reward the Unfinished Sword of Mastery (epic, Quel'Serrar's blade with a blue
  glow). Use it while you carry Quel'Serrar to forge both into the legendary Sword of Mastery.
  Its look and tooltips need patch-Z.MPQ in your WoW Data folder (made by build_mastery.py).

YOUR LEVEL 25 CHARACTERS
  The PLAYER account gets Ruuka (orc shaman), Morwenna (undead priest), Lianne (human priest)
  and Faelenna (night elf druid). They start at the Darnassus inn and become level 25 with
  their class spells on their first login (spend the talent points yourself).

ACCOUNTS
  PLAYER / PLAYER (normal)  -  ADMINISTRATOR / ADMINISTRATOR (game master)
  New account: in the world-server console window type   account create NAME PASSWORD

Your original realmlist.wtf is saved as realmlist.wtf.original in your WoW folder.
