#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <deque>
#include <map>
#include <set>

#define CVAR_AZEROTH(var) CVAR_ENHANCEMENT("Azeroth." var)

namespace Azeroth {

constexpr int MAX_LEVEL = 60;
constexpr int BAG_SLOTS = 20;

enum Rarity : uint8_t { POOR, COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, RARITY_COUNT };

enum Slot : uint8_t { HEAD, CHEST, HANDS, LEGS, FEET, RING, TRINKET, WEAPON, SLOT_COUNT, SLOT_JUNK = 0xFF };

struct Item {
    std::string name;
    uint8_t rarity = POOR;
    uint8_t slot = SLOT_JUNK;
    uint16_t ilvl = 1;
    uint16_t reqLevel = 1;
    int16_t str = 0, agi = 0, sta = 0, spi = 0, armor = 0;
    int16_t weaponPct = 0; // bonus damage % (weapons)
    uint16_t sellValue = 1;
    bool valid = false;
};

enum QuestStatus : uint8_t { Q_NONE, Q_ACTIVE, Q_READY, Q_DONE };

enum ObjectiveType : uint8_t { OBJ_KILL, OBJ_BOSS };

struct QuestDef {
    int id;
    const char* title;
    const char* giver;
    int16_t giverScene;  // scene where it's offered and turned in
    int8_t age;          // 0 = child, 1 = adult, -1 = either
    int level;
    const char* text;
    ObjectiveType type;
    std::vector<int16_t> targets; // actor ids
    const char* targetLabel;
    int count;
    int prereq; // quest id that must be turned in first (0 = none)
    uint8_t rewardRarity;
};

struct QuestState {
    uint8_t status = Q_NONE;
    uint16_t progress = 0;
};

enum ContentKind : uint8_t { CONTENT_WORLD, CONTENT_DUNGEON, CONTENT_RAID };

struct ZoneInfo {
    const char* name;
    int childMin, childMax, adultMin, adultMax;
};

struct State {
    int level = 1;
    uint32_t xp = 0;
    uint32_t totalKills = 0;
    std::vector<Item> bags;
    Item equipped[SLOT_COUNT];
    std::map<int, QuestState> quests;
    std::set<int> explored;
    // Talents: talent id -> rank
    std::map<int, int> talents;
    // Professions
    uint8_t prof[2] = { 0, 0 };
    uint16_t skill[8] = { 0 };
    std::map<std::string, int> reagents; // materials and consumables
};

extern State gState;

// ---- Data (AzerothData.cpp) ----
const ZoneInfo* GetZone(int16_t sceneNum);
ContentKind GetContentKind(int16_t sceneNum);
const char* ContentLabel(ContentKind kind);
const std::vector<QuestDef>& GetQuests();
const QuestDef* GetQuest(int id);
std::string GetEnemyName(int16_t actorId);
bool IsBoss(int16_t actorId);
bool IsElite(int16_t actorId);
bool IsTrackedEnemy(void* actor);
Item GenerateItem(int ilvl, uint8_t rarity, int16_t sceneNum, uint8_t forcedSlot = 0xFF);
Item GenerateJunk(int ilvl, int16_t actorId);
const char* SlotName(uint8_t slot);

// ---- Rules / state (Azeroth.cpp) ----
bool Enabled();
uint32_t XpToLevel(int level);
int CurrentZoneLevel();
const char* CurrentZoneName();
int MobLevel(void* actor);
int ConColor(int mobLevel); // 0 grey,1 green,2 yellow,3 orange,4 red,5 skull
struct Stats {
    int str, agi, sta, spi, armor, weaponPct;
};
Stats GetStats();
float CritChance(int mobLevel);
float DamageMultiplier(int mobLevel);
float DamageReduction(int mobLevel);
int EnemyMaxHealth(void* actor);
bool InCombat();
int Difficulty(); // 0 normal, 1 heroic, 2 mythic
const char* DifficultyName(int d);
ContentKind CurrentContent();

void AwardXp(int amount, const char* reason);
bool AddToBags(const Item& item);
void EquipFromBag(int index);
void Unequip(int slot);
void SellFromBag(int index);
void SellAllJunk();
void AcceptQuest(int id);
void TurnInQuest(int id);
void AbandonQuest(int id);
bool QuestAvailable(const QuestDef& q);
bool CanTurnInHere(const QuestDef& q);
void SaveNow();

// ---- Talents (AzerothProgression.cpp) ----
enum TalentId {
    T_IMPROVED_STRIKES = 0, T_CRUELTY, T_DEEP_WOUNDS, T_BLOOD_FRENZY, T_EXECUTIONER,
    T_QUICK_STUDY = 10, T_SPIRIT_FOREST, T_TREASURE_HUNTER, T_SECOND_WIND, T_MANA_FONT,
    T_IRON_WILL = 20, T_VIGOR, T_TOUGHNESS, T_SHIELD_WALL, T_LAST_STAND,
};
struct TalentDef {
    int id;
    int tree; // 0 Courage, 1 Wisdom, 2 Power
    const char* name;
    int maxRank;
    int reqTreePoints;
    const char* desc; // %d = per-rank value * rank
    int perRank;
};
const std::vector<TalentDef>& GetTalents();
const char* TreeName(int tree);
int TalentRank(int id);
int TalentPointsTotal();
int TalentPointsSpent();
int TreePoints(int tree);
bool CanLearnTalent(const TalentDef& t);
void LearnTalent(int id);
int RespecCost();
void ResetTalents();

// ---- Professions (AzerothProgression.cpp) ----
enum ProfId : uint8_t { P_NONE, P_HERBALISM, P_MINING, P_SKINNING, P_ALCHEMY, P_BLACKSMITHING, P_LEATHERWORKING, P_COUNT };
enum RecipeKind : uint8_t { R_HEAL, R_MAGIC, R_ELIXIR_STR, R_ELIXIR_AGI, R_ELIXIR_ARMOR, R_FLASK, R_GEAR };
struct Recipe {
    uint8_t prof;
    std::string name;
    int reqSkill;
    std::vector<std::pair<std::string, int>> mats;
    RecipeKind kind;
    int tier;
    uint8_t slot;
    uint8_t rarity;
};
const char* ProfName(uint8_t p);
bool IsGathering(uint8_t p);
bool KnowsProf(uint8_t p);
void LearnProf(uint8_t p);
void UnlearnProf(uint8_t p);
const std::vector<Recipe>& GetRecipes();
int RecipeColor(const Recipe& r); // 0 grey 1 green 2 yellow 3 orange 4 red(unlearnable)
bool CanCraft(const Recipe& r);
void Craft(const Recipe& r);
bool IsConsumable(const std::string& name);
void UseConsumable(const std::string& name);
void QuaffBestHealingPotion();
void OnGatherHerb(float chance);
void OnGatherOre(int amount);
void OnSkinKill(void* actor);
void ProgressionFrame(); // per game frame
struct Buff {
    std::string name;
    int str, agi, sta, armor;
    int framesLeft;
};
const std::vector<Buff>& GetBuffs();
int PotionCooldownFrames();

// ---- UI feedback (AzerothUI.cpp) ----
struct ImColor4 {
    float r, g, b, a;
};
ImColor4 RarityColor(uint8_t rarity);
ImColor4 ConColorRGB(int con);
void ChatLine(const std::string& text, ImColor4 color);
void ChatLoot(const Item& item);
void CenterText(const std::string& text, ImColor4 color, float seconds = 4.0f);
void FloatText(float x, float y, float z, const std::string& text, ImColor4 color, float scale = 1.0f);
void RegisterUI();

} // namespace Azeroth
