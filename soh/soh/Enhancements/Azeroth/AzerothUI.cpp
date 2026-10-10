// Hyrule of Warcraft - WoW style interface: XP bar, nameplates, target frame, floating combat text,
// chat log, quest tracker, character sheet, bags and quest log.

#ifdef _MSC_VER
#pragma warning(disable : 4244 4267 4305 4838 4018 4389 4456 4457 4458 4459)
#endif

#include "AzerothInternal.h"

#include <algorithm>
#include <cmath>
#include <deque>
#include <memory>
#include <imgui.h>
#include <imgui_internal.h>
#include <libultraship/bridge/consolevariablebridge.h>
#include <ship/Context.h>
#include <ship/window/gui/GuiWindow.h>

#include "soh/Enhancements/game-interactor/GameInteractor.h"
#include "soh/SohGui/SohMenu.h"
#include "soh/SohGui/SohGui.hpp"
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

// ---------------------------------------------------------------------------------------------------------------
// Colors
// ---------------------------------------------------------------------------------------------------------------
ImColor4 RarityColor(uint8_t r) {
    switch (r) {
        case POOR:
            return { 0.62f, 0.62f, 0.62f, 1.0f };
        case COMMON:
            return { 1.0f, 1.0f, 1.0f, 1.0f };
        case UNCOMMON:
            return { 0.12f, 1.0f, 0.0f, 1.0f };
        case RARE:
            return { 0.0f, 0.44f, 0.87f, 1.0f };
        case EPIC:
            return { 0.64f, 0.21f, 0.93f, 1.0f };
        default:
            return { 1.0f, 0.5f, 0.0f, 1.0f };
    }
}

ImColor4 ConColorRGB(int con) {
    switch (con) {
        case 0:
            return { 0.6f, 0.6f, 0.6f, 1.0f };
        case 1:
            return { 0.25f, 0.85f, 0.25f, 1.0f };
        case 2:
            return { 1.0f, 1.0f, 0.0f, 1.0f };
        case 3:
            return { 1.0f, 0.5f, 0.0f, 1.0f };
        default:
            return { 1.0f, 0.1f, 0.1f, 1.0f };
    }
}

static ImVec4 ColV4(ImColor4 c, float alphaMul = 1.0f) {
    return ImVec4(c.r, c.g, c.b, c.a * alphaMul);
}
static ImU32 ColU32(ImColor4 c, float alphaMul = 1.0f) {
    return ImGui::ColorConvertFloat4ToU32(ColV4(c, alphaMul));
}

static const ImColor4 kYellow = { 1.0f, 0.82f, 0.0f, 1.0f };
static const ImColor4 kWhite = { 1.0f, 1.0f, 1.0f, 1.0f };
static const ImColor4 kGrey = { 0.65f, 0.65f, 0.65f, 1.0f };
static const ImColor4 kGreen = { 0.12f, 1.0f, 0.0f, 1.0f };
static const ImColor4 kRed = { 1.0f, 0.25f, 0.25f, 1.0f };

// ---------------------------------------------------------------------------------------------------------------
// Feedback buffers
// ---------------------------------------------------------------------------------------------------------------
struct ChatEntry {
    std::string text;
    ImColor4 color;
    double time;
};
struct CenterEntry {
    std::string text;
    ImColor4 color;
    double until;
    float duration;
};
struct FloatEntry {
    Vec3f pos;
    std::string text;
    ImColor4 color;
    float scale;
    double start;
};

static std::deque<ChatEntry> sChat;
static std::deque<CenterEntry> sCenter;
static std::vector<FloatEntry> sFloats;

static double Now() {
    return ImGui::GetCurrentContext() != nullptr ? ImGui::GetTime() : 0.0;
}

void ChatLine(const std::string& text, ImColor4 color) {
    sChat.push_back({ text, color, Now() });
    while (sChat.size() > 60) {
        sChat.pop_front();
    }
}

void ChatLoot(const Item& item) {
    sChat.push_back({ "You receive loot: [" + item.name + "]", RarityColor(item.rarity), Now() });
    if (item.rarity >= RARE) {
        CenterText("[" + item.name + "]", RarityColor(item.rarity), 4.0f);
        Sfx_PlaySfxCentered(NA_SE_SY_TRE_BOX_APPEAR);
    } else {
        Sfx_PlaySfxCentered(NA_SE_SY_GET_ITEM);
    }
}

void CenterText(const std::string& text, ImColor4 color, float seconds) {
    sCenter.push_back({ text, color, Now() + seconds, seconds });
    while (sCenter.size() > 4) {
        sCenter.pop_front();
    }
}

