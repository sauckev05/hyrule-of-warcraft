-- Zelda HUD: the target's health as a Zelda boss bar, just above the reputation and experience
-- bars at the bottom of the screen. The old target frame (portrait, level circle, name plate) is
-- hidden for good.
--
--      ═══════════ (the target's charge-up, castbar.lua) ═══════════
--               Theradrim Shardling  [46]
--   ╔══════════════════════════════════════════════════╗
--   ║█████████████████████████████░░░░░░░░░░░░░   62% ║   red, yellow or green by how it feels
--   ╚══════════════════════════════════════════════════╝   about you; gold edge for elites, rares
--   ── reputation bar ──                                    and bosses
--   ── experience bar ──

local WIDTH_SHARE = 0.6        -- of the experience bar's width
local HEIGHT = 14              -- the bar itself, as slim as the experience bar
local SEGMENTS = 20

-- the anchor stays put whether or not there is a target, so the charge-up bar has a place too
local anchor = CreateFrame("Frame", "ZeldaTargetAnchor", UIParent)
anchor:SetWidth(600)
anchor:SetHeight(HEIGHT)
anchor:SetFrameStrata("LOW")

local bar = CreateFrame("StatusBar", "ZeldaTargetBar", anchor)
bar:SetAllPoints(anchor)
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetMinMaxValues(0, 100)
bar:SetValue(100)
bar:Hide()

local bg = bar:CreateTexture(nil, "BACKGROUND")
bg:SetAllPoints(bar)
bg:SetTexture(0, 0, 0, 0.75)

-- the segment marks, as on the experience bar
local ticks = {}
for i = 1, SEGMENTS - 1 do
	local t = bar:CreateTexture(nil, "OVERLAY")
	t:SetTexture(0.85, 0.85, 0.9, 0.45)
	t:SetWidth(1)
	ticks[i] = t
end

local border = CreateFrame("Frame", nil, bar)
border:SetPoint("TOPLEFT", bar, "TOPLEFT", -3, 3)
border:SetPoint("BOTTOMRIGHT", bar, "BOTTOMRIGHT", 3, -3)
border:SetBackdrop({
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 8, edgeSize = 8,
	insets = { left = 2, right = 2, top = 2, bottom = 2 },
})

local pct = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
pct:SetPoint("RIGHT", bar, "RIGHT", -6, 0)

-- the title above the bar: the name, and the level in a little gold gem
local title = CreateFrame("Frame", nil, bar)
title:SetWidth(10)
title:SetHeight(18)
title:SetPoint("BOTTOM", bar, "TOP", 0, 3)
local name = title:CreateFontString(nil, "OVERLAY", "GameFontNormal")
name:SetTextColor(1, 1, 1)
name:SetPoint("LEFT", title, "LEFT", 0, 0)

local gem = CreateFrame("Frame", nil, title)
gem:SetWidth(24)
gem:SetHeight(16)
gem:SetPoint("LEFT", name, "RIGHT", 6, 0)
gem:SetBackdrop({
	bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 8, edgeSize = 8,
	insets = { left = 2, right = 2, top = 2, bottom = 2 },
})
gem:SetBackdropColor(0.35, 0.22, 0.02, 0.95)
gem:SetBackdropBorderColor(1.0, 0.82, 0.25, 1)
local level = gem:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
level:SetPoint("CENTER", gem, "CENTER", 0, 0)
level:SetTextColor(1.0, 0.86, 0.35)

local function Layout()
	local under = MainMenuExpBar
	if ReputationWatchBar and ReputationWatchBar:IsVisible() then
		under = ReputationWatchBar
	end
	local width = (MainMenuExpBar and MainMenuExpBar:GetWidth() or 1000) * WIDTH_SHARE
	anchor:SetWidth(width)
	anchor:ClearAllPoints()
	if under then
		anchor:SetPoint("BOTTOM", under, "TOP", 0, 30)
	else
		anchor:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 60)
	end
	for i = 1, SEGMENTS - 1 do
		local t = ticks[i]
		t:ClearAllPoints()
		t:SetPoint("TOP", bar, "TOPLEFT", width * i / SEGMENTS, 0)
		t:SetPoint("BOTTOM", bar, "BOTTOMLEFT", width * i / SEGMENTS, 0)
	end
end

-- red against you, yellow for the indifferent, green for friends
local function Colour()
	local r = UnitReaction("target", "player")
	if UnitIsPlayer("target") and UnitIsFriend("player", "target") then
		return 0.2, 0.8, 0.25
	end
	if not r or r <= 3 then
		return 0.85, 0.12, 0.12
	elseif r == 4 then
		return 0.9, 0.75, 0.1
	end
	return 0.2, 0.8, 0.25
end

local function Update()
	if not UnitExists("target") then
		bar:Hide()
		return
	end
	local hp, max = UnitHealth("target"), UnitHealthMax("target")
	if not max or max <= 0 then max = 100 end
	bar:SetMinMaxValues(0, max)
	bar:SetValue(hp or 0)
	bar:SetStatusBarColor(Colour())
	if UnitIsDead("target") then
		pct:SetText("Dead")
	else
		pct:SetText(math.floor((hp or 0) / max * 100 + 0.5) .. "%")
	end

	name:SetText(UnitName("target") or "")
	title:SetWidth(name:GetStringWidth() + 6 + gem:GetWidth())
	local lvl = UnitLevel("target")
	local kind = UnitClassification and UnitClassification("target") or "normal"
	if not lvl or lvl <= 0 or kind == "worldboss" then
		level:SetText("??")
	else
		level:SetText(lvl)
	end
	if kind == "elite" or kind == "rareelite" or kind == "rare" or kind == "worldboss" then
		border:SetBackdropBorderColor(1.0, 0.82, 0.25, 1)     -- gold for the strong ones
	else
		border:SetBackdropBorderColor(0.75, 0.75, 0.8, 1)
	end
	bar:Show()
end

-- the old target frame goes away for good
local function HideOldTargetFrame()
	for _, f in ipairs({ TargetFrame, TargetofTargetFrame, ComboFrame }) do
		if f then
			f:Hide()
			f:SetScript("OnShow", function() this:Hide() end)
		end
	end
end

local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("PLAYER_TARGET_CHANGED")
events:RegisterEvent("UNIT_HEALTH")
events:RegisterEvent("UNIT_MAXHEALTH")
events:RegisterEvent("UNIT_LEVEL")
events:RegisterEvent("UNIT_FACTION")
events:RegisterEvent("UPDATE_FACTION")
events:SetScript("OnEvent", function()
	if event == "PLAYER_ENTERING_WORLD" then
		HideOldTargetFrame()
		Layout()
		Update()
	elseif event == "PLAYER_TARGET_CHANGED" or event == "UPDATE_FACTION" or arg1 == "target" then
		Update()
	end
end)

-- the bars below can move (the reputation bar comes and goes); follow them, and catch any health
-- change an event missed
local since = 0
events:SetScript("OnUpdate", function()
	since = since + (arg1 or 0)
	if since >= 0.25 then
		since = 0
		Layout()
		Update()
	end
end)
