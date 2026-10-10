// Hyrule of Warcraft - core rules: levels, XP, stats, combat math, loot, quests, persistence.

#include "Azeroth.h"
#include "AzerothInternal.h"

#include <algorithm>
#include <cmath>
#include <unordered_map>
#include <unordered_set>
#include <nlohmann/json.hpp>
#include <libultraship/bridge/consolevariablebridge.h>

#include "soh/Enhancements/game-interactor/GameInteractor.h"
#include "soh/ShipInit.hpp"
#include "soh/SaveManager.h"
#include "soh/cvar_prefixes.h"

extern "C" {
#include "z64.h"
#include "functions.h"
#include "macros.h"
#include "variables.h"
extern PlayState* gPlayState;
extern SaveContext gSaveContext;
}

namespace Azeroth {

State gState;

static const ImColor4 kYellow = { 1.0f, 0.82f, 0.0f, 1.0f };
static const ImColor4 kWhite = { 1.0f, 1.0f, 1.0f, 1.0f };
static const ImColor4 kXpPurple = { 0.75f, 0.45f, 1.0f, 1.0f };
static const ImColor4 kRed = { 1.0f, 0.25f, 0.25f, 1.0f };
static const ImColor4 kGreen = { 0.25f, 1.0f, 0.25f, 1.0f };
static const ImColor4 kGold = { 1.0f, 0.85f, 0.35f, 1.0f };

struct MobInfo {
    int level;
    int maxHp;
};
static std::unordered_map<Actor*, MobInfo> sMobs;
static std::unordered_set<Actor*> sKilled;
static int16_t sLastZoneScene = SCENE_KOKIRI_FOREST;
static int sCombatTimer = 0;
static int sRegenTimer = 0;
static int sBossesAlive = 0;
static int sSaveSection = -1;

// ---------------------------------------------------------------------------------------------------------------
// Settings
// ---------------------------------------------------------------------------------------------------------------
bool Enabled() {
    return CVarGetInteger(CVAR_AZEROTH("Enabled"), 1) != 0;
}

int Difficulty() {
    return std::clamp(CVarGetInteger(CVAR_AZEROTH("Difficulty"), 0), 0, 2);
}

const char* DifficultyName(int d) {
    static const char* names[] = { "Normal", "Heroic", "Mythic" };
    return names[std::clamp(d, 0, 2)];
}

static float XpRate() {
    return std::clamp(CVarGetFloat(CVAR_AZEROTH("XpRate"), 1.0f), 0.25f, 10.0f);
}

// ---------------------------------------------------------------------------------------------------------------
// Levels and zones
// ---------------------------------------------------------------------------------------------------------------
uint32_t XpToLevel(int level) {
    return (uint32_t)(100 + 40 * level + 2 * level * level);
}

static int16_t CurrentScene() {
    return gPlayState != nullptr ? gPlayState->sceneNum : sLastZoneScene;
}

static const ZoneInfo* CurrentZoneInfo() {
    const ZoneInfo* z = GetZone(CurrentScene());
    if (z == nullptr) {
        z = GetZone(sLastZoneScene);
    }
    return z;
}

ContentKind CurrentContent() {
    return GetContentKind(CurrentScene());
}

static void ZoneRange(const ZoneInfo* z, int& lo, int& hi) {
    if (z == nullptr) {
        lo = hi = std::max(1, gState.level);
        return;
    }
    if (LINK_IS_ADULT) {
        lo = z->adultMin;
        hi = z->adultMax;
    } else {
        lo = z->childMin;
        hi = z->childMax;
    }
}

int CurrentZoneLevel() {
    int lo, hi;
    ZoneRange(CurrentZoneInfo(), lo, hi);
    return (lo + hi) / 2;
}

const char* CurrentZoneName() {
    const ZoneInfo* z = CurrentZoneInfo();
    return z ? z->name : "Hyrule";
}

struct ContentMods {
    float taken;  // multiplier on damage the player takes
    float dealt;  // multiplier on damage the player deals
    int levelBonus;
};

static ContentMods GetContentMods(bool boss) {
    ContentMods m = { 1.0f, 1.0f, 0 };
    switch (CurrentContent()) {
        case CONTENT_DUNGEON:
            m = boss ? ContentMods{ 1.4f, 0.85f, 2 } : ContentMods{ 1.25f, 0.9f, 1 };
            break;
        case CONTENT_RAID:
            m = boss ? ContentMods{ 1.8f, 0.7f, 3 } : ContentMods{ 1.5f, 0.8f, 2 };
            break;
        default:
            return m;
    }
    switch (Difficulty()) {
        case 1:
            m.taken *= 1.3f;
            m.dealt *= 0.9f;
            m.levelBonus += 2;
            break;
        case 2:
            m.taken *= 1.7f;
            m.dealt *= 0.8f;
            m.levelBonus += 4;
            break;
    }
    return m;
}

static uint32_t HashActor(Actor* a) {
    uint32_t h = 2166136261u;
    auto mix = [&h](uint32_t v) {
        h ^= v;
        h *= 16777619u;
    };
    mix((uint32_t)a->id);
    mix((uint32_t)(uint16_t)a->params);
    mix((uint32_t)(int32_t)a->home.pos.x);
    mix((uint32_t)(int32_t)a->home.pos.y);
    mix((uint32_t)(int32_t)a->home.pos.z);
    return h;
}

static int ComputeMobLevel(Actor* actor) {
    int lo, hi;
    ZoneRange(CurrentZoneInfo(), lo, hi);
    bool boss = IsBoss(actor->id);
    int lvl = boss ? hi + 2 : lo + (int)(HashActor(actor) % (uint32_t)(hi - lo + 1));
    if (!boss && IsElite(actor->id)) {
        lvl += 1;
    }
    lvl += GetContentMods(boss).levelBonus;
    return std::clamp(lvl, 1, 73);
}

int MobLevel(void* refActor) {
    Actor* actor = static_cast<Actor*>(refActor);
    auto it = sMobs.find(actor);
    if (it != sMobs.end()) {
        return it->second.level;
    }
    return ComputeMobLevel(actor);
}

int EnemyMaxHealth(void* refActor) {
    Actor* actor = static_cast<Actor*>(refActor);
    auto it = sMobs.find(actor);
    int hp = actor->colChkInfo.health;
    if (it != sMobs.end()) {
        it->second.maxHp = std::max(it->second.maxHp, hp);
        return std::max(1, it->second.maxHp);
    }
    return std::max(1, hp);
}

int ConColor(int mob) {
    int p = gState.level;
    int diff = mob - p;
    if (diff >= 10) {
        return 5;
    }
    if (diff >= 5) {
        return 4;
    }
    if (diff >= 3) {
        return 3;
    }
    if (diff >= -2) {
        return 2;
    }
    int grey = p <= 5 ? 0 : p - (p / 10 + 5);
    if (mob <= grey) {
        return 0;
    }
    return 1;
}

// ---------------------------------------------------------------------------------------------------------------
// Stats and combat math
// ---------------------------------------------------------------------------------------------------------------
static float BaseStr(int l) {
    return 18.0f + 2.0f * l;
}
static float BaseAgi(int l) {
    return 16.0f + 1.5f * l;
}
static float BaseSta(int l) {
    return 18.0f + 2.0f * l;
}
static float BaseSpi(int l) {
    return 15.0f + 1.0f * l;
}

Stats GetStats() {
    int l = gState.level;
    Stats s = { (int)BaseStr(l), (int)BaseAgi(l), (int)BaseSta(l), (int)BaseSpi(l), 5 * l, 0 };
    for (int i = 0; i < SLOT_COUNT; i++) {
        const Item& it = gState.equipped[i];
        if (!it.valid) {
            continue;
        }
        s.str += it.str;
        s.agi += it.agi;
        s.sta += it.sta;
        s.spi += it.spi;
        s.armor += it.armor;
        s.weaponPct += it.weaponPct;
    }
    s.spi += TalentRank(T_SPIRIT_FOREST) * 6;
    s.sta += TalentRank(T_IRON_WILL) * 4;
    s.str += TalentRank(T_VIGOR) * 3;
    s.armor = (int)std::lround(s.armor * (1.0f + 0.05f * TalentRank(T_TOUGHNESS)));
    for (const Buff& b : GetBuffs()) {
        s.str += b.str;
        s.agi += b.agi;
        s.sta += b.sta;
        s.armor += b.armor;
    }
    return s;
}

float DamageMultiplier(int mob) {
    Stats s = GetStats();
    float mine = s.str + 0.5f * s.agi;
    float theirs = BaseStr(mob) + 0.5f * BaseAgi(mob);
    float m = (mine / theirs) * (1.0f + s.weaponPct / 100.0f) * (1.0f + 0.02f * TalentRank(T_IMPROVED_STRIKES));
    return std::clamp(m, 0.35f, 4.0f);
}

float CritChance(int mob) {
    Stats s = GetStats();
    return std::clamp(0.05f + (s.agi - BaseAgi(mob)) * 0.0025f + 0.01f * TalentRank(T_CRUELTY), 0.02f, 0.45f);
}

float DamageReduction(int mob) {
    Stats s = GetStats();
    float armor = (float)std::max(0, s.armor);
    float r = armor / (armor + 60.0f + 30.0f * mob) + (s.sta - BaseSta(mob)) * 0.004f;
    return std::clamp(r, -0.6f, 0.75f);
}

static int CombatFrames() {
    return (int)(100 * (1.0f - 0.2f * TalentRank(T_SECOND_WIND)));
}

bool InCombat() {
    return sCombatTimer > 0;
}

static float RoundRandom(float v) {
    float f = std::floor(v);
    return f + ((Rand_ZeroOne() < (v - f)) ? 1.0f : 0.0f);
}

} // namespace Azeroth