void FloatText(float x, float y, float z, const std::string& text, ImColor4 color, float scale) {
    FloatEntry e;
    e.pos.x = x;
    e.pos.y = y;
    e.pos.z = z;
    e.text = text;
    e.color = color;
    e.scale = scale;
    e.start = Now();
    // Small horizontal jitter so stacked numbers stay readable
    e.pos.x += (Rand_ZeroOne() - 0.5f) * 20.0f;
    sFloats.push_back(e);
    if (sFloats.size() > 40) {
        sFloats.erase(sFloats.begin());
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Drawing helpers
// ---------------------------------------------------------------------------------------------------------------
struct GameRect {
    ImVec2 pos;  // full game image
    ImVec2 size;
    float x43;   // left edge of the 4:3 area
    float w43;   // width of the 4:3 area
    float s;     // UI scale
};

static GameRect GetGameRect() {
    GameRect r;
    ImGuiWindow* w = ImGui::FindWindowByName("Main Game");
    if (w != nullptr && w->Size.x > 32 && w->Size.y > 32) {
        r.pos = w->Pos;
        r.size = w->Size;
    } else {
        ImGuiViewport* vp = ImGui::GetMainViewport();
        r.pos = vp->Pos;
        r.size = vp->Size;
    }
    r.w43 = std::min(r.size.x, r.size.y * 4.0f / 3.0f);
    r.x43 = r.pos.x + (r.size.x - r.w43) * 0.5f;
    r.s = std::clamp(r.size.y / 720.0f, 0.75f, 2.5f);
    return r;
}

static bool Project(const GameRect& r, Vec3f world, ImVec2& out) {
    if (gPlayState == nullptr) {
        return false;
    }
    Vec3f proj;
    f32 w;
    SkinMatrix_Vec3fMtxFMultXYZW(&gPlayState->viewProjectionMtxF, &world, &proj, &w);
    if (w <= 1.0f) {
        return false;
    }
    float nx = proj.x / w;
    float ny = proj.y / w;
    if (nx < -1.3f || nx > 1.3f || ny < -1.3f || ny > 1.3f) {
        return false;
    }
    out.x = r.x43 + r.w43 * 0.5f + nx * r.w43 * 0.5f;
    out.y = r.pos.y + r.size.y * 0.5f - ny * r.size.y * 0.5f;
    return true;
}

static float BaseFont() {
    return ImGui::GetFontSize();
}

static ImVec2 TextSize(const std::string& t, float size) {
    return ImGui::GetFont()->CalcTextSizeA(size, FLT_MAX, 0.0f, t.c_str());
}

static void ShadowText(ImDrawList* dl, ImVec2 pos, float size, ImU32 col, const std::string& t, float alpha = 1.0f) {
    ImU32 shadow = IM_COL32(0, 0, 0, (int)(220 * alpha));
    float o = std::max(1.0f, size / 14.0f);
    dl->AddText(ImGui::GetFont(), size, ImVec2(pos.x + o, pos.y + o), shadow, t.c_str());
    dl->AddText(ImGui::GetFont(), size, ImVec2(pos.x - o * 0.5f, pos.y - o * 0.5f), shadow, t.c_str());
    dl->AddText(ImGui::GetFont(), size, pos, col, t.c_str());
}

static void CenteredText(ImDrawList* dl, float cx, float y, float size, ImU32 col, const std::string& t,
                         float alpha = 1.0f) {
    ImVec2 ts = TextSize(t, size);
    ShadowText(dl, ImVec2(cx - ts.x * 0.5f, y), size, col, t, alpha);
}

static void Bar(ImDrawList* dl, ImVec2 a, ImVec2 b, float frac, ImU32 fill, ImU32 bg, float rounding) {
    frac = std::clamp(frac, 0.0f, 1.0f);
    dl->AddRectFilled(a, b, bg, rounding);
    if (frac > 0.0f) {
        dl->AddRectFilled(a, ImVec2(a.x + (b.x - a.x) * frac, b.y), fill, rounding);
    }
    dl->AddRect(a, b, IM_COL32(0, 0, 0, 230), rounding, 0, 1.5f);
}

static std::string LevelText(Actor* actor, int lvl) {
    if (IsBoss(actor->id)) {
        return lvl - gState.level >= 10 ? "??" : std::to_string(lvl) + " Boss";
    }
    if (lvl - gState.level >= 10) {
        return "??";
    }
    return std::to_string(lvl) + (IsElite(actor->id) ? "+" : "");
}

static bool HudBlocked() {
    if (gPlayState == nullptr) {
        return true;
    }
    if (gPlayState->pauseCtx.state != 0) {
        return true;
    }
    Player* player = GET_PLAYER(gPlayState);
    if (player == nullptr) {
        return true;
    }
    return Player_InBlockingCsMode(gPlayState, player) != 0;
}

// ---------------------------------------------------------------------------------------------------------------
// HUD pieces
// ---------------------------------------------------------------------------------------------------------------
static void DrawNameplates(ImDrawList* dl, const GameRect& r) {
    if (!CVarGetInteger(CVAR_AZEROTH("Nameplates"), 1)) {
        return;
    }
    Player* player = GET_PLAYER(gPlayState);
    Actor* focus = player != nullptr ? player->focusActor : nullptr;
    const int cats[] = { ACTORCAT_ENEMY, ACTORCAT_BOSS };
    for (int cat : cats) {
        for (Actor* a = gPlayState->actorCtx.actorLists[cat].head; a != nullptr; a = a->next) {
            if (!IsTrackedEnemy(a) || a->draw == nullptr || !a->isDrawn) {
                continue;
            }
            if (!(a->flags & ACTOR_FLAG_ATTENTION_ENABLED) && !IsBoss(a->id)) {
                continue;
            }
            if (a->xyzDistToPlayerSq > 700.0f * 700.0f) {
                continue;
            }
            int hp = a->colChkInfo.health;
            if (hp <= 0 && !IsBoss(a->id)) {
                continue;
            }
            Vec3f top = a->world.pos;
            top.y = std::max(a->world.pos.y, a->focus.pos.y) + 22.0f;
            ImVec2 sp;
            if (!Project(r, top, sp)) {
                continue;
            }
            float alpha = a->xyzDistToPlayerSq > 550.0f * 550.0f ? 0.6f : 1.0f;
            bool targeted = a == focus;
            float s = r.s * (targeted ? 1.15f : 1.0f);
            int lvl = MobLevel(a);
            int maxHp = EnemyMaxHealth(a);
            ImColor4 con = ConColorRGB(ConColor(lvl));

            float bw = 90.0f * s, bh = 8.0f * s;
            ImVec2 a0(sp.x - bw * 0.5f, sp.y - bh);
            Bar(dl, a0, ImVec2(a0.x + bw, a0.y + bh), (float)hp / (float)maxHp,
                targeted ? IM_COL32(230, 40, 40, (int)(255 * alpha)) : IM_COL32(190, 30, 30, (int)(230 * alpha)),
                IM_COL32(20, 20, 20, (int)(180 * alpha)), 2.0f * s);
            if (targeted) {
                dl->AddRect(ImVec2(a0.x - 2, a0.y - 2), ImVec2(a0.x + bw + 2, a0.y + bh + 2),
                            IM_COL32(255, 255, 255, 220), 2.0f * s, 0, 1.5f);
            }
            float fs = BaseFont() * 0.95f * s;
            std::string name = GetEnemyName(a->id);
            std::string lt = LevelText(a, lvl);
            ImVec2 ns = TextSize(name, fs);
            ImVec2 ls = TextSize(lt + " ", fs);
            float total = ns.x + ls.x;
            float x = sp.x - total * 0.5f;
            float y = a0.y - fs - 2.0f * s;
            ShadowText(dl, ImVec2(x, y), fs, ColU32(con, alpha), lt + " ", alpha);
            ImColor4 nameCol = IsBoss(a->id) ? ImColor4{ 1.0f, 0.5f, 0.1f, 1.0f } : ImColor4{ 1.0f, 0.3f, 0.3f, 1.0f };
            ShadowText(dl, ImVec2(x + ls.x, y), fs, ColU32(nameCol, alpha), name, alpha);
        }
    }
}

static void DrawQuestMarkers(ImDrawList* dl, const GameRect& r) {
    bool available = false, ready = false;
    for (const QuestDef& q : GetQuests()) {
        if (QuestAvailable(q)) {
            available = true;
        }
        auto it = gState.quests.find(q.id);
        if (it != gState.quests.end() && it->second.status == Q_READY && CanTurnInHere(q)) {
            ready = true;
        }
    }
    if (!available && !ready) {
        return;
    }
    // Put the marker over the nearest friendly NPC, WoW style.
    Actor* best = nullptr;
    for (Actor* a = gPlayState->actorCtx.actorLists[ACTORCAT_NPC].head; a != nullptr; a = a->next) {
        if (a->draw == nullptr || !a->isDrawn) {
            continue;
        }
        if (best == nullptr || a->xyzDistToPlayerSq < best->xyzDistToPlayerSq) {
            best = a;
        }
    }
    if (best == nullptr || best->xyzDistToPlayerSq > 1500.0f * 1500.0f) {
        return;
    }
    Vec3f top = best->world.pos;
    top.y = std::max(best->world.pos.y, best->focus.pos.y) + 35.0f;
    ImVec2 sp;
    if (!Project(r, top, sp)) {
        return;
    }
    float bob = (float)std::sin(Now() * 3.0) * 4.0f * r.s;
    float fs = BaseFont() * 3.0f * r.s;
    CenteredText(dl, sp.x, sp.y - fs + bob, fs, ColU32(kYellow), ready ? "?" : "!");
}

static void DrawFloats(ImDrawList* dl, const GameRect& r) {
    double now = Now();
    const float life = 1.3f;
    for (size_t i = 0; i < sFloats.size();) {
        FloatEntry& e = sFloats[i];
        float t = (float)(now - e.start);
        if (t > life) {
            sFloats.erase(sFloats.begin() + i);
            continue;
        }
        i++;
        ImVec2 sp;
        if (!Project(r, e.pos, sp)) {
            continue;
        }
        float k = t / life;
        float alpha = k < 0.6f ? 1.0f : 1.0f - (k - 0.6f) / 0.4f;
        float pop = e.scale > 1.5f && t < 0.15f ? 1.0f + (0.15f - t) * 4.0f : 1.0f;
        float fs = BaseFont() * 1.4f * e.scale * pop * r.s;
        CenteredText(dl, sp.x, sp.y - fs - k * 60.0f * r.s, fs, ColU32(e.color, alpha), e.text, alpha);
    }
}

static void DrawXpBar(ImDrawList* dl, const GameRect& r) {
    float s = r.s;
    float w = r.w43 * 0.62f;
    float h = 11.0f * s;
    float cx = r.x43 + r.w43 * 0.5f;
    float y = r.pos.y + r.size.y - h - 6.0f * s;
    ImVec2 a(cx - w * 0.5f, y), b(cx + w * 0.5f, y + h);
    bool max = gState.level >= MAX_LEVEL;
    float frac = max ? 1.0f : (float)gState.xp / (float)XpToLevel(gState.level);
    Bar(dl, a, b, frac, max ? IM_COL32(200, 160, 30, 235) : IM_COL32(150, 40, 190, 235), IM_COL32(15, 10, 25, 190),
        3.0f * s);
    for (int i = 1; i < 20; i++) {
        float x = a.x + w * i / 20.0f;
        dl->AddLine(ImVec2(x, a.y + 2), ImVec2(x, b.y - 2), IM_COL32(0, 0, 0, 120), 1.0f);
    }
    float fs = BaseFont() * 0.85f * s;
    std::string t = max ? std::string("Level 60 - Maximum level") :
                          "Level " + std::to_string(gState.level) + "   XP " + std::to_string(gState.xp) + " / " +
                              std::to_string(XpToLevel(gState.level));
    CenteredText(dl, cx, a.y + (h - fs) * 0.5f, fs, IM_COL32(255, 255, 255, 240), t);

    // Level badge
    float rad = 13.0f * s;
    ImVec2 c(a.x - rad - 6.0f * s, a.y + h * 0.5f);
    dl->AddCircleFilled(c, rad, IM_COL32(25, 20, 10, 230));
    dl->AddCircle(c, rad, IM_COL32(220, 180, 60, 255), 0, 2.0f * s);
    float lf = BaseFont() * 1.05f * s;
    std::string lv = std::to_string(gState.level);
    ImVec2 ls = TextSize(lv, lf);
    ShadowText(dl, ImVec2(c.x - ls.x * 0.5f, c.y - ls.y * 0.5f), lf, ColU32(kYellow), lv);
}

static void DrawTargetFrame(ImDrawList* dl, const GameRect& r) {
    Player* player = GET_PLAYER(gPlayState);
    if (player == nullptr) {
        return;
    }
    Actor* t = player->focusActor;
    if (t == nullptr || !IsTrackedEnemy(t)) {
        return;
    }
    float s = r.s;
    float w = 250.0f * s, h = 54.0f * s;
    float cx = r.x43 + r.w43 * 0.5f;
    ImVec2 a(cx - w * 0.5f, r.pos.y + 8.0f * s);
    ImVec2 b(a.x + w, a.y + h);
    bool boss = IsBoss(t->id);
    bool elite = IsElite(t->id);
    dl->AddRectFilled(a, b, IM_COL32(0, 0, 0, 170), 6.0f * s);
    dl->AddRect(a, b, boss ? IM_COL32(255, 130, 30, 255) : (elite ? IM_COL32(230, 190, 60, 255) : IM_COL32(150, 150, 150, 200)),
                6.0f * s, 0, (boss || elite) ? 2.5f * s : 1.5f * s);

    int lvl = MobLevel(t);
    int hp = std::max<int>(0, t->colChkInfo.health);
    int maxHp = EnemyMaxHealth(t);
    float fs = BaseFont() * 1.0f * s;
    std::string name = GetEnemyName(t->id);
    ShadowText(dl, ImVec2(a.x + 44.0f * s, a.y + 5.0f * s), fs, IM_COL32(255, 255, 255, 255), name);
    std::string tag;
    if (boss) {
        tag = CurrentContent() == CONTENT_RAID ? "Raid Boss" : "Dungeon Boss";
    } else if (elite) {
        tag = "Elite";
    } else if (CurrentContent() != CONTENT_WORLD) {
        tag = ContentLabel(CurrentContent());
    }
    if (!tag.empty()) {
        ImVec2 ts = TextSize(tag, fs * 0.85f);
        ShadowText(dl, ImVec2(b.x - ts.x - 8.0f * s, a.y + 6.0f * s), fs * 0.85f, IM_COL32(255, 200, 80, 255), tag);
    }
    // level circle
    ImVec2 c(a.x + 22.0f * s, a.y + h * 0.5f);
    dl->AddCircleFilled(c, 16.0f * s, IM_COL32(20, 20, 20, 240));
    dl->AddCircle(c, 16.0f * s, ColU32(ConColorRGB(ConColor(lvl))), 0, 2.0f * s);
    std::string lt = (lvl - gState.level >= 10) ? "??" : std::to_string(lvl);
    ImVec2 ls = TextSize(lt, fs);
    ShadowText(dl, ImVec2(c.x - ls.x * 0.5f, c.y - ls.y * 0.5f), fs, ColU32(ConColorRGB(ConColor(lvl))), lt);
    // health
    ImVec2 ha(a.x + 44.0f * s, a.y + 26.0f * s), hb(b.x - 8.0f * s, a.y + 44.0f * s);
    Bar(dl, ha, hb, (float)hp / (float)maxHp, IM_COL32(40, 200, 40, 255), IM_COL32(30, 30, 30, 220), 2.0f * s);
    std::string ht = std::to_string(hp * 10) + " / " + std::to_string(maxHp * 10);
    CenteredText(dl, (ha.x + hb.x) * 0.5f, ha.y + (hb.y - ha.y - fs * 0.8f) * 0.5f, fs * 0.8f,
                 IM_COL32(255, 255, 255, 255), ht);
}

static void DrawQuestTracker(ImDrawList* dl, const GameRect& r) {
    if (!CVarGetInteger(CVAR_AZEROTH("QuestTracker"), 1)) {
        return;
    }
    float s = r.s;
    float fs = BaseFont() * 0.9f * s;
    float right = r.pos.x + r.size.x - 12.0f * s;
    float y = r.pos.y + r.size.y * 0.30f;
    float width = 260.0f * s;
    float x = right - width;
    bool header = false;
    auto ensureHeader = [&]() {
        if (!header) {
            ShadowText(dl, ImVec2(x, y), fs * 1.1f, ColU32(kYellow), "Quests");
            y += fs * 1.4f;
            header = true;
        }
    };
    int shown = 0;
    for (const QuestDef& q : GetQuests()) {
        auto it = gState.quests.find(q.id);
        if (it == gState.quests.end() || (it->second.status != Q_ACTIVE && it->second.status != Q_READY)) {
            continue;
        }
        if (shown >= 6) {
            break;
        }
        ensureHeader();
        bool ready = it->second.status == Q_READY;
        ShadowText(dl, ImVec2(x, y), fs, ready ? ColU32(kGreen) : ColU32(kYellow),
                   std::string(q.title) + (ready ? " (Complete)" : ""));
        y += fs * 1.15f;
        std::string line = ready ? std::string("  - Return to ") + q.giver :
                                   std::string("  - ") + q.targetLabel + ": " + std::to_string(it->second.progress) +
                                       "/" + std::to_string(q.count);
        ShadowText(dl, ImVec2(x, y), fs * 0.92f, ColU32(kWhite, 0.9f), line);
        y += fs * 1.35f;
        shown++;
    }
    bool avail = false;
    for (const QuestDef& q : GetQuests()) {
        if (QuestAvailable(q)) {
            avail = true;
            break;
        }
    }
    if (avail) {
        ensureHeader();
        ShadowText(dl, ImVec2(x, y), fs * 0.92f, ColU32(kYellow), "! New quests here - press L");
    }
}

static void DrawChat(ImDrawList* dl, const GameRect& r) {
    if (!CVarGetInteger(CVAR_AZEROTH("Chat"), 1) || sChat.empty()) {
        return;
    }
    float s = r.s;
    float fs = BaseFont() * 0.85f * s;
    float x = r.pos.x + 12.0f * s;
    float bottom = r.pos.y + r.size.y * 0.74f;
    double now = Now();
    int lines = 0;
    float y = bottom;
    for (auto it = sChat.rbegin(); it != sChat.rend() && lines < 8; ++it, ++lines) {
        float age = (float)(now - it->time);
        if (age > 14.0f) {
            break;
        }
        float alpha = age < 11.0f ? 1.0f : 1.0f - (age - 11.0f) / 3.0f;
        y -= fs * 1.25f;
        ShadowText(dl, ImVec2(x, y), fs, ColU32(it->color, alpha), it->text, alpha);
    }
}

static void DrawCenterText(ImDrawList* dl, const GameRect& r) {
    double now = Now();
    while (!sCenter.empty() && sCenter.front().until < now) {
        sCenter.pop_front();
    }
    float s = r.s;
    float fs = BaseFont() * 1.9f * s;
    float y = r.pos.y + r.size.y * 0.20f;
    float cx = r.x43 + r.w43 * 0.5f;
    for (const auto& c : sCenter) {
        float left = (float)(c.until - now);
        float alpha = left > 1.0f ? 1.0f : std::max(0.0f, left);
        CenteredText(dl, cx, y, fs, ColU32(c.color, alpha), c.text, alpha);
        y += fs * 1.2f;
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Windows
// ---------------------------------------------------------------------------------------------------------------
static bool sShowChar = false, sShowBags = false, sShowQuests = false, sShowTalents = false, sShowProfs = false;

static void StatLine(const char* label, int v, int gearBonus) {
    ImGui::Text("%s", label);
    ImGui::SameLine(110);
    if (gearBonus > 0) {
        ImGui::TextColored(ColV4(kGreen), "%d", v);
    } else {
        ImGui::Text("%d", v);
    }
}

static void ItemTooltip(const Item& it) {
    ImGui::BeginTooltip();
    ImGui::PushTextWrapPos(320.0f);
    ImGui::TextColored(ColV4(RarityColor(it.rarity)), "%s", it.name.c_str());
    if (it.slot < SLOT_COUNT) {
        ImGui::TextColored(ColV4(kWhite), "Binds when picked up");
        ImGui::Text("%s", SlotName(it.slot));
        if (it.armor > 0) {
            ImGui::Text("%d Armor", it.armor);
        }
        if (it.weaponPct > 0) {
            ImGui::Text("+%d%% Weapon Damage", it.weaponPct);
        }
        if (it.str) {
            ImGui::Text("+%d Strength", it.str);
        }
        if (it.agi) {
            ImGui::Text("+%d Agility", it.agi);
        }
        if (it.sta) {
            ImGui::Text("+%d Stamina", it.sta);
        }
        if (it.spi) {
            ImGui::Text("+%d Spirit", it.spi);
        }
        ImGui::TextColored(it.reqLevel > gState.level ? ColV4(kRed) : ColV4(kWhite), "Requires Level %d", it.reqLevel);
        ImGui::TextColored(ColV4(kYellow), "Item Level %d", it.ilvl);
        if (it.slot < SLOT_COUNT && gState.equipped[it.slot].valid) {
            const Item& cur = gState.equipped[it.slot];
            ImGui::Separator();
            ImGui::TextColored(ColV4(kGrey), "Currently equipped:");
            ImGui::TextColored(ColV4(RarityColor(cur.rarity)), "%s", cur.name.c_str());
            int dStats = (it.str + it.agi + it.sta + it.spi) - (cur.str + cur.agi + cur.sta + cur.spi);
            int dArmor = it.armor - cur.armor;
            ImGui::TextColored(dStats >= 0 ? ColV4(kGreen) : ColV4(kRed), "%+d total stats", dStats);
            if (dArmor != 0) {
                ImGui::TextColored(dArmor >= 0 ? ColV4(kGreen) : ColV4(kRed), "%+d armor", dArmor);
            }
        }
    } else {
        ImGui::TextColored(ColV4(kGrey), "Junk - sell it for rupees");
    }
    ImGui::Text("Sell Price: %d rupees", it.sellValue);
    ImGui::PopTextWrapPos();
    ImGui::EndTooltip();
}

static void DrawCharacterWindow() {
    ImGui::SetNextWindowSize(ImVec2(560, 430), ImGuiCond_FirstUseEver);
    if (!ImGui::Begin("Character - Link##Azeroth", &sShowChar, ImGuiWindowFlags_NoDocking)) {
        ImGui::End();
        return;
    }
    Stats s = GetStats();
    int zl = CurrentZoneLevel();
    ImGui::TextColored(ColV4(kYellow), "Link");
    ImGui::SameLine();
    ImGui::Text("Level %d Hylian Hero of Time", gState.level);
    if (gState.level < MAX_LEVEL) {
        ImGui::ProgressBar((float)gState.xp / (float)XpToLevel(gState.level), ImVec2(-1, 0),
                           (std::to_string(gState.xp) + " / " + std::to_string(XpToLevel(gState.level)) + " XP").c_str());
    }
    ImGui::Separator();

    if (ImGui::BeginTable("##charcols", 2, ImGuiTableFlags_BordersInnerV)) {
        ImGui::TableNextColumn();
        ImGui::TextColored(ColV4(kYellow), "Equipment");
        for (int i = 0; i < SLOT_COUNT; i++) {
            ImGui::PushID(i);
            ImGui::TextColored(ColV4(kGrey), "%-8s", SlotName(i));
            ImGui::SameLine(80);
            const Item& it = gState.equipped[i];
            if (it.valid) {
                ImGui::TextColored(ColV4(RarityColor(it.rarity)), "%s", it.name.c_str());
                if (ImGui::IsItemHovered()) {
                    ItemTooltip(it);
                }
                if (ImGui::IsItemClicked(ImGuiMouseButton_Right)) {
                    Unequip(i);
                }
            } else {
                ImGui::TextColored(ColV4(kGrey, 0.5f), "(empty)");
            }
            ImGui::PopID();
        }
        ImGui::TextColored(ColV4(kGrey, 0.8f), "Right-click an item to unequip it.");

        ImGui::TableNextColumn();
        ImGui::TextColored(ColV4(kYellow), "Attributes");
        int gStr = 0, gAgi = 0, gSta = 0, gSpi = 0;
        for (int i = 0; i < SLOT_COUNT; i++) {
            if (gState.equipped[i].valid) {
                gStr += gState.equipped[i].str;
                gAgi += gState.equipped[i].agi;
                gSta += gState.equipped[i].sta;
                gSpi += gState.equipped[i].spi;
            }
        }
        StatLine("Strength", s.str, gStr);
        StatLine("Agility", s.agi, gAgi);
        StatLine("Stamina", s.sta, gSta);
        StatLine("Spirit", s.spi, gSpi);
        StatLine("Armor", s.armor, 1);
        ImGui::Spacing();
        ImGui::TextColored(ColV4(kYellow), "Versus level %d enemies (%s)", zl, CurrentZoneName());
        ImGui::Text("Damage:      %d%%", (int)std::lround(DamageMultiplier(zl) * 100.0f));
        ImGui::Text("Crit chance: %.1f%%", CritChance(zl) * 100.0f);
        ImGui::Text("Damage taken: %+d%%", (int)std::lround(-DamageReduction(zl) * 100.0f));
        ImGui::Text("Weapon bonus: +%d%%", s.weaponPct);
        ImGui::Spacing();
        ImGui::Text("Enemies slain: %u", gState.totalKills);
        ImGui::EndTable();
    }
    ImGui::Separator();
    int diff = Difficulty();
    ImGui::Text("Dungeon & Raid difficulty:");
    ImGui::SameLine();
    for (int d = 0; d < 3; d++) {
        if (d > 0) {
            ImGui::SameLine();
        }
        if (ImGui::RadioButton(DifficultyName(d), diff == d)) {
            CVarSetInteger(CVAR_AZEROTH("Difficulty"), d);
            Ship::Context::GetRawInstance()->GetWindow()->GetGui()->SaveConsoleVariablesNextFrame();
        }
    }
    ImGui::End();
}

static void DrawBagsWindow() {
    ImGui::SetNextWindowSize(ImVec2(420, 480), ImGuiCond_FirstUseEver);
    if (!ImGui::Begin("Backpack##Azeroth", &sShowBags, ImGuiWindowFlags_NoDocking)) {
        ImGui::End();
        return;
    }
    ImGui::Text("Slots: %d / %d", (int)gState.bags.size(), BAG_SLOTS);
    ImGui::SameLine();
    ImGui::TextColored(ColV4(kGreen), "   Rupees: %d", gSaveContext.rupees);
    if (ImGui::Button("Sell all junk (grey items)")) {
        SellAllJunk();
    }
    ImGui::Separator();
    int toEquip = -1, toSell = -1;
    for (int i = 0; i < (int)gState.bags.size(); i++) {
        const Item& it = gState.bags[i];
        ImGui::PushID(i);
        bool usable = it.slot < SLOT_COUNT;
        if (usable) {
            if (ImGui::SmallButton("Equip")) {
                toEquip = i;
            }
            ImGui::SameLine();
        }
        if (ImGui::SmallButton("Sell")) {
            toSell = i;
        }
        ImGui::SameLine();
        ImGui::TextColored(ColV4(RarityColor(it.rarity)), "%s", it.name.c_str());
        if (ImGui::IsItemHovered()) {
            ItemTooltip(it);
        }
        ImGui::PopID();
    }
    if (gState.bags.empty()) {
        ImGui::TextColored(ColV4(kGrey), "Your bags are empty. Defeat enemies to find loot!");
    }
    if (toEquip >= 0) {
        EquipFromBag(toEquip);
    } else if (toSell >= 0) {
        SellFromBag(toSell);
    }
    ImGui::End();
}

static ImVec4 QuestLevelColor(int qlvl) {
    return ColV4(ConColorRGB(ConColor(qlvl)));
}

static void DrawQuestWindow() {
    ImGui::SetNextWindowSize(ImVec2(520, 520), ImGuiCond_FirstUseEver);
    if (!ImGui::Begin("Quest Log##Azeroth", &sShowQuests, ImGuiWindowFlags_NoDocking)) {
        ImGui::End();
        return;
    }
    ImGui::TextColored(ColV4(kYellow), "%s", CurrentZoneName());
    ContentKind c = CurrentContent();
    if (c != CONTENT_WORLD) {
        ImGui::SameLine();
        ImGui::TextColored(ImVec4(1.0f, 0.6f, 0.2f, 1.0f), "[%s - %s]", ContentLabel(c), DifficultyName(Difficulty()));
    }
    ImGui::Separator();

    int accept = -1, turnIn = -1, abandon = -1;
    bool anyAvail = false;
    if (ImGui::CollapsingHeader("Available here", ImGuiTreeNodeFlags_DefaultOpen)) {
        for (const QuestDef& q : GetQuests()) {
            if (!QuestAvailable(q)) {
                continue;
            }
            anyAvail = true;
            ImGui::PushID(q.id);
            ImGui::TextColored(QuestLevelColor(q.level), "[%d] %s", q.level, q.title);
            ImGui::TextColored(ColV4(kGrey), "%s says:", q.giver);
            ImGui::PushTextWrapPos(0.0f);
            ImGui::TextWrapped("\"%s\"", q.text);
            ImGui::PopTextWrapPos();
            ImGui::Text("Objective: %s x%d", q.targetLabel, q.count);
            if (ImGui::Button("Accept")) {
                accept = q.id;
            }
            ImGui::Separator();
            ImGui::PopID();
        }
        if (!anyAvail) {
            ImGui::TextColored(ColV4(kGrey), "No new quests in this area. Explore Hyrule to find more!");
        }
    }
    if (ImGui::CollapsingHeader("Active quests", ImGuiTreeNodeFlags_DefaultOpen)) {
        bool any = false;
        for (const QuestDef& q : GetQuests()) {
            auto it = gState.quests.find(q.id);
            if (it == gState.quests.end() || (it->second.status != Q_ACTIVE && it->second.status != Q_READY)) {
                continue;
            }
            any = true;
            ImGui::PushID(1000 + q.id);
            bool ready = it->second.status == Q_READY;
            ImGui::TextColored(QuestLevelColor(q.level), "[%d] %s", q.level, q.title);
            if (ready) {
                ImGui::SameLine();
                ImGui::TextColored(ColV4(kGreen), "(Complete)");
            }
            ImGui::Text("  %s: %d/%d", q.targetLabel, it->second.progress, q.count);
            const ZoneInfo* gz = GetZone(q.giverScene);
            ImGui::TextColored(ColV4(kGrey), "  Quest giver: %s (%s)", q.giver, gz ? gz->name : "?");
            if (ready) {
                if (CanTurnInHere(q)) {
                    if (ImGui::Button("Complete Quest")) {
                        turnIn = q.id;
                    }
                } else {
                    ImGui::TextColored(ColV4(kYellow), "  Return to %s to collect your reward.", gz ? gz->name : "?");
                }
            } else if (ImGui::SmallButton("Abandon")) {
                abandon = q.id;
            }
            ImGui::Separator();
            ImGui::PopID();
        }
        if (!any) {
            ImGui::TextColored(ColV4(kGrey), "Your quest log is empty.");
        }
    }
    int done = 0;
    for (const auto& [id, st] : gState.quests) {
        if (st.status == Q_DONE) {
            done++;
        }
    }
    ImGui::TextColored(ColV4(kGrey), "Quests completed: %d / %d", done, (int)GetQuests().size());
    if (accept >= 0) {
        AcceptQuest(accept);
    }
    if (turnIn >= 0) {
        TurnInQuest(turnIn);
    }
    if (abandon >= 0) {
        AbandonQuest(abandon);
    }
    ImGui::End();
}


static void DrawTalentWindow() {
    ImGui::SetNextWindowSize(ImVec2(780, 470), ImGuiCond_FirstUseEver);
    if (!ImGui::Begin("Talents##Azeroth", &sShowTalents, ImGuiWindowFlags_NoDocking)) {
        ImGui::End();
        return;
    }
    int total = TalentPointsTotal();
    int spent = TalentPointsSpent();
    ImGui::TextColored(ColV4(kYellow), "Talent points: %d available  (%d spent)", total - spent, spent);
    if (total == 0) {
        ImGui::SameLine();
        ImGui::TextColored(ColV4(kGrey), "- you earn your first talent point at level 10.");
    }
    ImGui::Separator();
    int learn = -1;
    if (ImGui::BeginTable("##trees", 3, ImGuiTableFlags_BordersInnerV)) {
        for (int tree = 0; tree < 3; tree++) {
            ImGui::TableNextColumn();
            ImGui::TextColored(ColV4(kYellow), "%s (%d)", TreeName(tree), TreePoints(tree));
            ImGui::Spacing();
            for (const TalentDef& t : GetTalents()) {
                if (t.tree != tree) {
                    continue;
                }
                ImGui::PushID(t.id);
                int rank = TalentRank(t.id);
                bool can = CanLearnTalent(t);
                bool locked = TreePoints(tree) < t.reqTreePoints;
                ImVec4 col = rank == t.maxRank ? ColV4(kYellow) : (rank > 0 || can ? ColV4(kGreen) : ColV4(kGrey));
                ImGui::BeginDisabled(!can);
                if (ImGui::SmallButton("+")) {
                    learn = t.id;
                }
                ImGui::EndDisabled();
                ImGui::SameLine();
                ImGui::TextColored(col, "%s  %d/%d", t.name, rank, t.maxRank);
                if (ImGui::IsItemHovered()) {
                    ImGui::BeginTooltip();
                    ImGui::TextColored(ColV4(kWhite), "%s", t.name);
                    ImGui::Text("Rank %d/%d", rank, t.maxRank);
                    ImGui::Text(t.desc, std::max(1, rank) * t.perRank);
                    if (rank > 0 && rank < t.maxRank) {
                        ImGui::TextColored(ColV4(kGrey), "Next rank:");
                        ImGui::Text(t.desc, (rank + 1) * t.perRank);
                    }
                    if (locked) {
                        ImGui::TextColored(ColV4(kRed), "Requires %d points in %s", t.reqTreePoints, TreeName(tree));
                    }
                    ImGui::EndTooltip();
                }
                ImGui::PopID();
            }
        }
        ImGui::EndTable();
    }
    ImGui::Separator();
    if (ImGui::Button("Reset talents")) {
        ResetTalents();
    }
    ImGui::SameLine();
    ImGui::TextColored(ColV4(kGrey), "Costs %d rupees", RespecCost());
    if (learn >= 0) {
        LearnTalent(learn);
    }
    ImGui::End();
}

static ImVec4 RecipeCol(int c) {
    switch (c) {
        case 0:
            return ImVec4(0.6f, 0.6f, 0.6f, 1.0f);
        case 1:
            return ImVec4(0.25f, 0.85f, 0.25f, 1.0f);
        case 2:
            return ImVec4(1.0f, 1.0f, 0.0f, 1.0f);
        case 3:
            return ImVec4(1.0f, 0.5f, 0.0f, 1.0f);
        default:
            return ImVec4(1.0f, 0.2f, 0.2f, 1.0f);
    }
}

static void DrawProfessionWindow() {
    ImGui::SetNextWindowSize(ImVec2(600, 560), ImGuiCond_FirstUseEver);
    if (!ImGui::Begin("Professions##Azeroth", &sShowProfs, ImGuiWindowFlags_NoDocking)) {
        ImGui::End();
        return;
    }
    ImGui::TextColored(ColV4(kYellow), "Your professions (max 2)");
    uint8_t unlearn = P_NONE, learnP = P_NONE;
    for (int i = 0; i < 2; i++) {
        uint8_t p = gState.prof[i];
        ImGui::PushID(i);
        if (p == P_NONE) {
            ImGui::TextColored(ColV4(kGrey), "  (empty slot)");
        } else {
            ImGui::Text("  %s", ProfName(p));
            ImGui::SameLine(150);
            ImGui::ProgressBar(gState.skill[p] / 300.0f, ImVec2(200, 0),
                               (std::to_string(gState.skill[p]) + " / 300").c_str());
            ImGui::SameLine();
            if (ImGui::SmallButton("Unlearn")) {
                unlearn = p;
            }
        }
        ImGui::PopID();
    }
    if (gState.prof[0] == P_NONE || gState.prof[1] == P_NONE) {
        ImGui::Text("Learn:");
        for (uint8_t p = P_HERBALISM; p < P_COUNT; p++) {
            if (KnowsProf(p)) {
                continue;
            }
            ImGui::SameLine();
            if (ImGui::SmallButton(ProfName(p))) {
                learnP = p;
            }
        }
        ImGui::TextColored(ColV4(kGrey),
                           "Herbalism: cut grass and bushes. Mining: break rocks. Skinning: defeat beasts.\n"
                           "Alchemy uses herbs, Blacksmithing uses ore, Leatherworking uses leather.");
    }
    ImGui::Separator();

    std::string use;
    if (ImGui::CollapsingHeader("Reagents & consumables", ImGuiTreeNodeFlags_DefaultOpen)) {
        if (gState.reagents.empty()) {
            ImGui::TextColored(ColV4(kGrey), "Nothing yet.");
        }
        for (const auto& [name, n] : gState.reagents) {
            ImGui::PushID(name.c_str());
            if (IsConsumable(name)) {
                if (ImGui::SmallButton("Use")) {
                    use = name;
                }
                ImGui::SameLine();
                ImGui::TextColored(ColV4(kGreen), "%s x%d", name.c_str(), n);
            } else {
                ImGui::Text("%s x%d", name.c_str(), n);
            }
            ImGui::PopID();
        }
        ImGui::TextColored(ColV4(kGrey), "Press Q to drink your best healing potion (1 minute cooldown).");
    }

    const Recipe* craft = nullptr;
    for (int i = 0; i < 2; i++) {
        uint8_t p = gState.prof[i];
        if (p == P_NONE || IsGathering(p)) {
            continue;
        }
        if (ImGui::CollapsingHeader((std::string(ProfName(p)) + " recipes").c_str(), ImGuiTreeNodeFlags_DefaultOpen)) {
            for (const Recipe& r : GetRecipes()) {
                if (r.prof != p) {
                    continue;
                }
                int c = RecipeColor(r);
                if (c == 4 && r.reqSkill > gState.skill[p] + 60) {
                    continue; // hide far-off recipes
                }
                ImGui::PushID(r.name.c_str());
                ImGui::BeginDisabled(!CanCraft(r));
                if (ImGui::SmallButton("Create")) {
                    craft = &r;
                }
                ImGui::EndDisabled();
                ImGui::SameLine();
                ImGui::TextColored(RecipeCol(c), "%s", r.name.c_str());
                ImGui::SameLine();
                std::string mats = "(";
                for (size_t m = 0; m < r.mats.size(); m++) {
                    auto it = gState.reagents.find(r.mats[m].first);
                    int have = it == gState.reagents.end() ? 0 : it->second;
                    mats += (m ? ", " : "") + r.mats[m].first + " " + std::to_string(have) + "/" +
                            std::to_string(r.mats[m].second);
                }
                mats += ")";
                ImGui::TextColored(ColV4(kGrey), "%s", mats.c_str());
                if (c == 4) {
                    ImGui::SameLine();
                    ImGui::TextColored(ColV4(kRed), "Requires %d", r.reqSkill);
                }
                ImGui::PopID();
            }
        }
    }
    if (unlearn != P_NONE) {
        UnlearnProf(unlearn);
    }
    if (learnP != P_NONE) {
        LearnProf(learnP);
    }
    if (!use.empty()) {
        UseConsumable(use);
    }
    if (craft != nullptr) {
        Craft(*craft);
    }
    ImGui::End();
}

static void DrawBuffs(ImDrawList* dl, const GameRect& r) {
    const auto& buffs = GetBuffs();
    float s = r.s;
    float fs = BaseFont() * 0.8f * s;
    float x = r.pos.x + r.size.x - 12.0f * s;
    float y = r.pos.y + r.size.y * 0.22f;
    for (const Buff& b : buffs) {
        int secs = b.framesLeft / 20;
        std::string t = b.name + "  " + std::to_string(secs / 60) + ":" + (secs % 60 < 10 ? "0" : "") +
                        std::to_string(secs % 60);
        ImVec2 ts = TextSize(t, fs);
        ShadowText(dl, ImVec2(x - ts.x, y), fs, ColU32(kGreen), t);
        y += fs * 1.2f;
    }
    if (PotionCooldownFrames() > 0) {
        std::string t = "Potion cooldown " + std::to_string(PotionCooldownFrames() / 20 + 1) + "s";
        ImVec2 ts = TextSize(t, fs);
        ShadowText(dl, ImVec2(x - ts.x, y), fs, ColU32(kGrey), t);
    }
}

static void DrawMicroMenu(const GameRect& r) {
    float s = r.s;
    float barRight = r.x43 + r.w43 * 0.5f + r.w43 * 0.31f;
    float barTop = r.pos.y + r.size.y - 17.0f * s;
    ImGui::SetNextWindowPos(ImVec2(barRight, barTop - 4.0f * s), ImGuiCond_Always, ImVec2(1.0f, 1.0f));
    ImGui::SetNextWindowBgAlpha(0.35f);
    ImGuiWindowFlags f = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoSavedSettings |
                         ImGuiWindowFlags_NoFocusOnAppearing | ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoDocking |
                         ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoMove;
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(3, 3));
    if (ImGui::Begin("##AzerothMicro", nullptr, f)) {
        if (ImGui::SmallButton("Char (I)")) {
            sShowChar = !sShowChar;
        }
        ImGui::SameLine();
        if (ImGui::SmallButton("Bags (B)")) {
            sShowBags = !sShowBags;
        }
        ImGui::SameLine();
        if (ImGui::SmallButton("Quests (L)")) {
            sShowQuests = !sShowQuests;
        }
        ImGui::SameLine();
        bool pts = TalentPointsSpent() < TalentPointsTotal();
        if (pts) {
            ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1.0f, 0.85f, 0.2f, 1.0f));
        }
        if (ImGui::SmallButton("Talents (N)")) {
            sShowTalents = !sShowTalents;
        }
        if (pts) {
            ImGui::PopStyleColor();
        }
        ImGui::SameLine();
        if (ImGui::SmallButton("Profs (K)")) {
            sShowProfs = !sShowProfs;
        }
    }
    ImGui::End();
    ImGui::PopStyleVar();
}

// ---------------------------------------------------------------------------------------------------------------
// The always-on HUD window
// ---------------------------------------------------------------------------------------------------------------
class HudWindow final : public Ship::GuiWindow {
  public:
    using GuiWindow::GuiWindow;
    void InitElement() override {
    }
    void DrawElement() override {
    }
    void UpdateElement() override {
    }
    void Draw() override {
        if (!Enabled() || gPlayState == nullptr || !GameInteractor::IsSaveLoaded(true)) {
            return;
        }
        ImGuiIO& io = ImGui::GetIO();
        if (!io.WantTextInput) {
            if (ImGui::IsKeyPressed(ImGuiKey_I, false)) {
                sShowChar = !sShowChar;
            }
            if (ImGui::IsKeyPressed(ImGuiKey_B, false)) {
                sShowBags = !sShowBags;
            }
            if (ImGui::IsKeyPressed(ImGuiKey_L, false)) {
                sShowQuests = !sShowQuests;
            }
            if (ImGui::IsKeyPressed(ImGuiKey_N, false)) {
                sShowTalents = !sShowTalents;
            }
            if (ImGui::IsKeyPressed(ImGuiKey_K, false)) {
                sShowProfs = !sShowProfs;
            }
            if (ImGui::IsKeyPressed(ImGuiKey_Q, false) && !HudBlocked()) {
                QuaffBestHealingPotion();
            }
        }

        GameRect r = GetGameRect();
        ImGui::SetNextWindowPos(r.pos, ImGuiCond_Always);
        ImGui::SetNextWindowSize(r.size, ImGuiCond_Always);
        ImGui::SetNextWindowViewport(ImGui::GetMainViewport()->ID);
        ImGuiWindowFlags f = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoInputs | ImGuiWindowFlags_NoBackground |
                             ImGuiWindowFlags_NoNav | ImGuiWindowFlags_NoFocusOnAppearing |
                             ImGuiWindowFlags_NoBringToFrontOnFocus | ImGuiWindowFlags_NoDocking |
                             ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoMove;
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0, 0));
        ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 0.0f);
        if (ImGui::Begin("##AzerothOverlay", nullptr, f)) {
            ImDrawList* dl = ImGui::GetWindowDrawList();
            dl->PushClipRect(r.pos, ImVec2(r.pos.x + r.size.x, r.pos.y + r.size.y), false);
            bool blocked = HudBlocked();
            if (!blocked) {
                DrawNameplates(dl, r);
                DrawQuestMarkers(dl, r);
                DrawFloats(dl, r);
                DrawTargetFrame(dl, r);
                DrawQuestTracker(dl, r);
                DrawBuffs(dl, r);
            } else {
                sFloats.clear();
            }
            DrawChat(dl, r);
            DrawCenterText(dl, r);
            if (gPlayState->pauseCtx.state == 0) {
                DrawXpBar(dl, r);
            }
            dl->PopClipRect();
        }
        ImGui::End();
        ImGui::PopStyleVar(2);

        if (gPlayState->pauseCtx.state == 0) {
            DrawMicroMenu(r);
        }
        if (sShowChar) {
            DrawCharacterWindow();
        }
        if (sShowBags) {
            DrawBagsWindow();
        }
        if (sShowTalents) {
            DrawTalentWindow();
        }
        if (sShowProfs) {
            DrawProfessionWindow();
        }
        if (sShowQuests) {
            DrawQuestWindow();
        }
    }
};

