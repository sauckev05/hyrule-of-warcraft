// Hyrule of Warcraft - talents, professions, consumables and buffs.

#include "AzerothInternal.h"

#include <algorithm>
#include <cmath>
#include <libultraship/bridge/consolevariablebridge.h>

#include "soh/Enhancements/game-interactor/GameInteractor.h"
#include "soh/cvar_prefixes.h"
#include "soh/ShipInit.hpp"

extern "C" {
#include "z64.h"
#include "functions.h"
#include "macros.h"
#include "variables.h"
extern PlayState* gPlayState;
extern SaveContext gSaveContext;
}

namespace Azeroth {

static const ImColor4 kYellow = { 1.0f, 0.82f, 0.0f, 1.0f };
static const ImColor4 kRed = { 1.0f, 0.25f, 0.25f, 1.0f };
static const ImColor4 kWhite = { 1.0f, 1.0f, 1.0f, 1.0f };
static const ImColor4 kSkill = { 0.35f, 0.55f, 1.0f, 1.0f };
static const ImColor4 kGreen = { 0.25f, 1.0f, 0.25f, 1.0f };

// ===============================================================================================================
// Talents
// ===============================================================================================================
static const std::vector<TalentDef> sTalents = {
    // Courage - offense
    { T_IMPROVED_STRIKES, 0, "Improved Strikes", 5, 0, "Increases all damage you deal by %d%%.", 2 },
    { T_CRUELTY, 0, "Cruelty", 5, 0, "Increases your critical strike chance by %d%%.", 1 },
    { T_DEEP_WOUNDS, 0, "Deep Wounds", 3, 5, "Your critical strikes deal %d%% more damage.", 15 },
    { T_BLOOD_FRENZY, 0, "Blood Frenzy", 3, 5, "Defeating an enemy restores %d sixteenths of a heart.", 2 },
    { T_EXECUTIONER, 0, "Executioner", 2, 10, "Deal %d%% more damage to enemies below 30%% health.", 25 },
    // Wisdom - utility
    { T_QUICK_STUDY, 1, "Quick Study", 5, 0, "Increases experience gained by %d%%.", 2 },
    { T_SPIRIT_FOREST, 1, "Spirit of the Forest", 5, 0, "Increases your Spirit by %d.", 6 },
    { T_TREASURE_HUNTER, 1, "Treasure Hunter", 3, 5, "Increases the chance to find loot by %d%%.", 10 },
    { T_SECOND_WIND, 1, "Second Wind", 3, 5, "You leave combat %d%% faster, starting regeneration sooner.", 20 },
    { T_MANA_FONT, 1, "Fairy Font", 3, 10, "Regenerate magic out of combat. Rank %d.", 1 },
    // Power - defense
    { T_IRON_WILL, 2, "Iron Will", 5, 0, "Increases your Stamina by %d.", 4 },
    { T_VIGOR, 2, "Goron Vigor", 3, 0, "Increases your Strength by %d.", 3 },
    { T_TOUGHNESS, 2, "Toughness", 5, 5, "Increases armor from items and levels by %d%%.", 5 },
    { T_SHIELD_WALL, 2, "Hylian Shield Wall", 3, 5, "Reduces all damage taken by %d%%.", 3 },
    { T_LAST_STAND, 2, "Last Stand", 1, 10, "Below 4 hearts, damage taken is reduced by %d%%.", 30 },
};

const std::vector<TalentDef>& GetTalents() {
    return sTalents;
}

const char* TreeName(int tree) {
    static const char* names[] = { "Courage", "Wisdom", "Power" };
    return names[std::clamp(tree, 0, 2)];
}

int TalentRank(int id) {
    auto it = gState.talents.find(id);
    return it == gState.talents.end() ? 0 : it->second;
}

int TalentPointsTotal() {
    return std::max(0, gState.level - 9);
}

int TalentPointsSpent() {
    int n = 0;
    for (const auto& [id, r] : gState.talents) {
        n += r;
    }
    return n;
}

int TreePoints(int tree) {
    int n = 0;
    for (const TalentDef& t : sTalents) {
        if (t.tree == tree) {
            n += TalentRank(t.id);
        }
    }
    return n;
}

bool CanLearnTalent(const TalentDef& t) {
    return TalentPointsSpent() < TalentPointsTotal() && TalentRank(t.id) < t.maxRank &&
           TreePoints(t.tree) >= t.reqTreePoints;
}

void LearnTalent(int id) {
    for (const TalentDef& t : sTalents) {
        if (t.id == id && CanLearnTalent(t)) {
            gState.talents[id] = TalentRank(id) + 1;
            Sfx_PlaySfxCentered(NA_SE_SY_DECIDE);
            ChatLine(std::string("You have learned ") + t.name + " (Rank " + std::to_string(gState.talents[id]) + ").",
                     kYellow);
            return;
        }
    }
}

int RespecCost() {
    return std::clamp(gState.level, 1, 50);
}

void ResetTalents() {
    if (TalentPointsSpent() == 0) {
        return;
    }
    int cost = RespecCost();
    if (gSaveContext.rupees < cost) {
        ChatLine("You need " + std::to_string(cost) + " rupees to unlearn your talents.", kRed);
        Sfx_PlaySfxCentered(NA_SE_SY_ERROR);
        return;
    }
    Rupees_ChangeBy((s16)-cost);
    gState.talents.clear();
    ChatLine("Your talents have been reset.", kYellow);
}

// ===============================================================================================================
// Professions
// ===============================================================================================================
const char* ProfName(uint8_t p) {
    static const char* names[] = { "None", "Herbalism", "Mining", "Skinning", "Alchemy", "Blacksmithing", "Leatherworking" };
    return p < P_COUNT ? names[p] : "?";
}

bool IsGathering(uint8_t p) {
    return p == P_HERBALISM || p == P_MINING || p == P_SKINNING;
}

bool KnowsProf(uint8_t p) {
    return p != P_NONE && (gState.prof[0] == p || gState.prof[1] == p);
}

void LearnProf(uint8_t p) {
    if (p == P_NONE || p >= P_COUNT || KnowsProf(p)) {
        return;
    }
    for (int i = 0; i < 2; i++) {
        if (gState.prof[i] == P_NONE) {
            gState.prof[i] = p;
            gState.skill[p] = 1;
            ChatLine(std::string("You have learned a new profession: ") + ProfName(p) + ".", kYellow);
            Sfx_PlaySfxCentered(NA_SE_SY_CORRECT_CHIME);
            return;
        }
    }
    ChatLine("You can only learn two professions. Unlearn one first.", kRed);
}

void UnlearnProf(uint8_t p) {
    for (int i = 0; i < 2; i++) {
        if (gState.prof[i] == p) {
            gState.prof[i] = P_NONE;
            gState.skill[p] = 0;
            ChatLine(std::string("You have unlearned ") + ProfName(p) + ".", kYellow);
        }
    }
}

static const char* const kHerbs[5] = { "Kokiri Clover", "Hylian Shroom", "Silent Princess", "Gerudo Sandbloom",
                                       "Sacred Lotus" };
static const char* const kOres[5] = { "Copper Ore", "Goron Iron Ore", "Zora Silver Ore", "Gerudo Gold Ore",
                                      "Mythril Ore" };
static const char* const kLeathers[5] = { "Light Leather", "Medium Leather", "Heavy Leather", "Thick Leather",
                                          "Rugged Leather" };
static const char* const kMetalPrefix[5] = { "Copper", "Goron Iron", "Zora Silver", "Gerudo Gold", "Mythril" };
static const char* const kLeatherPrefix[5] = { "Rough", "Sturdy", "Wolfhide", "Dodongo-scale", "Volvagia-scale" };
static const char* const kHealNames[5] = { "Minor Healing Potion", "Lesser Healing Potion", "Healing Potion",
                                           "Greater Healing Potion", "Major Healing Potion" };
static const int kHealHearts[5] = { 2, 4, 6, 10, 20 };

static int ReqForTier(int t) {
    return (t - 1) * 60 + 1;
}

static std::vector<Recipe> BuildRecipes() {
    std::vector<Recipe> r;
    for (int t = 1; t <= 5; t++) {
        int i = t - 1;
        int req = ReqForTier(t);
        // Alchemy
        r.push_back({ P_ALCHEMY, kHealNames[i], req, { { kHerbs[i], 2 } }, R_HEAL, t, SLOT_JUNK, COMMON });
        if (t >= 2) {
            r.push_back({ P_ALCHEMY, std::string(t >= 4 ? "Greater " : "") + "Magic Potion", req + 10,
                          { { kHerbs[i], 2 }, { kHerbs[i - 1], 1 } }, R_MAGIC, t, SLOT_JUNK, COMMON });
        }
        // Blacksmithing
        r.push_back({ P_BLACKSMITHING, std::string(kMetalPrefix[i]) + " Sword", req, { { kOres[i], 4 } }, R_GEAR, t,
                      WEAPON, (uint8_t)(t == 5 ? RARE : UNCOMMON) });
        r.push_back({ P_BLACKSMITHING, std::string(kMetalPrefix[i]) + " Gauntlets", req + 15, { { kOres[i], 3 } },
                      R_GEAR, t, HANDS, UNCOMMON });
        r.push_back({ P_BLACKSMITHING, std::string(kMetalPrefix[i]) + " Helm", req + 25, { { kOres[i], 5 } }, R_GEAR,
                      t, HEAD, UNCOMMON });
        r.push_back({ P_BLACKSMITHING, std::string(kMetalPrefix[i]) + " Breastplate", req + 40,
                      { { kOres[i], 7 } }, R_GEAR, t, CHEST, (uint8_t)(t >= 4 ? RARE : UNCOMMON) });
        r.push_back({ P_BLACKSMITHING, std::string(kMetalPrefix[i]) + " Band", req + 30,
                      { { kOres[i], 2 }, { kHerbs[i], 1 } }, R_GEAR, t, RING, UNCOMMON });
        // Leatherworking
        r.push_back({ P_LEATHERWORKING, std::string(kLeatherPrefix[i]) + " Boots", req, { { kLeathers[i], 3 } },
                      R_GEAR, t, FEET, UNCOMMON });
        r.push_back({ P_LEATHERWORKING, std::string(kLeatherPrefix[i]) + " Leggings", req + 20,
                      { { kLeathers[i], 5 } }, R_GEAR, t, LEGS, UNCOMMON });
        r.push_back({ P_LEATHERWORKING, std::string(kLeatherPrefix[i]) + " Tunic", req + 35, { { kLeathers[i], 6 } },
                      R_GEAR, t, CHEST, (uint8_t)(t >= 4 ? RARE : UNCOMMON) });
        r.push_back({ P_LEATHERWORKING, std::string(kLeatherPrefix[i]) + " Trophy Charm", req + 45,
                      { { kLeathers[i], 2 }, { kOres[i], 1 } }, R_GEAR, t, TRINKET, UNCOMMON });
    }
    r.push_back({ P_ALCHEMY, "Elixir of Agility", ReqForTier(2) + 20, { { kHerbs[1], 3 } }, R_ELIXIR_AGI, 2,
                  SLOT_JUNK, COMMON });
    r.push_back({ P_ALCHEMY, "Elixir of Giants", ReqForTier(3) + 20, { { kHerbs[2], 3 } }, R_ELIXIR_STR, 3,
                  SLOT_JUNK, COMMON });
    r.push_back({ P_ALCHEMY, "Elixir of Fortitude", ReqForTier(4) + 20, { { kHerbs[3], 3 } }, R_ELIXIR_ARMOR, 4,
                  SLOT_JUNK, COMMON });
    r.push_back({ P_ALCHEMY, "Flask of the Titans", ReqForTier(5) + 40, { { kHerbs[4], 5 }, { kHerbs[3], 2 } },
                  R_FLASK, 5, SLOT_JUNK, COMMON });
    std::stable_sort(r.begin(), r.end(), [](const Recipe& a, const Recipe& b) { return a.reqSkill < b.reqSkill; });
    return r;
}

const std::vector<Recipe>& GetRecipes() {
    static std::vector<Recipe> recipes = BuildRecipes();
    return recipes;
}

int RecipeColor(const Recipe& r) {
    int s = gState.skill[r.prof];
    if (s < r.reqSkill) {
        return 4;
    }
    int d = s - r.reqSkill;
    if (d < 15) {
        return 3;
    }
    if (d < 30) {
        return 2;
    }
    if (d < 45) {
        return 1;
    }
    return 0;
}

static bool HasMats(const Recipe& r) {
    for (const auto& [name, n] : r.mats) {
        auto it = gState.reagents.find(name);
        if (it == gState.reagents.end() || it->second < n) {
            return false;
        }
    }
    return true;
}

bool CanCraft(const Recipe& r) {
    return KnowsProf(r.prof) && gState.skill[r.prof] >= r.reqSkill && HasMats(r);
}

static void SkillUp(uint8_t prof, int chancePct) {
    if (gState.skill[prof] >= 300) {
        return;
    }
    if ((int)(Rand_ZeroOne() * 100.0f) < chancePct) {
        gState.skill[prof]++;
        ChatLine(std::string("Your skill in ") + ProfName(prof) + " has increased to " +
                     std::to_string(gState.skill[prof]) + ".",
                 kSkill);
    }
}

static void AddReagent(const std::string& name, int n) {
    gState.reagents[name] += n;
    ChatLine("You receive item: [" + name + "]" + (n > 1 ? "x" + std::to_string(n) : ""), kWhite);
}

void Craft(const Recipe& r) {
    if (!CanCraft(r)) {
        Sfx_PlaySfxCentered(NA_SE_SY_ERROR);
        return;
    }
    if (r.kind == R_GEAR && (int)gState.bags.size() >= BAG_SLOTS) {
        ChatLine("Inventory is full.", kRed);
        return;
    }
    for (const auto& [name, n] : r.mats) {
        gState.reagents[name] -= n;
        if (gState.reagents[name] <= 0) {
            gState.reagents.erase(name);
        }
    }
    int color = RecipeColor(r);
    if (r.kind == R_GEAR) {
        int16_t scene = gPlayState != nullptr ? gPlayState->sceneNum : 0;
        Item it = GenerateItem(r.tier * 12 + 2, r.rarity, scene, r.slot);
        it.name = r.name;
        AddToBags(it);
    } else {
        AddReagent(r.name, r.kind == R_HEAL ? 2 : 1);
    }
    Sfx_PlaySfxCentered(NA_SE_SY_GET_ITEM);
    SkillUp(r.prof, color == 3 ? 100 : (color == 2 ? 60 : (color == 1 ? 25 : 0)));
}

// ---------------------------------------------------------------------------------------------------------------
// Consumables & buffs
// ---------------------------------------------------------------------------------------------------------------
static std::vector<Buff> sBuffs;
static int sPotionCd = 0;
static int sMagicTimer = 0;
constexpr int kBuffFrames = 20 * 60 * 10; // 10 minutes of game frames

const std::vector<Buff>& GetBuffs() {
    return sBuffs;
}

int PotionCooldownFrames() {
    return sPotionCd;
}

static const Recipe* FindRecipe(const std::string& name) {
    for (const Recipe& r : GetRecipes()) {
        if (r.name == name) {
            return &r;
        }
    }
    return nullptr;
}

bool IsConsumable(const std::string& name) {
    const Recipe* r = FindRecipe(name);
    return r != nullptr && r->kind != R_GEAR;
}

static void AddBuff(const Buff& b) {
    for (Buff& x : sBuffs) {
        if (x.name == b.name) {
            x = b;
            return;
        }
    }
    sBuffs.push_back(b);
}

void UseConsumable(const std::string& name) {
    const Recipe* r = FindRecipe(name);
    auto it = gState.reagents.find(name);
    if (r == nullptr || r->kind == R_GEAR || it == gState.reagents.end() || it->second <= 0 || gPlayState == nullptr) {
        return;
    }
    if ((r->kind == R_HEAL || r->kind == R_MAGIC) && sPotionCd > 0) {
        ChatLine("Potions are still on cooldown (" + std::to_string(sPotionCd / 20 + 1) + "s).", kRed);
        Sfx_PlaySfxCentered(NA_SE_SY_ERROR);
        return;
    }
    switch (r->kind) {
        case R_HEAL:
            if (gSaveContext.health <= 0) {
                return;
            }
            gSaveContext.health =
                std::min<int>(gSaveContext.healthCapacity, gSaveContext.health + kHealHearts[r->tier - 1] * 16);
            sPotionCd = 20 * 60;
            Sfx_PlaySfxCentered(NA_SE_SY_HP_RECOVER);
            break;
        case R_MAGIC:
            if (gSaveContext.magicLevel <= 0) {
                ChatLine("You have no magic to restore.", kRed);
                return;
            }
            gSaveContext.magic = std::min<int>(gSaveContext.magicCapacity, gSaveContext.magic + 12 * r->tier);
            sPotionCd = 20 * 60;
            Sfx_PlaySfxCentered(NA_SE_SY_HP_RECOVER);
            break;
        case R_ELIXIR_AGI:
            AddBuff({ name, 0, 20, 0, 0, kBuffFrames });
            break;
        case R_ELIXIR_STR:
            AddBuff({ name, 25, 0, 0, 0, kBuffFrames });
            break;
        case R_ELIXIR_ARMOR:
            AddBuff({ name, 0, 0, 0, 250, kBuffFrames });
            break;
        case R_FLASK:
            AddBuff({ name, 40, 0, 40, 0, kBuffFrames * 2 });
            break;
        default:
            break;
    }
    if (--it->second <= 0) {
        gState.reagents.erase(it);
    }
    ChatLine("You use " + name + ".", kGreen);
}

void QuaffBestHealingPotion() {
    for (int i = 4; i >= 0; i--) {
        auto it = gState.reagents.find(kHealNames[i]);
        if (it != gState.reagents.end() && it->second > 0) {
            UseConsumable(kHealNames[i]);
            return;
        }
    }
    ChatLine("You have no healing potions. (Alchemists can brew them!)", kRed);
}

// ---------------------------------------------------------------------------------------------------------------
// Gathering
// ---------------------------------------------------------------------------------------------------------------
static int ZoneTier() {
    return std::clamp(CurrentZoneLevel() / 12 + 1, 1, 5);
}

static int GatherTier(uint8_t prof) {
    int byskill = std::clamp(gState.skill[prof] / 60 + 1, 1, 5);
    return std::min(ZoneTier(), byskill);
}

void OnGatherHerb(float chance) {
    if (!KnowsProf(P_HERBALISM) || Rand_ZeroOne() >= chance) {
        return;
    }
    int t = GatherTier(P_HERBALISM);
    AddReagent(kHerbs[t - 1], 1 + (Rand_ZeroOne() < 0.25f ? 1 : 0));
    SkillUp(P_HERBALISM, gState.skill[P_HERBALISM] < ReqForTier(t) + 75 ? 100 : 30);
}

void OnGatherOre(int amount) {
    if (!KnowsProf(P_MINING)) {
        return;
    }
    int t = GatherTier(P_MINING);
    AddReagent(kOres[t - 1], amount);
    SkillUp(P_MINING, gState.skill[P_MINING] < ReqForTier(t) + 75 ? 100 : 30);
}

void OnSkinKill(void* refActor) {
    Actor* a = static_cast<Actor*>(refActor);
    if (!KnowsProf(P_SKINNING) || a == nullptr) {
        return;
    }
    switch (a->id) {
        case ACTOR_EN_SKB:
        case ACTOR_EN_TEST:
        case ACTOR_EN_RD:
        case ACTOR_EN_POH:
        case ACTOR_EN_PO_FIELD:
        case ACTOR_EN_PO_SISTERS:
        case ACTOR_EN_WALLMAS:
        case ACTOR_EN_FLOORMAS:
        case ACTOR_EN_TUBO_TRAP:
        case ACTOR_EN_BUBBLE:
        case ACTOR_EN_BILI:
        case ACTOR_EN_VALI:
        case ACTOR_EN_FZ:
        case ACTOR_EN_IK:
        case ACTOR_EN_ANUBICE:
            return; // nothing to skin
    }
    bool boss = IsBoss(a->id);
    if (!boss && Rand_ZeroOne() >= 0.45f) {
        return;
    }
    int t = GatherTier(P_SKINNING);
    AddReagent(kLeathers[t - 1], boss ? 5 : 1);
    SkillUp(P_SKINNING, gState.skill[P_SKINNING] < ReqForTier(t) + 75 ? 100 : 30);
}

// ---------------------------------------------------------------------------------------------------------------
// Per-frame upkeep
// ---------------------------------------------------------------------------------------------------------------
void ProgressionFrame() {
    if (sPotionCd > 0) {
        sPotionCd--;
    }
    for (size_t i = 0; i < sBuffs.size();) {
        if (--sBuffs[i].framesLeft <= 0) {
            ChatLine(sBuffs[i].name + " fades.", kYellow);
            sBuffs.erase(sBuffs.begin() + i);
        } else {
            i++;
        }
    }
    int font = TalentRank(T_MANA_FONT);
    if (font > 0 && !InCombat() && gSaveContext.magicLevel > 0 && gSaveContext.magic < gSaveContext.magicCapacity &&
        gSaveContext.magicState == MAGIC_STATE_IDLE) {
        if (++sMagicTimer >= 60 / font) {
            sMagicTimer = 0;
            gSaveContext.magic++;
        }
    }
}

static void RegisterGatherHooks() {
    COND_VB_SHOULD(VB_GRASS_DROP_ITEM, Enabled(), { OnGatherHerb(0.12f); });
    COND_VB_SHOULD(VB_BUSH_DROP_ITEM, Enabled(), { OnGatherHerb(0.5f); });
    COND_VB_SHOULD(VB_ROCK_DROP_ITEM, Enabled(), {
        Actor* rock = va_arg(args, Actor*);
        int amount = (rock != nullptr && rock->id == ACTOR_EN_ISHI) ? 1 : 3;
        if (rock != nullptr && rock->id == ACTOR_EN_ISHI && Rand_ZeroOne() >= 0.4f) {
            amount = 0;
        }
        if (amount > 0) {
            OnGatherOre(amount);
        }
    });
}

static RegisterShipInitFunc sGatherInit(RegisterGatherHooks, { CVAR_AZEROTH("Enabled") });

} // namespace Azeroth
