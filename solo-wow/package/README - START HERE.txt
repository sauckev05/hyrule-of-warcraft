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

ELARA STARFALL, SYLWEN AND ZAGRA (AI-played characters who talk back)
  Sylwen (night elf hunter) and Zagra (orc shaman) start at the inn in Darnassus, level 25,
  and work just like Elara. Turn them off with Zelda.DarnassusBots = 0.
  Elara is a real level 25 human mage played by the bot AI. She travels, fights, quests and
  levels up on her own. To let her talk with her own personality she needs a local AI model:
    1. Install Ollama from https://ollama.com
    2. In a command window run:   ollama pull llama3.2:3b
       (a stronger PC can use qwen2.5:7b; then change "llama3.2:3b" in the LLMApiJson line
        of server\aiplayerbot.conf to match)
  Talk to her with /say when she is near, or whisper /w Elara anywhere. /invite Elara to travel
  together. She remembers your conversations, even after the server restarts.
  Her personality is in server\llm_character_card.txt (one line: Name::description).
  To remove her: Zelda.ElaraPlayerBot = 0 in mangosd.conf and AiPlayerbot.MinRandomBots = 0, MaxRandomBots = 0 in aiplayerbot.conf.

YOUR LEVEL 25 CHARACTERS
  The PLAYER account gets Ruuka (orc shaman), Morwenna (undead priest), Lianne (human priest)
  and Faelenna (night elf druid). They start at the Darnassus inn and become level 25 with
  their class spells on their first login (spend the talent points yourself).

ACCOUNTS
  PLAYER / PLAYER (normal)  -  ADMINISTRATOR / ADMINISTRATOR (game master)
  New account: in the world-server console window type   account create NAME PASSWORD

Your original realmlist.wtf is saved as realmlist.wtf.original in your WoW folder.