static std::shared_ptr<HudWindow> sHud;

void RegisterUI() {
    auto ctx = Ship::Context::GetRawInstance();
    if (ctx == nullptr || ctx->GetWindow() == nullptr || ctx->GetWindow()->GetGui() == nullptr) {
        return;
    }
    auto gui = ctx->GetWindow()->GetGui();
    sHud = std::make_shared<HudWindow>(CVAR_WINDOW("AzerothHud"), "Hyrule of Warcraft HUD");
    gui->AddGuiWindow(sHud);
    sHud->Show();
}

// ---------------------------------------------------------------------------------------------------------------
// Settings menu (Esc -> Enhancements -> Warcraft)
// ---------------------------------------------------------------------------------------------------------------
static void RegisterMenu() {
    using namespace UIWidgets;
    WidgetPath path = { "Enhancements", "Warcraft", SECTION_COLUMN_1 };
    SohGui::GetSohMenu()->AddSidebarEntry("Enhancements", path.sidebarName, 2);
    SohGui::GetSohMenu()->AddWidget(path, "Hyrule of Warcraft", WIDGET_SEPARATOR_TEXT);
    SohGui::GetSohMenu()->AddWidget(path, "Enable WoW systems", WIDGET_CVAR_CHECKBOX)
        .CVar(CVAR_AZEROTH("Enabled"))
        .Options(CheckboxOptions().DefaultValue(true).Tooltip(
            "Levels, XP, loot, quests, dungeons/raids and the WoW style interface."));
    static const std::map<int32_t, const char*> diffs = { { 0, "Normal" }, { 1, "Heroic" }, { 2, "Mythic" } };
    SohGui::GetSohMenu()->AddWidget(path, "Dungeon & Raid Difficulty", WIDGET_CVAR_COMBOBOX)
        .CVar(CVAR_AZEROTH("Difficulty"))
        .Options(ComboboxOptions().ComboMap(diffs).DefaultIndex(0).Tooltip(
            "Heroic and Mythic make dungeon and raid enemies hit harder and take less damage, with better loot. "
            "Mythic also disables health regeneration inside dungeons and raids."));
    SohGui::GetSohMenu()->AddWidget(path, "XP Rate: %.2fx", WIDGET_CVAR_SLIDER_FLOAT)
        .CVar(CVAR_AZEROTH("XpRate"))
        .Options(FloatSliderOptions().Min(0.25f).Max(5.0f).DefaultValue(1.0f).Format("%.2fx").Tooltip(
            "Multiplier for all experience gained."));
    SohGui::GetSohMenu()->AddWidget(path, "Out-of-combat health regen", WIDGET_CVAR_CHECKBOX)
        .CVar(CVAR_AZEROTH("Regen"))
        .Options(CheckboxOptions().DefaultValue(true).Tooltip(
            "Slowly regenerate hearts while out of combat, like in WoW. Scales with Spirit."));
    SohGui::GetSohMenu()->AddWidget(path, "Enemy nameplates", WIDGET_CVAR_CHECKBOX)
        .CVar(CVAR_AZEROTH("Nameplates"))
        .Options(CheckboxOptions().DefaultValue(true));
    SohGui::GetSohMenu()->AddWidget(path, "Quest tracker", WIDGET_CVAR_CHECKBOX)
        .CVar(CVAR_AZEROTH("QuestTracker"))
        .Options(CheckboxOptions().DefaultValue(true));
    SohGui::GetSohMenu()->AddWidget(path, "Chat / combat log", WIDGET_CVAR_CHECKBOX)
        .CVar(CVAR_AZEROTH("Chat"))
        .Options(CheckboxOptions().DefaultValue(true));
    SohGui::GetSohMenu()->AddWidget(path, "Hotkeys: I Character, B Bags, L Quests, N Talents, K Professions, Q Potion", WIDGET_TEXT);
}

static RegisterMenuInitFunc menuInitFunc(RegisterMenu);

} // namespace Azeroth