using namespace Azeroth;

extern "C" float Azeroth_ModifyOutgoingDamage(void* playv, void* colliderv, float damage) {
    if (!Enabled() || damage <= 0.0f || playv == nullptr || colliderv == nullptr) {
        return damage;
    }
    PlayState* play = static_cast<PlayState*>(playv);
    Collider* collider = static_cast<Collider*>(colliderv);
    Actor* target = collider->actor;
    Actor* source = collider->ac;
    if (target == nullptr || !IsTrackedEnemy(target)) {
        return damage;
    }
    Player* player = GET_PLAYER(play);
    if (player == nullptr) {
        return damage;
    }
    bool fromPlayer = source != nullptr && (source == &player->actor || source->parent == &player->actor ||
                                            source->category == ACTORCAT_EXPLOSIVE);
    if (!fromPlayer) {
        return damage;
    }

    int mob = MobLevel(target);
    bool boss = IsBoss(target->id);
    float mult = DamageMultiplier(mob) * GetContentMods(boss).dealt;
    bool crit = Rand_ZeroOne() < CritChance(mob);
    float critMult = 2.0f + 0.15f * TalentRank(T_DEEP_WOUNDS);
    float raw = damage * mult * (crit ? critMult : 1.0f);
    if (TalentRank(T_EXECUTIONER) > 0 && target->colChkInfo.health * 10 < EnemyMaxHealth(target) * 3) {
        raw *= 1.0f + 0.25f * TalentRank(T_EXECUTIONER);
    }
    float result = std::clamp(RoundRandom(raw), 0.0f, 255.0f);

    sCombatTimer = CombatFrames();

    Vec3f p = target->focus.pos;
    if (result <= 0.0f) {
        FloatText(p.x, p.y + 10.0f, p.z, "Miss", { 0.8f, 0.8f, 0.8f, 1.0f }, 1.0f);
    } else {
        int shown = std::max(1, (int)std::lround(raw * 10.0f));
        if (crit) {
            FloatText(p.x, p.y + 10.0f, p.z, std::to_string(shown) + "!", { 1.0f, 0.9f, 0.1f, 1.0f }, 1.7f);
        } else {
            FloatText(p.x, p.y + 10.0f, p.z, std::to_string(shown), kWhite, 1.15f);
        }
    }
    return result;
}

