-- Zelda HUD: enemy charge-ups.
--
-- Every enemy ability aimed at you charges up first (the server makes it take at least a moment),
-- long enough to raise the shield. While one charges, a thin light-blue line above the target's
-- health bar (targetbar.lua) shows what is charging and how long is left. The server sends the hidden line
-- "ZCAST:caster;ability;milliseconds" when a charge-up starts, and "ZCAST:caster;;0" when one is
-- cut short.

local bar = CreateFrame("StatusBar", "ZeldaEnemyCastBar", UIParent)
bar:SetWidth(360)
bar:SetHeight(10)
bar:SetFrameStrata("MEDIUM")
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetStatusBarColor(0.55, 0.88, 1.0)
bar:SetMinMaxValues(0, 1)
bar:SetValue(0)
bar:Hide()

local bg = bar:CreateTexture(nil, "BACKGROUND")
bg:SetTexture(0, 0, 0, 0.65)
bg:SetAllPoints(bar)

local border = CreateFrame("Frame", nil, bar)
border:SetPoint("TOPLEFT", bar, "TOPLEFT", -3, 3)
border:SetPoint("BOTTOMRIGHT", bar, "BOTTOMRIGHT", 3, -3)
border:SetBackdrop({
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 8, edgeSize = 8,
	insets = { left = 2, right = 2, top = 2, bottom = 2 },
})
border:SetBackdropBorderColor(0.66, 0.94, 1.0, 1)

local label = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
label:SetPoint("CENTER", bar, "CENTER", 0, 0)
local timeText = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
timeText:SetPoint("LEFT", bar, "RIGHT", 6, 0)

-- Every charge-up under way, so several enemies charging at once are all kept: the bar shows the
-- most urgent. A Heavy Blow or a Charged Bolt (the ones to block) always comes first, the one
-- landing soonest; then the target's own charge-up; then the one landing soonest.
local HEAVY = { ["Heavy Blow"] = true, ["Charged Bolt"] = true }
local charges = {}             -- { who, ability, startAt, endAt, heavy }

-- above the target bar's title (targetbar.lua), 60% of its width
local function Place()
	bar:ClearAllPoints()
	if ZeldaTargetAnchor then
		bar:SetWidth(ZeldaTargetAnchor:GetWidth() * 0.6)
		bar:SetPoint("BOTTOM", ZeldaTargetAnchor, "TOP", 0, 28)
	else
		bar:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 110)
	end
end

local function Pick(now)
	local best
	for i = table.getn(charges), 1, -1 do
		if charges[i].endAt <= now then
			table.remove(charges, i)
		end
	end
	local target = UnitName("target")
	for _, c in ipairs(charges) do
		if not best then
			best = c
		elseif c.heavy ~= best.heavy then
			if c.heavy then best = c end
		elseif (c.who == target) ~= (best.who == target) then
			if c.who == target then best = c end
		elseif c.endAt < best.endAt then
			best = c
		end
	end
	return best
end

local shown
local function Show(c)
	if shown == c then
		return
	end
	shown = c
	Place()
	bar:SetMinMaxValues(0, c.endAt - c.startAt)
	local ability = c.ability ~= "" and c.ability or "Attack"
	local text = c.heavy and (ability .. "  - BLOCK!") or (ability .. "  - shield up!")
	if c.who ~= UnitName("target") then
		text = c.who .. ":  " .. text
	end
	label:SetText(text)
	if c.heavy then
		bar:SetStatusBarColor(1.0, 0.45, 0.1)          -- the heavy ones burn orange
		border:SetBackdropBorderColor(1.0, 0.6, 0.2, 1)
	else
		bar:SetStatusBarColor(0.55, 0.88, 1.0)
		border:SetBackdropBorderColor(0.66, 0.94, 1.0, 1)
	end
	bar:Show()
end

local function Refresh()
	local c = Pick(GetTime())
	if not c then
		shown = nil
		bar:Hide()
		return
	end
	Show(c)
end

local function Start(who, ability, ms)
	-- a caster starting again replaces its own earlier charge-up
	for i = table.getn(charges), 1, -1 do
		if charges[i].who == who then
			table.remove(charges, i)
		end
	end
	local now = GetTime()
	table.insert(charges, { who = who, ability = ability, startAt = now, endAt = now + ms / 1000, heavy = HEAVY[ability] or false })
	Refresh()
end

local function Stop(who)
	for i = table.getn(charges), 1, -1 do
		if not who or charges[i].who == who then
			table.remove(charges, i)
		end
	end
	Refresh()
end

local watcher = CreateFrame("Frame")
watcher:SetScript("OnUpdate", function()
	if table.getn(charges) == 0 then
		return
	end
	Refresh()
	if shown then
		local now = GetTime()
		bar:SetValue(now - shown.startAt)
		timeText:SetText(string.format("%.1f", math.max(0, shown.endAt - now)))
	end
end)

local events = CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_SYSTEM")
events:RegisterEvent("PLAYER_DEAD")
events:RegisterEvent("PLAYER_TARGET_CHANGED")
events:SetScript("OnEvent", function()
	if event == "PLAYER_DEAD" then
		Stop()
		return
	end
	if event == "PLAYER_TARGET_CHANGED" then
		shown = nil              -- the label names the caster unless it is the target
		Refresh()
		return
	end
	if not arg1 or string.sub(arg1, 1, 6) ~= "ZCAST:" then
		return
	end
	local _, _, who, ability, ms = string.find(arg1, "^ZCAST:(.-);(.-);(%d+)$")
	if not who then
		return
	end
	ms = tonumber(ms)
	if ms == 0 then
		Stop(who)
	else
		Start(who, ability, ms)
	end
end)
