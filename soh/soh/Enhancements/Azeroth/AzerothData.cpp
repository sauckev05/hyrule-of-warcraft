#include "AzerothInternal.h"

#include <unordered_map>
#include <cmath>
#include <algorithm>
#include "soh/ActorDB.h"
#include "soh/Enhancements/game-interactor/GameInteractor.h"

extern "C" {
#include "z64.h"
#include "functions.h"
#include "macros.h"
}

namespace Azeroth {

// ---------------------------------------------------------------------------------------------------------------
// Zones: WoW style level ranges for every area. {name, childMin, childMax, adultMin, adultMax}
// ---------------------------------------------------------------------------------------------------------------
static const std::unordered_map<int16_t, ZoneInfo> sZones = {
    { SCENE_KOKIRI_FOREST, { "Kokiri Forest", 1, 3, 22, 24 } },
    { SCENE_LINKS_HOUSE, { "Kokiri Forest", 1, 3, 22, 24 } },
    { SCENE_DEKU_TREE, { "Inside the Deku Tree", 2, 5, 2, 5 } },
    { SCENE_DEKU_TREE_BOSS, { "Inside the Deku Tree", 6, 6, 6, 6 } },
    { SCENE_LOST_WOODS, { "Lost Woods", 3, 6, 22, 26 } },
    { SCENE_SACRED_FOREST_MEADOW, { "Sacred Forest Meadow", 4, 7, 23, 27 } },
    { SCENE_HYRULE_FIELD, { "Hyrule Field", 4, 8, 20, 26 } },
    { SCENE_LON_LON_RANCH, { "Lon Lon Ranch", 4, 6, 20, 22 } },
    { SCENE_MARKET_ENTRANCE_DAY, { "Castle Town", 5, 6, 5, 6 } },
    { SCENE_MARKET_ENTRANCE_NIGHT, { "Castle Town", 5, 6, 5, 6 } },
    { SCENE_MARKET_ENTRANCE_RUINS, { "Ruins of Castle Town", 25, 28, 25, 28 } },
    { SCENE_MARKET_DAY, { "Castle Town", 5, 6, 5, 6 } },
    { SCENE_MARKET_NIGHT, { "Castle Town", 5, 6, 5, 6 } },
    { SCENE_MARKET_RUINS, { "Ruins of Castle Town", 25, 28, 25, 28 } },
    { SCENE_BACK_ALLEY_DAY, { "Castle Town", 5, 6, 5, 6 } },
    { SCENE_BACK_ALLEY_NIGHT, { "Castle Town", 5, 6, 5, 6 } },
    { SCENE_TEMPLE_OF_TIME_EXTERIOR_DAY, { "Temple of Time", 5, 6, 5, 6 } },
    { SCENE_TEMPLE_OF_TIME_EXTERIOR_NIGHT, { "Temple of Time", 5, 6, 5, 6 } },
    { SCENE_TEMPLE_OF_TIME_EXTERIOR_RUINS, { "Temple of Time", 25, 28, 25, 28 } },
    { SCENE_TEMPLE_OF_TIME, { "Temple of Time", 5, 6, 20, 20 } },
    { SCENE_HYRULE_CASTLE, { "Hyrule Castle", 5, 7, 5, 7 } },
    { SCENE_CASTLE_COURTYARD_GUARDS_DAY, { "Hyrule Castle", 5, 7, 5, 7 } },
    { SCENE_CASTLE_COURTYARD_GUARDS_NIGHT, { "Hyrule Castle", 5, 7, 5, 7 } },
    { SCENE_CASTLE_COURTYARD_ZELDA, { "Hyrule Castle", 5, 7, 5, 7 } },
    { SCENE_KAKARIKO_VILLAGE, { "Kakariko Village", 6, 9, 26, 28 } },
    { SCENE_HOUSE_OF_SKULLTULA, { "Kakariko Village", 6, 9, 26, 28 } },
    { SCENE_GRAVEYARD, { "Kakariko Graveyard", 7, 10, 28, 31 } },
    { SCENE_WINDMILL_AND_DAMPES_GRAVE, { "Kakariko Graveyard", 7, 10, 28, 31 } },
    { SCENE_REDEAD_GRAVE, { "Kakariko Graveyard", 8, 11, 28, 31 } },
    { SCENE_ROYAL_FAMILYS_TOMB, { "Royal Family's Tomb", 9, 11, 29, 31 } },
    { SCENE_BOTTOM_OF_THE_WELL, { "Bottom of the Well", 26, 30, 26, 30 } },
    { SCENE_DEATH_MOUNTAIN_TRAIL, { "Death Mountain Trail", 8, 11, 28, 31 } },
    { SCENE_GORON_CITY, { "Goron City", 9, 11, 28, 30 } },
    { SCENE_DEATH_MOUNTAIN_CRATER, { "Death Mountain Crater", 12, 14, 32, 35 } },
    { SCENE_DODONGOS_CAVERN, { "Dodongo's Cavern", 10, 14, 10, 14 } },
    { SCENE_DODONGOS_CAVERN_BOSS, { "Dodongo's Cavern", 15, 15, 15, 15 } },
    { SCENE_ZORAS_RIVER, { "Zora's River", 12, 15, 30, 33 } },
    { SCENE_ZORAS_DOMAIN, { "Zora's Domain", 14, 16, 40, 42 } },
    { SCENE_ZORAS_FOUNTAIN, { "Zora's Fountain", 15, 17, 40, 43 } },
    { SCENE_JABU_JABU, { "Jabu-Jabu's Belly", 15, 19, 15, 19 } },
    { SCENE_JABU_JABU_BOSS, { "Jabu-Jabu's Belly", 20, 20, 20, 20 } },
    { SCENE_LAKE_HYLIA, { "Lake Hylia", 16, 18, 38, 42 } },
    { SCENE_LAKESIDE_LABORATORY, { "Lake Hylia", 16, 18, 38, 42 } },
    { SCENE_FISHING_POND, { "Lake Hylia", 16, 18, 38, 42 } },
    { SCENE_FOREST_TEMPLE, { "Forest Temple", 24, 28, 24, 28 } },
    { SCENE_FOREST_TEMPLE_BOSS, { "Forest Temple", 30, 30, 30, 30 } },
    { SCENE_FIRE_TEMPLE, { "Fire Temple", 32, 36, 32, 36 } },
    { SCENE_FIRE_TEMPLE_BOSS, { "Fire Temple", 38, 38, 38, 38 } },
    { SCENE_ICE_CAVERN, { "Ice Cavern", 38, 41, 38, 41 } },
    { SCENE_WATER_TEMPLE, { "Water Temple", 41, 45, 41, 45 } },
    { SCENE_WATER_TEMPLE_BOSS, { "Water Temple", 46, 46, 46, 46 } },
    { SCENE_SHADOW_TEMPLE, { "Shadow Temple", 46, 50, 46, 50 } },
    { SCENE_SHADOW_TEMPLE_BOSS, { "Shadow Temple", 51, 51, 51, 51 } },
    { SCENE_GERUDO_VALLEY, { "Gerudo Valley", 18, 20, 44, 46 } },
    { SCENE_CARPENTERS_TENT, { "Gerudo Valley", 18, 20, 44, 46 } },
    { SCENE_GERUDOS_FORTRESS, { "Gerudo's Fortress", 44, 47, 44, 47 } },
    { SCENE_THIEVES_HIDEOUT, { "Thieves' Hideout", 44, 47, 44, 47 } },
    { SCENE_GERUDO_TRAINING_GROUND, { "Gerudo Training Ground", 48, 52, 48, 52 } },
    { SCENE_HAUNTED_WASTELAND, { "Haunted Wasteland", 47, 50, 47, 50 } },
    { SCENE_DESERT_COLOSSUS, { "Desert Colossus", 20, 22, 48, 51 } },
    { SCENE_SPIRIT_TEMPLE, { "Spirit Temple", 22, 26, 52, 56 } },
    { SCENE_SPIRIT_TEMPLE_BOSS, { "Spirit Temple", 57, 57, 57, 57 } },
    { SCENE_OUTSIDE_GANONS_CASTLE, { "Outside Ganon's Castle", 56, 58, 56, 58 } },
    { SCENE_INSIDE_GANONS_CASTLE, { "Ganon's Castle", 57, 60, 57, 60 } },
    { SCENE_INSIDE_GANONS_CASTLE_COLLAPSE, { "Ganon's Castle", 60, 60, 60, 60 } },
    { SCENE_GANONS_TOWER, { "Ganon's Tower", 59, 60, 59, 60 } },
    { SCENE_GANONS_TOWER_COLLAPSE_INTERIOR, { "Ganon's Tower", 60, 60, 60, 60 } },
    { SCENE_GANONS_TOWER_COLLAPSE_EXTERIOR, { "Ganon's Tower", 60, 60, 60, 60 } },
    { SCENE_GANONDORF_BOSS, { "Ganon's Tower", 62, 62, 62, 62 } },
    { SCENE_GANON_BOSS, { "Ganon's Tower", 63, 63, 63, 63 } },
};

const ZoneInfo* GetZone(int16_t sceneNum) {
    auto it = sZones.find(sceneNum);
    return it == sZones.end() ? nullptr : &it->second;
}

ContentKind GetContentKind(int16_t scene) {
    switch (scene) {
        case SCENE_DEKU_TREE:
        case SCENE_DEKU_TREE_BOSS:
        case SCENE_DODONGOS_CAVERN:
        case SCENE_DODONGOS_CAVERN_BOSS:
        case SCENE_JABU_JABU:
        case SCENE_JABU_JABU_BOSS:
        case SCENE_FOREST_TEMPLE:
        case SCENE_FOREST_TEMPLE_BOSS:
        case SCENE_FIRE_TEMPLE:
        case SCENE_FIRE_TEMPLE_BOSS:
        case SCENE_WATER_TEMPLE:
        case SCENE_WATER_TEMPLE_BOSS:
        case SCENE_SHADOW_TEMPLE:
        case SCENE_SHADOW_TEMPLE_BOSS:
        case SCENE_SPIRIT_TEMPLE:
        case SCENE_SPIRIT_TEMPLE_BOSS:
        case SCENE_BOTTOM_OF_THE_WELL:
        case SCENE_ICE_CAVERN:
        case SCENE_GERUDO_TRAINING_GROUND:
            return CONTENT_DUNGEON;
        case SCENE_INSIDE_GANONS_CASTLE:
        case SCENE_INSIDE_GANONS_CASTLE_COLLAPSE:
        case SCENE_GANONS_TOWER:
        case SCENE_GANONS_TOWER_COLLAPSE_INTERIOR:
        case SCENE_GANONS_TOWER_COLLAPSE_EXTERIOR:
        case SCENE_GANONDORF_BOSS:
        case SCENE_GANON_BOSS:
            return CONTENT_RAID;
    }
    return CONTENT_WORLD;
}

const char* ContentLabel(ContentKind kind) {
    switch (kind) {
        case CONTENT_DUNGEON:
            return "Dungeon";
        case CONTENT_RAID:
            return "Raid";
        default:
            return "";
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Enemies
// ---------------------------------------------------------------------------------------------------------------
static const std::unordered_map<int16_t, const char*> sEnemyNames = {
    { ACTOR_EN_DEKUBABA, "Deku Baba" },
    { ACTOR_EN_KAREBABA, "Withered Deku Baba" },
    { ACTOR_EN_ST, "Skulltula" },
    { ACTOR_EN_SW, "Skullwalltula" },
    { ACTOR_EN_FIREFLY, "Keese" },
    { ACTOR_EN_OKUTA, "Octorok" },
    { ACTOR_EN_SKB, "Stalchild" },
    { ACTOR_EN_TITE, "Tektite" },
    { ACTOR_EN_DODONGO, "Dodongo" },
    { ACTOR_EN_DODOJR, "Baby Dodongo" },
    { ACTOR_EN_BW, "Torch Slug" },
    { ACTOR_EN_ZF, "Lizalfos" },
    { ACTOR_EN_TEST, "Stalfos" },
    { ACTOR_EN_WF, "Wolfos" },
    { ACTOR_EN_MB, "Moblin" },
    { ACTOR_EN_PEEHAT, "Peahat" },
    { ACTOR_EN_RD, "ReDead" },
    { ACTOR_EN_POH, "Poe" },
    { ACTOR_EN_PO_FIELD, "Field Poe" },
    { ACTOR_EN_PO_SISTERS, "Poe Sister" },
    { ACTOR_EN_IK, "Iron Knuckle" },
    { ACTOR_EN_FZ, "Freezard" },
    { ACTOR_EN_WALLMAS, "Wallmaster" },
    { ACTOR_EN_FLOORMAS, "Floormaster" },
    { ACTOR_EN_BB, "Bubble" },
    { ACTOR_EN_BUBBLE, "Shabom" },
    { ACTOR_EN_DEKUNUTS, "Mad Scrub" },
    { ACTOR_EN_BILI, "Biri" },
    { ACTOR_EN_VALI, "Bari" },
    { ACTOR_EN_BA, "Parasitic Tentacle" },
    { ACTOR_EN_TP, "Tailpasaran" },
    { ACTOR_EN_AM, "Armos" },
    { ACTOR_EN_SB, "Shell Blade" },
    { ACTOR_EN_EIYER, "Stinger" },
    { ACTOR_EN_CROW, "Guay" },
    { ACTOR_EN_RR, "Like Like" },
    { ACTOR_EN_ANUBICE, "Anubis" },
    { ACTOR_EN_GELDB, "Gerudo Thief" },
    { ACTOR_EN_DH, "Dead Hand" },
    { ACTOR_EN_DHA, "Dead Hand's Hand" },
    { ACTOR_EN_SKJ, "Skull Kid" },
    { ACTOR_EN_NY, "Spike" },
    { ACTOR_EN_TORCH2, "Dark Link" },
    { ACTOR_EN_REEBA, "Leever" },
    { ACTOR_EN_GOMA, "Gohma Larva" },
    { ACTOR_EN_BIGOKUTA, "Big Octo" },
    { ACTOR_EN_TUBO_TRAP, "Flying Pot" },
    { ACTOR_BOSS_GOMA, "Queen Gohma" },
    { ACTOR_BOSS_DODONGO, "King Dodongo" },
    { ACTOR_BOSS_VA, "Barinade" },
    { ACTOR_BOSS_GANONDROF, "Phantom Ganon" },
    { ACTOR_BOSS_FD, "Volvagia" },
    { ACTOR_BOSS_FD2, "Volvagia" },
    { ACTOR_BOSS_MO, "Morpha" },
    { ACTOR_BOSS_SST, "Bongo Bongo" },
    { ACTOR_BOSS_TW, "Twinrova" },
    { ACTOR_BOSS_GANON, "Ganondorf" },
    { ACTOR_BOSS_GANON2, "Ganon" },
};

std::string GetEnemyName(int16_t actorId) {
    auto it = sEnemyNames.find(actorId);
    if (it != sEnemyNames.end()) {
        return it->second;
    }
    if (ActorDB::Instance != nullptr && actorId >= 0 && actorId < ActorDB::Instance->GetEntryCount()) {
        const std::string& desc = ActorDB::Instance->RetrieveEntry(actorId).desc;
        if (!desc.empty()) {
            return desc;
        }
    }
    return "Monster";
}

bool IsBoss(int16_t id) {
    switch (id) {
        case ACTOR_BOSS_GOMA:
        case ACTOR_BOSS_DODONGO:
        case ACTOR_BOSS_VA:
        case ACTOR_BOSS_GANONDROF:
        case ACTOR_BOSS_FD:
        case ACTOR_BOSS_FD2:
        case ACTOR_BOSS_MO:
        case ACTOR_BOSS_SST:
        case ACTOR_BOSS_TW:
        case ACTOR_BOSS_GANON:
        case ACTOR_BOSS_GANON2:
            return true;
    }
    return false;
}

bool IsElite(int16_t id) {
    switch (id) {
        case ACTOR_EN_TEST:
        case ACTOR_EN_ZF:
        case ACTOR_EN_IK:
        case ACTOR_EN_TORCH2:
        case ACTOR_EN_DH:
        case ACTOR_EN_PO_SISTERS:
        case ACTOR_EN_BIGOKUTA:
        case ACTOR_EN_SKJ:
        case ACTOR_EN_GELDB:
        case ACTOR_EN_WF:
        case ACTOR_EN_MB:
            return true;
    }
    return false;
}

bool IsTrackedEnemy(void* refActor) {
    Actor* actor = static_cast<Actor*>(refActor);
    if (actor == nullptr) {
        return false;
    }
    if (IsBoss(actor->id)) {
        return true;
    }
    if (actor->category != ACTORCAT_ENEMY) {
        return false;
    }
    switch (actor->id) {
        case ACTOR_EN_ENCOUNT1:
        case ACTOR_EN_ENCOUNT2:
        case ACTOR_EN_FIRE_ROCK:
        case ACTOR_EN_DHA:
        case ACTOR_EN_BA:
            return false;
    }
    return true;
}

// ---------------------------------------------------------------------------------------------------------------
// Quests
// ---------------------------------------------------------------------------------------------------------------
static const std::vector<QuestDef> sQuests = {
    // ---------------- Child ----------------
    { 1, "The Forest's Bite", "Mido", SCENE_KOKIRI_FOREST, 0, 1,
      "Hey, you! Fairy-boy! The Deku Babas around here are getting fat on Kokiri kids. Prove you're not useless "
      "and cut down some of them.",
      OBJ_KILL, { ACTOR_EN_DEKUBABA, ACTOR_EN_KAREBABA }, "Deku Baba slain", 4, 0, UNCOMMON },
    { 2, "Webs in the Great Tree", "Saria", SCENE_KOKIRI_FOREST, 0, 3,
      "Something is wrong with the Great Deku Tree, Link. Skulltulas are spinning webs inside him. Please be "
      "careful... and clear them out.",
      OBJ_KILL, { ACTOR_EN_ST, ACTOR_EN_SW }, "Skulltula slain", 3, 0, UNCOMMON },
    { 3, "The Queen of Parasites", "Saria", SCENE_KOKIRI_FOREST, 0, 5,
      "A curse has taken root in the Great Deku Tree. Find the beast at its heart and destroy it.", OBJ_BOSS,
      { ACTOR_BOSS_GOMA }, "Queen Gohma slain", 1, 2, RARE },
    { 4, "Hyrule Field Patrol", "Royal Guard", SCENE_HYRULE_FIELD, 0, 5,
      "Halt! When night falls the dead rise from the dirt of the field. The Crown pays for every Stalchild put "
      "back in the ground.",
      OBJ_KILL, { ACTOR_EN_SKB }, "Stalchild slain", 6, 0, UNCOMMON },
    { 5, "Eight-Legged Menace", "Anju", SCENE_KAKARIKO_VILLAGE, 0, 7,
      "The house up the hill is crawling with spiders, and a family was cursed for its greed. Please, thin the "
      "Skulltulas out.",
      OBJ_KILL, { ACTOR_EN_ST, ACTOR_EN_SW }, "Skulltula slain", 8, 0, UNCOMMON },
    { 6, "Wings in the Dark", "Dampe", SCENE_GRAVEYARD, 0, 8,
      "Heh heh... the Keese get into my graves and peck at the flowers. Kill 'em. I'll make it worth your while.",
      OBJ_KILL, { ACTOR_EN_FIREFLY }, "Keese slain", 6, 0, UNCOMMON },
    { 7, "Rocks That Bite", "Goron Elder", SCENE_DEATH_MOUNTAIN_TRAIL, 0, 9,
      "Tektites keep jumping on our rock roasts! Brother, smash some for us, Goron!", OBJ_KILL, { ACTOR_EN_TITE },
      "Tektite slain", 5, 0, UNCOMMON },
    { 8, "Dodongo Extermination", "Darunia", SCENE_GORON_CITY, 0, 11,
      "The Dodongos have overrun our cavern and our food stores. Show me your strength, and I may call you "
      "Brother.",
      OBJ_KILL, { ACTOR_EN_DODONGO, ACTOR_EN_DODOJR }, "Dodongo slain", 8, 0, UNCOMMON },
    { 9, "Scaled Warriors", "Darunia", SCENE_GORON_CITY, 0, 12,
      "Reptile warriors guard the deep halls of the cavern. Defeat them and the path will open.", OBJ_KILL,
      { ACTOR_EN_ZF }, "Lizalfos slain", 2, 8, UNCOMMON },
    { 10, "The King of Dodongos", "Darunia", SCENE_GORON_CITY, 0, 13,
      "At the bottom of the cavern waits the King of all Dodongos. Bring me its end, Brother!", OBJ_BOSS,
      { ACTOR_BOSS_DODONGO }, "King Dodongo slain", 1, 8, RARE },
    { 11, "River Patrol", "Zora Scout", SCENE_ZORAS_RIVER, 0, 13,
      "Octoroks spit rocks at anyone who swims upriver. Clear the waters, land-dweller.", OBJ_KILL,
      { ACTOR_EN_OKUTA }, "Octorok slain", 5, 0, UNCOMMON },
    { 12, "Parasites of the Deep", "King Zora", SCENE_ZORAS_DOMAIN, 0, 16,
      "Lord Jabu-Jabu is unwell. Something lives inside him... jellies, shocking things. Cleanse him.", OBJ_KILL,
      { ACTOR_EN_BILI, ACTOR_EN_VALI, ACTOR_EN_BUBBLE }, "Biri or Bari slain", 6, 0, UNCOMMON },
    { 13, "The Heart of Jabu-Jabu", "King Zora", SCENE_ZORAS_DOMAIN, 0, 18,
      "Deep within Lord Jabu-Jabu, a monstrous parasite feeds. End it, and my daughter's guardian will be free.",
      OBJ_BOSS, { ACTOR_BOSS_VA }, "Barinade slain", 1, 12, RARE },
    // ---------------- Adult ----------------
    { 20, "Shadows of the Sacred Forest", "Sheik", SCENE_SACRED_FOREST_MEADOW, 1, 22,
      "Ganondorf's Moblins guard the meadow where the Sage of Forest waits. Cut them down.", OBJ_KILL,
      { ACTOR_EN_MB, ACTOR_EN_WF }, "Moblin or Wolfos slain", 4, 0, UNCOMMON },
    { 21, "ReDead Ruins", "Lost Soul", SCENE_MARKET_ENTRANCE_RUINS, 1, 25,
      "...Castle Town fell. The dead walk among the ashes. Put them to rest, hero...", OBJ_KILL, { ACTOR_EN_RD },
      "ReDead slain", 3, 0, UNCOMMON },
    { 22, "The Phantom Rider", "Sheik", SCENE_SACRED_FOREST_MEADOW, 1, 27,
      "A phantom of Ganondorf haunts the Forest Temple and holds Saria captive. Destroy it.", OBJ_BOSS,
      { ACTOR_BOSS_GANONDROF }, "Phantom Ganon slain", 1, 20, RARE },
    { 23, "Ring of Fire", "Goron Link", SCENE_DEATH_MOUNTAIN_CRATER, 1, 32,
      "The crater burns with monsters. Torch Slugs and Fire Keese everywhere! Help us, big brother!", OBJ_KILL,
      { ACTOR_EN_FIREFLY, ACTOR_EN_BW, ACTOR_EN_TITE }, "Fire creature slain", 6, 0, UNCOMMON },
    { 24, "The Dragon of Death Mountain", "Goron Link", SCENE_GORON_CITY, 1, 34,
      "Volvagia has risen again and taken the Gorons. Slay the dragon!", OBJ_BOSS,
      { ACTOR_BOSS_FD, ACTOR_BOSS_FD2 }, "Volvagia slain", 1, 0, RARE },
    { 25, "Frozen Domain", "Zora Survivor", SCENE_ZORAS_FOUNTAIN, 1, 39,
      "The ice creatures spread from the cavern. Shatter the Freezards before they freeze us all.", OBJ_KILL,
      { ACTOR_EN_FZ }, "Freezard slain", 5, 0, UNCOMMON },
    { 26, "Shells and Stingers", "Lake Scientist", SCENE_LAKE_HYLIA, 1, 40,
      "Fascinating! The temple below the lake teems with Shell Blades, Stingers and Spikes. Bring me data... "
      "by killing them.",
      OBJ_KILL, { ACTOR_EN_SB, ACTOR_EN_EIYER, ACTOR_EN_NY, ACTOR_EN_TP }, "Water creature slain", 6, 0,
      UNCOMMON },
    { 27, "The Water Beast", "Lake Scientist", SCENE_LAKE_HYLIA, 1, 42,
      "Something living in the water itself has drained the lake. Destroy it at its core!", OBJ_BOSS,
      { ACTOR_BOSS_MO }, "Morpha slain", 1, 26, RARE },
    { 28, "Restless Dead", "Dampe's Ghost", SCENE_GRAVEYARD, 1, 45,
      "The shadows under Kakariko have woken. Poes, Wallmasters, ReDeads... send them back.", OBJ_KILL,
      { ACTOR_EN_POH, ACTOR_EN_RD, ACTOR_EN_WALLMAS, ACTOR_EN_FLOORMAS }, "Undead slain", 6, 0, UNCOMMON },
    { 29, "Bongo Bongo", "Sheik", SCENE_GRAVEYARD, 1, 48,
      "An ancient evil has broken free of the Shadow Temple. Impa has gone after it alone. Follow her.", OBJ_BOSS,
      { ACTOR_BOSS_SST }, "Bongo Bongo slain", 1, 28, RARE },
    { 30, "Thieves of the Desert", "Carpenter Boss", SCENE_GERUDO_VALLEY, 1, 45,
      "My boys are locked up in the fortress! The Gerudo guards are fierce. Beat a few of 'em!", OBJ_KILL,
      { ACTOR_EN_GELDB }, "Gerudo Thief defeated", 3, 0, UNCOMMON },
    { 31, "Leevers of the Wastes", "Desert Wanderer", SCENE_DESERT_COLOSSUS, 1, 49,
      "The sands crawl with Leevers. Thin them out so travelers can reach the Colossus.", OBJ_KILL,
      { ACTOR_EN_REEBA }, "Leever slain", 6, 0, UNCOMMON },
    { 32, "Knights of Iron", "Nabooru", SCENE_DESERT_COLOSSUS, 1, 51,
      "The witches' Iron Knuckles guard the Spirit Temple. Break their armor.", OBJ_KILL, { ACTOR_EN_IK },
      "Iron Knuckle slain", 2, 0, RARE },
    { 33, "The Twin Witches", "Nabooru", SCENE_DESERT_COLOSSUS, 1, 52,
      "Koume and Kotake. Ganondorf's surrogate mothers. End them.", OBJ_BOSS, { ACTOR_BOSS_TW }, "Twinrova slain",
      1, 32, EPIC },
    { 34, "The King of Evil", "Princess Zelda", SCENE_OUTSIDE_GANONS_CASTLE, 1, 57,
      "Ganondorf awaits at the top of his tower. This is the end of the road, hero. Defeat him.", OBJ_BOSS,
      { ACTOR_BOSS_GANON }, "Ganondorf defeated", 1, 0, LEGENDARY },
};

const std::vector<QuestDef>& GetQuests() {
    return sQuests;
}

const QuestDef* GetQuest(int id) {
    for (const auto& q : sQuests) {
        if (q.id == id) {
            return &q;
        }
    }
    return nullptr;
}

// ---------------------------------------------------------------------------------------------------------------
// Items
// ---------------------------------------------------------------------------------------------------------------
const char* SlotName(uint8_t slot) {
    static const char* names[] = { "Head", "Chest", "Hands", "Legs", "Feet", "Finger", "Trinket", "Sword" };
    return slot < SLOT_COUNT ? names[slot] : "Junk";
}

static int RandInt(int n) {
    if (n <= 0) {
        return 0;
    }
    int r = (int)(Rand_ZeroOne() * n);
    return std::min(r, n - 1);
}

template <size_t N> static const char* Pick(const char* const (&arr)[N]) {
    return arr[RandInt((int)N)];
}

static const char* const kHead[] = { "Cap", "Hood", "Helm", "Circlet", "Coif", "Mask" };
static const char* const kChest[] = { "Tunic", "Vest", "Breastplate", "Robe", "Jerkin", "Hauberk" };
static const char* const kHands[] = { "Gloves", "Gauntlets", "Grips", "Handwraps" };
static const char* const kLegs[] = { "Leggings", "Trousers", "Greaves", "Kilt", "Legguards" };
static const char* const kFeet[] = { "Boots", "Sandals", "Treads", "Sabatons", "Striders" };
static const char* const kRing[] = { "Ring", "Band", "Loop", "Signet" };
static const char* const kTrinket[] = { "Charm", "Idol", "Totem", "Emblem", "Talisman", "Medallion" };
static const char* const kWeapon[] = { "Sword", "Blade", "Edge", "Cutlass", "Saber", "Longsword" };

static const char* const kCommonAdj[] = { "Worn", "Sturdy", "Simple", "Patched", "Plain", "Rough" };

static const char* ZonePrefix(int16_t scene) {
    switch (scene) {
        case SCENE_KOKIRI_FOREST:
        case SCENE_DEKU_TREE:
        case SCENE_DEKU_TREE_BOSS:
        case SCENE_LOST_WOODS:
        case SCENE_SACRED_FOREST_MEADOW:
        case SCENE_FOREST_TEMPLE:
        case SCENE_FOREST_TEMPLE_BOSS: {
            static const char* const p[] = { "Kokiri", "Leafwoven", "Deku", "Mossy", "Forest" };
            return Pick(p);
        }
        case SCENE_DEATH_MOUNTAIN_TRAIL:
        case SCENE_DEATH_MOUNTAIN_CRATER:
        case SCENE_GORON_CITY:
        case SCENE_DODONGOS_CAVERN:
        case SCENE_DODONGOS_CAVERN_BOSS:
        case SCENE_FIRE_TEMPLE:
        case SCENE_FIRE_TEMPLE_BOSS: {
            static const char* const p[] = { "Goron", "Magma-forged", "Dodongo-hide", "Volcanic", "Emberstone" };
            return Pick(p);
        }
        case SCENE_ZORAS_RIVER:
        case SCENE_ZORAS_DOMAIN:
        case SCENE_ZORAS_FOUNTAIN:
        case SCENE_JABU_JABU:
        case SCENE_JABU_JABU_BOSS:
        case SCENE_LAKE_HYLIA:
        case SCENE_WATER_TEMPLE:
        case SCENE_WATER_TEMPLE_BOSS:
        case SCENE_ICE_CAVERN: {
            static const char* const p[] = { "Zora", "Scaled", "Tidal", "Frostwoven", "Coral" };
            return Pick(p);
        }
        case SCENE_GERUDO_VALLEY:
        case SCENE_GERUDOS_FORTRESS:
        case SCENE_THIEVES_HIDEOUT:
        case SCENE_GERUDO_TRAINING_GROUND:
        case SCENE_HAUNTED_WASTELAND:
        case SCENE_DESERT_COLOSSUS:
        case SCENE_SPIRIT_TEMPLE:
        case SCENE_SPIRIT_TEMPLE_BOSS: {
            static const char* const p[] = { "Gerudo", "Sandstrider", "Desert", "Sunscorched", "Spirit-bound" };
            return Pick(p);
        }
        case SCENE_KAKARIKO_VILLAGE:
        case SCENE_GRAVEYARD:
        case SCENE_SHADOW_TEMPLE:
        case SCENE_SHADOW_TEMPLE_BOSS:
        case SCENE_BOTTOM_OF_THE_WELL:
        case SCENE_ROYAL_FAMILYS_TOMB: {
            static const char* const p[] = { "Sheikah", "Shadowbound", "Gravewoven", "Lantern-lit", "Eyeless" };
            return Pick(p);
        }
        case SCENE_INSIDE_GANONS_CASTLE:
        case SCENE_GANONS_TOWER:
        case SCENE_GANONDORF_BOSS:
        case SCENE_GANON_BOSS:
        case SCENE_OUTSIDE_GANONS_CASTLE: {
            static const char* const p[] = { "Dread", "Evilforged", "Gerudo King's", "Twilight", "Malice-touched" };
            return Pick(p);
        }
        default: {
            static const char* const p[] = { "Hylian", "Royal", "Castle Guard's", "Ranch-hand's", "Traveler's" };
            return Pick(p);
        }
    }
}

struct Suffix {
    const char* name;
    float str, agi, sta, spi;
};
static const Suffix kSuffixes[] = {
    { "of the Bear", 0.5f, 0.0f, 0.5f, 0.0f },     { "of the Monkey", 0.0f, 0.5f, 0.5f, 0.0f },
    { "of the Tiger", 0.5f, 0.5f, 0.0f, 0.0f },    { "of the Whale", 0.0f, 0.0f, 0.5f, 0.5f },
    { "of the Gorilla", 0.5f, 0.0f, 0.0f, 0.5f },  { "of the Falcon", 0.0f, 0.5f, 0.0f, 0.5f },
    { "of Strength", 1.0f, 0.0f, 0.0f, 0.0f },     { "of Agility", 0.0f, 1.0f, 0.0f, 0.0f },
    { "of Stamina", 0.0f, 0.0f, 1.0f, 0.0f },      { "of Spirit", 0.0f, 0.0f, 0.0f, 1.0f },
    { "of the Hero", 0.34f, 0.33f, 0.33f, 0.0f },  { "of Courage", 0.6f, 0.0f, 0.4f, 0.0f },
    { "of Wisdom", 0.0f, 0.0f, 0.4f, 0.6f },       { "of Power", 0.7f, 0.3f, 0.0f, 0.0f },
};

static const char* const kRareNames[] = { "Warden's",    "Champion's", "Sage's",   "Knight's", "Ranger's",
                                          "Gatekeeper's", "Seeker's",   "Hunter's", "Duelist's" };
static const char* const kEpicNames[] = { "Triforce-touched", "Hero of Time's", "Sacred Realm", "Goddess-blessed",
                                          "Timeworn Master" };

static float RarityBudget(uint8_t r) {
    switch (r) {
        case UNCOMMON:
            return 1.0f;
        case RARE:
            return 1.45f;
        case EPIC:
            return 2.0f;
        case LEGENDARY:
            return 2.8f;
        default:
            return 0.0f;
    }
}

static float SlotBudget(uint8_t s) {
    switch (s) {
        case HEAD:
        case CHEST:
        case LEGS:
            return 1.0f;
        case HANDS:
        case FEET:
            return 0.75f;
        case RING:
        case TRINKET:
            return 0.6f;
        case WEAPON:
            return 1.1f;
    }
    return 0.5f;
}

static float SlotArmor(uint8_t s) {
    switch (s) {
        case CHEST:
            return 1.0f;
        case LEGS:
            return 0.85f;
        case HEAD:
            return 0.7f;
        case HANDS:
        case FEET:
            return 0.55f;
    }
    return 0.0f;
}

Item GenerateItem(int ilvl, uint8_t rarity, int16_t scene, uint8_t forcedSlot) {
    Item it;
    it.valid = true;
    it.rarity = rarity;
    it.ilvl = (uint16_t)std::clamp(ilvl, 1, 70);
    it.slot = forcedSlot < SLOT_COUNT ? forcedSlot : (uint8_t)RandInt(SLOT_COUNT);
    it.reqLevel = (uint16_t)std::clamp(ilvl - 3, 1, MAX_LEVEL);

    const char* base = "";
    switch (it.slot) {
        case HEAD:
            base = Pick(kHead);
            break;
        case CHEST:
            base = Pick(kChest);
            break;
        case HANDS:
            base = Pick(kHands);
            break;
        case LEGS:
            base = Pick(kLegs);
            break;
        case FEET:
            base = Pick(kFeet);
            break;
        case RING:
            base = Pick(kRing);
            break;
        case TRINKET:
            base = Pick(kTrinket);
            break;
        case WEAPON:
            base = Pick(kWeapon);
            break;
    }

    float rarityArmor = rarity == COMMON ? 0.8f : (1.0f + RarityBudget(rarity) * 0.25f);
    it.armor = (int16_t)std::lround(SlotArmor(it.slot) * (8.0f + it.ilvl * 3.0f) * rarityArmor);

    float budget = (2.0f + it.ilvl * 0.7f) * RarityBudget(rarity) * SlotBudget(it.slot);
    if (it.slot == WEAPON) {
        it.weaponPct = (int16_t)std::lround((rarity == COMMON ? 3.0f : 5.0f) + it.ilvl * 0.35f * std::max(0.5f, RarityBudget(rarity)));
    }

    std::string name;
    if (rarity == COMMON) {
        name = std::string(Pick(kCommonAdj)) + " " + ZonePrefix(scene) + " " + base;
    } else {
        const Suffix& sfx = kSuffixes[RandInt((int)(sizeof(kSuffixes) / sizeof(kSuffixes[0])))];
        it.str = (int16_t)std::lround(budget * sfx.str);
        it.agi = (int16_t)std::lround(budget * sfx.agi);
        it.sta = (int16_t)std::lround(budget * sfx.sta);
        it.spi = (int16_t)std::lround(budget * sfx.spi);
        if (rarity == UNCOMMON) {
            name = std::string(ZonePrefix(scene)) + " " + base + " " + sfx.name;
        } else if (rarity == RARE) {
            name = std::string(ZonePrefix(scene)) + " " + Pick(kRareNames) + " " + base;
        } else if (rarity == EPIC) {
            name = std::string(Pick(kEpicNames)) + " " + base + " " + sfx.name;
        } else {
            name = it.slot == WEAPON ? "Master Sword, Blade of Evil's Bane" : std::string("Triforce of ") +
                                                                                (sfx.str >= sfx.agi ? "Power " : "Courage ") + base;
        }
    }
    it.name = name;

    float sellMul = 1.0f;
    switch (rarity) {
        case COMMON:
            sellMul = 1.0f;
            break;
        case UNCOMMON:
            sellMul = 3.0f;
            break;
        case RARE:
            sellMul = 8.0f;
            break;
        case EPIC:
            sellMul = 20.0f;
            break;
        case LEGENDARY:
            sellMul = 50.0f;
            break;
    }
    it.sellValue = (uint16_t)std::clamp((int)std::lround((2 + it.ilvl * 0.5f) * sellMul), 1, 500);
    return it;
}

Item GenerateJunk(int ilvl, int16_t actorId) {
    static const std::unordered_map<int16_t, std::vector<const char*>> junk = {
        { ACTOR_EN_DEKUBABA, { "Deku Baba Stem", "Wilted Baba Leaf" } },
        { ACTOR_EN_KAREBABA, { "Withered Stalk", "Brittle Baba Leaf" } },
        { ACTOR_EN_ST, { "Skulltula Fang", "Sticky Web" } },
        { ACTOR_EN_SW, { "Skulltula Fang", "Cracked Carapace" } },
        { ACTOR_EN_FIREFLY, { "Keese Wing", "Singed Bat Ear" } },
        { ACTOR_EN_OKUTA, { "Octorok Beak", "Slimy Tentacle" } },
        { ACTOR_EN_SKB, { "Stalchild Bone", "Cracked Skull" } },
        { ACTOR_EN_TITE, { "Tektite Leg", "Bulging Eye" } },
        { ACTOR_EN_DODONGO, { "Dodongo Scale", "Smoldering Gland" } },
        { ACTOR_EN_DODOJR, { "Baby Dodongo Tail" } },
        { ACTOR_EN_ZF, { "Lizalfos Tail", "Chipped Scale" } },
        { ACTOR_EN_TEST, { "Stalfos Femur", "Rusted Buckle" } },
        { ACTOR_EN_WF, { "Wolfos Pelt", "Matted Fur" } },
        { ACTOR_EN_MB, { "Moblin Tusk", "Splintered Spear Haft" } },
        { ACTOR_EN_RD, { "Tattered Wrappings", "Grave Dust" } },
        { ACTOR_EN_POH, { "Poe Wisp", "Cracked Lantern Glass" } },
        { ACTOR_EN_IK, { "Dented Armor Plate" } },
        { ACTOR_EN_FZ, { "Never-melting Shard" } },
        { ACTOR_EN_GELDB, { "Torn Gerudo Sash" } },
        { ACTOR_EN_REEBA, { "Leever Spine" } },
    };
    Item it;
    it.valid = true;
    it.rarity = POOR;
    it.slot = SLOT_JUNK;
    it.ilvl = (uint16_t)std::clamp(ilvl, 1, 70);
    auto f = junk.find(actorId);
    if (f != junk.end()) {
        it.name = f->second[RandInt((int)f->second.size())];
    } else {
        static const char* const generic[] = { "Monster Fang", "Torn Cloth", "Broken Tooth", "Murky Ichor",
                                               "Shiny Pebble", "Bent Rupee Clip" };
        it.name = Pick(generic);
    }
    it.sellValue = (uint16_t)std::clamp(1 + it.ilvl / 6, 1, 20);
    return it;
}

} // namespace Azeroth