extern "C" int Azeroth_ModifyIncomingDamage(void* playv, int healthChange) {
    if (!Enabled() || healthChange >= 0) {
        return healthChange;
    }
    int mob = CurrentZoneLevel() + GetContentMods(sBossesAlive > 0).levelBonus;
    float red = DamageReduction(mob);
    float taken = (float)(-healthChange) * (1.0f - red) * GetContentMods(sBossesAlive > 0).taken;
    taken *= 1.0f - 0.03f * TalentRank(T_SHIELD_WALL);
    if (TalentRank(T_LAST_STAND) > 0 && gSaveContext.health < 4 * 16) {
        taken *= 0.7f;
    }
    int result = std::max(1, (int)RoundRandom(taken));
    sCombatTimer = CombatFrames();
    sRegenTimer = 0;
    if (gPlayState != nullptr) {
        Player* player = GET_PLAYER(gPlayState);
        if (player != nullptr) {
            Vec3f p = player->actor.world.pos;
            FloatText(p.x, p.y + 60.0f, p.z, "-" + std::to_string(result * 5 / 4 > 0 ? result * 5 / 4 : 1), kRed,
                      1.25f);
        }
    }
    return -result;
}

namespace Azeroth {

// ---------------------------------------------------------------------------------------------------------------
// XP
// ---------------------------------------------------------------------------------------------------------------
static void LevelUp() {
    gState.level++;
    Stats s = GetStats();
    CenterText("You have reached Level " + std::to_string(gState.level) + "!", kGold, 5.0f);
    ChatLine("Congratulations, you have reached level " + std::to_string(gState.level) + "!", kYellow);
    ChatLine("Your Strength, Agility, Stamina and Spirit increase. (STR " + std::to_string(s.str) + ", AGI " +
                 std::to_string(s.agi) + ", STA " + std::to_string(s.sta) + ", SPI " + std::to_string(s.spi) + ")",
             kGreen);
    if (gPlayState != nullptr && gSaveContext.health > 0) {
        gSaveContext.health = gSaveContext.healthCapacity;
        if (gSaveContext.magicLevel > 0) {
            gSaveContext.magic = gSaveContext.magicCapacity;
        }
        Audio_PlayFanfare(NA_BGM_HEART_GET);
    }
}

void AwardXp(int amount, const char* reason) {
    if (amount <= 0) {
        return;
    }
    if (gState.level >= MAX_LEVEL) {
        return;
    }
    amount = std::max(1, (int)std::lround(amount * XpRate() * (1.0f + 0.02f * TalentRank(T_QUICK_STUDY))));
    gState.xp += (uint32_t)amount;
    std::string line = "You gain " + std::to_string(amount) + " experience";
    if (reason != nullptr && reason[0] != '\0') {
        line += std::string(" (") + reason + ")";
    }
    ChatLine(line + ".", kXpPurple);
    bool leveled = false;
    while (gState.level < MAX_LEVEL && gState.xp >= XpToLevel(gState.level)) {
        gState.xp -= XpToLevel(gState.level);
        LevelUp();
        leveled = true;
    }
    if (gState.level >= MAX_LEVEL) {
        gState.xp = 0;
    }
    if (leveled) {
        SaveNow();
    }
}

static int KillXp(Actor* actor) {
    int m = MobLevel(actor);
    int p = gState.level;
    float base = 20.0f + 4.0f * m;
    float mod;
    if (m >= p) {
        mod = 1.0f + 0.05f * std::min(m - p, 4);
    } else {
        int grey = p <= 5 ? 0 : p - (p / 10 + 5);
        if (m <= grey) {
            return 0;
        }
        float zd = 5.0f + p / 8.0f;
        mod = std::max(0.1f, 1.0f - (p - m) / zd);
    }
    float x = base * mod;
    if (IsBoss(actor->id)) {
        x *= 15.0f;
    } else if (IsElite(actor->id)) {
        x *= 2.5f;
    }
    switch (CurrentContent()) {
        case CONTENT_DUNGEON:
            x *= 1.2f;
            break;
        case CONTENT_RAID:
            x *= 1.5f;
            break;
        default:
            break;
    }
    x *= 1.0f + 0.15f * Difficulty() * (CurrentContent() != CONTENT_WORLD ? 1 : 0);
    if (actor->id == ACTOR_EN_TUBO_TRAP) {
        x *= 0.25f;
    }
    return (int)std::lround(x);
}

// ---------------------------------------------------------------------------------------------------------------
// Bags / equipment
// ---------------------------------------------------------------------------------------------------------------
bool AddToBags(const Item& item) {
    if ((int)gState.bags.size() >= BAG_SLOTS) {
        ChatLine("Inventory is full.", kRed);
        CenterText("Inventory is full.", kRed, 2.5f);
        return false;
    }
    gState.bags.push_back(item);
    ChatLoot(item);
    return true;
}

void EquipFromBag(int index) {
    if (index < 0 || index >= (int)gState.bags.size()) {
        return;
    }
    Item it = gState.bags[index];
    if (it.slot >= SLOT_COUNT) {
        return;
    }
    if (it.reqLevel > gState.level) {
        ChatLine("You must reach level " + std::to_string(it.reqLevel) + " to use that item.", kRed);
        Sfx_PlaySfxCentered(NA_SE_SY_ERROR);
        return;
    }
    Item old = gState.equipped[it.slot];
    gState.equipped[it.slot] = it;
    gState.bags.erase(gState.bags.begin() + index);
    if (old.valid) {
        gState.bags.insert(gState.bags.begin() + index, old);
    }
    Sfx_PlaySfxCentered(NA_SE_SY_DECIDE);
}

void Unequip(int slot) {
    if (slot < 0 || slot >= SLOT_COUNT || !gState.equipped[slot].valid) {
        return;
    }
    if ((int)gState.bags.size() >= BAG_SLOTS) {
        ChatLine("Inventory is full.", kRed);
        return;
    }
    gState.bags.push_back(gState.equipped[slot]);
    gState.equipped[slot] = Item();
    Sfx_PlaySfxCentered(NA_SE_SY_DECIDE);
}

void SellFromBag(int index) {
    if (index < 0 || index >= (int)gState.bags.size()) {
        return;
    }
    const Item& it = gState.bags[index];
    Rupees_ChangeBy((s16)it.sellValue);
    ChatLine("Sold " + it.name + " for " + std::to_string(it.sellValue) + " rupees.", kYellow);
    gState.bags.erase(gState.bags.begin() + index);
    Sfx_PlaySfxCentered(NA_SE_SY_GET_RUPY);
}

void SellAllJunk() {
    int total = 0;
    int count = 0;
    for (int i = (int)gState.bags.size() - 1; i >= 0; i--) {
        if (gState.bags[i].rarity == POOR) {
            total += gState.bags[i].sellValue;
            count++;
            gState.bags.erase(gState.bags.begin() + i);
        }
    }
    if (count > 0) {
        Rupees_ChangeBy((s16)total);
        ChatLine("Sold " + std::to_string(count) + " junk items for " + std::to_string(total) + " rupees.", kYellow);
        Sfx_PlaySfxCentered(NA_SE_SY_GET_RUPY);
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Loot
// ---------------------------------------------------------------------------------------------------------------
static int LootIlvlBonus() {
    if (CurrentContent() == CONTENT_WORLD) {
        return 0;
    }
    return Difficulty() * 4 + (CurrentContent() == CONTENT_RAID ? 3 : 1);
}

static void RollLoot(Actor* actor) {
    int m = MobLevel(actor);
    int16_t scene = CurrentScene();
    int ilvl = m + LootIlvlBonus();
    ContentKind content = CurrentContent();
    float diffMul = 1.0f + 0.25f * Difficulty() * (content != CONTENT_WORLD ? 1 : 0);

    if (IsBoss(actor->id)) {
        bool raid = content == CONTENT_RAID || actor->id == ACTOR_BOSS_GANON || actor->id == ACTOR_BOSS_GANON2;
        if (actor->id == ACTOR_BOSS_GANON2) {
            AddToBags(GenerateItem(ilvl + 5, LEGENDARY, scene));
        } else if (raid) {
            AddToBags(GenerateItem(ilvl, Rand_ZeroOne() < 0.2f * diffMul ? LEGENDARY : EPIC, scene));
        } else {
            float epicChance = 0.25f + 0.15f * Difficulty();
            AddToBags(GenerateItem(ilvl, Rand_ZeroOne() < epicChance ? EPIC : RARE, scene));
        }
        AddToBags(GenerateItem(ilvl, Rand_ZeroOne() < 0.5f ? RARE : UNCOMMON, scene));
        int rupees = 20 + m;
        Rupees_ChangeBy((s16)rupees);
        ChatLine("You loot " + std::to_string(rupees) + " Rupees.", kYellow);
        return;
    }

    float eliteMul = IsElite(actor->id) ? 3.0f : 1.0f;
    float contentMul = content == CONTENT_RAID ? 2.0f : (content == CONTENT_DUNGEON ? 1.5f : 1.0f);
    float mul = eliteMul * contentMul * diffMul * (1.0f + 0.1f * TalentRank(T_TREASURE_HUNTER));

    float r = Rand_ZeroOne();
    float pEpic = 0.002f * mul;
    float pRare = 0.012f * mul;
    float pGreen = 0.06f * mul;
    float pWhite = 0.08f;
    float pGrey = 0.30f;
    if (r < pEpic) {
        AddToBags(GenerateItem(ilvl, EPIC, scene));
    } else if (r < pEpic + pRare) {
        AddToBags(GenerateItem(ilvl, RARE, scene));
    } else if (r < pEpic + pRare + pGreen) {
        AddToBags(GenerateItem(ilvl, UNCOMMON, scene));
    } else if (r < pEpic + pRare + pGreen + pWhite) {
        AddToBags(GenerateItem(ilvl, COMMON, scene));
    } else if (r < pEpic + pRare + pGreen + pWhite + pGrey) {
        AddToBags(GenerateJunk(ilvl, actor->id));
    }

    if (Rand_ZeroOne() < 0.35f) {
        int rupees = 1 + m / 8 + (int)(Rand_ZeroOne() * 3);
        Rupees_ChangeBy((s16)rupees);
        ChatLine("You loot " + std::to_string(rupees) + (rupees == 1 ? " Rupee." : " Rupees."), kYellow);
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Quests
// ---------------------------------------------------------------------------------------------------------------
static bool SameZone(int16_t a, int16_t b) {
    if (a == b) {
        return true;
    }
    const ZoneInfo* za = GetZone(a);
    const ZoneInfo* zb = GetZone(b);
    return za != nullptr && zb != nullptr && std::string(za->name) == zb->name;
}

static int QuestXp(const QuestDef& q) {
    float x = XpToLevel(q.level) * (q.type == OBJ_BOSS ? 0.9f : 0.4f);
    return (int)std::lround(x);
}

static int QuestRupees(const QuestDef& q) {
    return q.type == OBJ_BOSS ? 20 + q.level : 5 + q.level / 2;
}

bool QuestAvailable(const QuestDef& q) {
    auto it = gState.quests.find(q.id);
    if (it != gState.quests.end() && it->second.status != Q_NONE) {
        return false;
    }
    if (q.age == 1 && !LINK_IS_ADULT) {
        return false;
    }
    if (q.age == 0 && LINK_IS_ADULT) {
        return false;
    }
    if (gState.level < q.level - 5) {
        return false;
    }
    if (q.prereq != 0) {
        auto p = gState.quests.find(q.prereq);
        if (p == gState.quests.end() || p->second.status != Q_DONE) {
            return false;
        }
    }
    return SameZone(CurrentScene(), q.giverScene);
}

bool CanTurnInHere(const QuestDef& q) {
    return SameZone(CurrentScene(), q.giverScene);
}

void AcceptQuest(int id) {
    const QuestDef* q = GetQuest(id);
    if (q == nullptr || !QuestAvailable(*q)) {
        return;
    }
    gState.quests[id] = { Q_ACTIVE, 0 };
    ChatLine(std::string("Quest accepted: ") + q->title, kYellow);
    Sfx_PlaySfxCentered(NA_SE_SY_DECIDE);
}

void AbandonQuest(int id) {
    auto it = gState.quests.find(id);
    if (it == gState.quests.end() || it->second.status == Q_DONE) {
        return;
    }
    const QuestDef* q = GetQuest(id);
    gState.quests.erase(it);
    if (q != nullptr) {
        ChatLine(std::string("Quest abandoned: ") + q->title, kYellow);
    }
}

void TurnInQuest(int id) {
    const QuestDef* q = GetQuest(id);
    auto it = gState.quests.find(id);
    if (q == nullptr || it == gState.quests.end() || it->second.status != Q_READY || !CanTurnInHere(*q)) {
        return;
    }
    it->second.status = Q_DONE;
    ChatLine(std::string(q->title) + " completed.", kYellow);
    CenterText(std::string("Quest Complete: ") + q->title, kYellow, 4.0f);
    Sfx_PlaySfxCentered(NA_SE_SY_CORRECT_CHIME);
    int rupees = QuestRupees(*q);
    Rupees_ChangeBy((s16)rupees);
    ChatLine("Received " + std::to_string(rupees) + " Rupees.", kYellow);
    AddToBags(GenerateItem(q->level + 1, q->rewardRarity, q->giverScene));
    AwardXp(QuestXp(*q), "quest");
    SaveNow();
}

static void QuestKillProgress(Actor* actor) {
    for (const QuestDef& q : GetQuests()) {
        if (std::find(q.targets.begin(), q.targets.end(), actor->id) == q.targets.end()) {
            continue;
        }
        QuestState& st = gState.quests[q.id];
        if (st.status == Q_NONE && q.type == OBJ_BOSS) {
            // Boss kills always count, even if the quest wasn't picked up yet.
            st.status = Q_ACTIVE;
            ChatLine(std::string("Quest accepted: ") + q.title, kYellow);
        }
        if (st.status != Q_ACTIVE) {
            if (st.status == Q_NONE) {
                gState.quests.erase(q.id);
            }
            continue;
        }
        st.progress = (uint16_t)std::min<int>(st.progress + 1, q.count);
        ChatLine(std::string(q.targetLabel) + ": " + std::to_string(st.progress) + "/" + std::to_string(q.count),
                 kYellow);
        if (st.progress >= q.count) {
            st.status = Q_READY;
            CenterText(std::string(q.title) + " (Complete)", kYellow, 3.5f);
            ChatLine(std::string("Return to ") + q.giver + " to turn in " + q.title + ".", kYellow);
            Sfx_PlaySfxCentered(NA_SE_SY_CORRECT_CHIME);
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------------------------------------------
static void OnKill(void* refActor) {
    Actor* actor = static_cast<Actor*>(refActor);
    if (actor == nullptr || !IsTrackedEnemy(actor) || sKilled.count(actor)) {
        return;
    }
    sKilled.insert(actor);
    gState.totalKills++;
    sCombatTimer = std::max(sCombatTimer, 60);

    int xp = KillXp(actor);
    if (xp > 0) {
        Vec3f p = actor->focus.pos;
        FloatText(p.x, p.y + 30.0f, p.z, "+" + std::to_string((int)std::lround(xp * XpRate())) + " XP", kXpPurple,
                  1.0f);
        AwardXp(xp, nullptr);
    }
    QuestKillProgress(actor);
    RollLoot(actor);
    OnSkinKill(actor);
    int frenzy = TalentRank(T_BLOOD_FRENZY);
    if (frenzy > 0 && gSaveContext.health > 0) {
        gSaveContext.health = std::min<int>(gSaveContext.healthCapacity, gSaveContext.health + 2 * frenzy);
    }

    if (IsBoss(actor->id)) {
        ContentKind c = CurrentContent();
        std::string label = c == CONTENT_RAID ? "Raid Boss defeated: " : "Dungeon Boss defeated: ";
        CenterText(label + GetEnemyName(actor->id), kGold, 5.0f);
        if (sBossesAlive > 0) {
            sBossesAlive--;
        }
        SaveNow();
    }
}

static void OnActorInitHook(void* refActor) {
    Actor* actor = static_cast<Actor*>(refActor);
    if (!IsTrackedEnemy(actor)) {
        return;
    }
    MobInfo info;
    info.level = ComputeMobLevel(actor);
    info.maxHp = std::max<int>(1, actor->colChkInfo.health);
    sMobs[actor] = info;
    if (IsBoss(actor->id)) {
        sBossesAlive++;
    }
}

static void OnActorDestroyHook(void* refActor) {
    Actor* actor = static_cast<Actor*>(refActor);
    auto it = sMobs.find(actor);
    if (it != sMobs.end()) {
        if (IsBoss(actor->id) && !sKilled.count(actor) && sBossesAlive > 0) {
            sBossesAlive--;
        }
        sMobs.erase(it);
    }
    sKilled.erase(actor);
}

static void OnSceneInitHook(int16_t sceneNum) {
    sMobs.clear();
    sKilled.clear();
    sBossesAlive = 0;
    const ZoneInfo* z = GetZone(sceneNum);
    if (z == nullptr) {
        return;
    }
    sLastZoneScene = sceneNum;

    bool known = false;
    for (int s : gState.explored) {
        const ZoneInfo* e = GetZone((int16_t)s);
        if (e != nullptr && std::string(e->name) == z->name) {
            known = true;
            break;
        }
    }
    gState.explored.insert(sceneNum);
    ContentKind c = GetContentKind(sceneNum);
    if (!known) {
        std::string title = std::string("Discovered: ") + z->name;
        if (c != CONTENT_WORLD) {
            title += std::string(" (") + ContentLabel(c) + ")";
        }
        CenterText(title, kYellow, 4.0f);
        int lo, hi;
        ZoneRange(z, lo, hi);
        AwardXp(20 + 12 * ((lo + hi) / 2), "discovery");
    } else if (c != CONTENT_WORLD) {
        CenterText(std::string(z->name) + " - " + ContentLabel(c) + " (" + DifficultyName(Difficulty()) + ")",
                   c == CONTENT_RAID ? ImColor4{ 1.0f, 0.5f, 0.0f, 1.0f } : ImColor4{ 0.4f, 0.7f, 1.0f, 1.0f },
                   3.0f);
    }
}

static void OnPlayerUpdateHook() {
    if (gPlayState == nullptr) {
        return;
    }
    ProgressionFrame();
    if (sCombatTimer > 0) {
        sCombatTimer--;
        sRegenTimer = 0;
        return;
    }
    if (!CVarGetInteger(CVAR_AZEROTH("Regen"), 1)) {
        return;
    }
    // Mythic dungeons and raids, and any active boss fight: no free healing.
    if (sBossesAlive > 0 || (Difficulty() == 2 && CurrentContent() != CONTENT_WORLD)) {
        return;
    }
    if (gSaveContext.health <= 0 || gSaveContext.health >= gSaveContext.healthCapacity) {
        sRegenTimer = 0;
        return;
    }
    Stats s = GetStats();
    int interval = std::max(12, 90 - std::min(s.spi, 78));
    if (++sRegenTimer >= interval) {
        sRegenTimer = 0;
        gSaveContext.health = std::min<int>(gSaveContext.health + 4, gSaveContext.healthCapacity);
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Persistence
// ---------------------------------------------------------------------------------------------------------------
static nlohmann::json ItemToJson(const Item& it) {
    return nlohmann::json{ { "n", it.name }, { "r", it.rarity }, { "s", it.slot }, { "i", it.ilvl },
                           { "q", it.reqLevel }, { "st", it.str }, { "ag", it.agi }, { "sa", it.sta },
                           { "sp", it.spi }, { "ar", it.armor }, { "w", it.weaponPct }, { "v", it.sellValue } };
}

static Item ItemFromJson(const nlohmann::json& j) {
    Item it;
    it.valid = true;
    it.name = j.value("n", std::string("Item"));
    it.rarity = j.value("r", (uint8_t)0);
    it.slot = j.value("s", (uint8_t)SLOT_JUNK);
    it.ilvl = j.value("i", (uint16_t)1);
    it.reqLevel = j.value("q", (uint16_t)1);
    it.str = j.value("st", (int16_t)0);
    it.agi = j.value("ag", (int16_t)0);
    it.sta = j.value("sa", (int16_t)0);
    it.spi = j.value("sp", (int16_t)0);
    it.armor = j.value("ar", (int16_t)0);
    it.weaponPct = j.value("w", (int16_t)0);
    it.sellValue = j.value("v", (uint16_t)1);
    return it;
}

static std::string Serialize() {
    nlohmann::json j;
    j["level"] = gState.level;
    j["xp"] = gState.xp;
    j["kills"] = gState.totalKills;
    j["bags"] = nlohmann::json::array();
    for (const Item& it : gState.bags) {
        j["bags"].push_back(ItemToJson(it));
    }
    j["equipped"] = nlohmann::json::array();
    for (int i = 0; i < SLOT_COUNT; i++) {
        j["equipped"].push_back(gState.equipped[i].valid ? ItemToJson(gState.equipped[i]) : nlohmann::json());
    }
    j["quests"] = nlohmann::json::array();
    for (const auto& [id, st] : gState.quests) {
        if (st.status != Q_NONE) {
            j["quests"].push_back({ id, st.status, st.progress });
        }
    }
    j["explored"] = gState.explored;
    j["talents"] = nlohmann::json::array();
    for (const auto& [id, r] : gState.talents) {
        j["talents"].push_back({ id, r });
    }
    j["prof"] = { gState.prof[0], gState.prof[1] };
    j["skill"] = nlohmann::json::array();
    for (int i = 0; i < 8; i++) {
        j["skill"].push_back(gState.skill[i]);
    }
    j["reagents"] = gState.reagents;
    return j.dump();
}

static void Deserialize(const std::string& s) {
    gState = State();
    if (s.empty()) {
        return;
    }
    nlohmann::json j = nlohmann::json::parse(s, nullptr, false);
    if (j.is_discarded() || !j.is_object()) {
        return;
    }
    gState.level = std::clamp(j.value("level", 1), 1, MAX_LEVEL);
    gState.xp = j.value("xp", 0u);
    gState.totalKills = j.value("kills", 0u);
    if (j.contains("bags") && j["bags"].is_array()) {
        for (const auto& it : j["bags"]) {
            if (it.is_object() && (int)gState.bags.size() < BAG_SLOTS) {
                gState.bags.push_back(ItemFromJson(it));
            }
        }
    }
    if (j.contains("equipped") && j["equipped"].is_array()) {
        for (size_t i = 0; i < j["equipped"].size() && i < SLOT_COUNT; i++) {
            if (j["equipped"][i].is_object()) {
                gState.equipped[i] = ItemFromJson(j["equipped"][i]);
            }
        }
    }
    if (j.contains("quests") && j["quests"].is_array()) {
        for (const auto& q : j["quests"]) {
            if (q.is_array() && q.size() == 3) {
                gState.quests[q[0].get<int>()] = { q[1].get<uint8_t>(), q[2].get<uint16_t>() };
            }
        }
    }
    if (j.contains("explored") && j["explored"].is_array()) {
        for (const auto& e : j["explored"]) {
            if (e.is_number_integer()) {
                gState.explored.insert(e.get<int>());
            }
        }
    }
    if (j.contains("talents") && j["talents"].is_array()) {
        for (const auto& t : j["talents"]) {
            if (t.is_array() && t.size() == 2) {
                gState.talents[t[0].get<int>()] = t[1].get<int>();
            }
        }
    }
    if (j.contains("prof") && j["prof"].is_array() && j["prof"].size() == 2) {
        gState.prof[0] = j["prof"][0].get<uint8_t>();
        gState.prof[1] = j["prof"][1].get<uint8_t>();
    }
    if (j.contains("skill") && j["skill"].is_array()) {
        for (size_t i = 0; i < j["skill"].size() && i < 8; i++) {
            gState.skill[i] = j["skill"][i].get<uint16_t>();
        }
    }
    if (j.contains("reagents") && j["reagents"].is_object()) {
        for (auto& [k, v] : j["reagents"].items()) {
            if (v.is_number_integer() && v.get<int>() > 0) {
                gState.reagents[k] = v.get<int>();
            }
        }
    }
}

static void SaveFn(const SaveContext& saveContext, int sectionID, bool fullSave) {
    SaveManager::Instance->SaveData("data", Serialize());
}

static void LoadFn() {
    std::string s;
    SaveManager::Instance->LoadData("data", s, std::string());
    Deserialize(s);
}

static void InitFn(bool isDebug) {
    gState = State();
    sMobs.clear();
    sKilled.clear();
    sBossesAlive = 0;
    sCombatTimer = 0;
}

void SaveNow() {
    if (sSaveSection < 0 || gSaveContext.fileNum < 0 || gSaveContext.fileNum > 2) {
        return;
    }
    SaveManager::Instance->SaveSection(gSaveContext.fileNum, sSaveSection, true);
}

static void RegisterAzeroth() {
    static bool sRegisteredSave = false;
    if (!sRegisteredSave && SaveManager::Instance != nullptr) {
        sRegisteredSave = true;
        SaveManager::Instance->AddInitFunction(InitFn);
        sSaveSection = SaveManager::Instance->AddSaveFunction("azeroth", 1, SaveFn, true, SECTION_PARENT_NONE);
        SaveManager::Instance->AddLoadFunction("azeroth", 1, LoadFn);
        RegisterUI();
    }

    bool on = Enabled();
    COND_HOOK(OnEnemyDefeat, on, OnKill);
    COND_HOOK(OnBossDefeat, on, OnKill);
    COND_HOOK(OnActorInit, on, OnActorInitHook);
    COND_HOOK(OnActorDestroy, on, OnActorDestroyHook);
    COND_HOOK(OnSceneInit, on, OnSceneInitHook);
    COND_HOOK(OnPlayerUpdate, on, OnPlayerUpdateHook);
}

static RegisterShipInitFunc initFunc(RegisterAzeroth, { CVAR_AZEROTH("Enabled") });

} // namespace Azeroth
