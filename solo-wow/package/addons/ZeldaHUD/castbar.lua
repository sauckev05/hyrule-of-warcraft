-- Zelda HUD: enemy charge-ups.
--
-- Every enemy ability aimed at you charges up first (the server makes it take at least a moment),
-- long enough to raise the shield. While one charges, a bar under the target's portrait shows who
-- is charging what and how long is left. The server sends the hidden line
-- "ZCAST:caster;ability;milliseconds" when a charge-up starts, and "ZCAST:caster;;0" when one is
-- cut short.

local bar = CreateFrame("StatusBar", "ZeldaEnemyCastBar", UIParent)
bar:SetWidth(190)
bar:SetHeight(14)
bar:SetFrameStrata("MEDIUM")
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetStatusBarColor(1.0, 0.45, 0.0)
bar:SetMinMaxValues(0, 1)
bar:SetValue(0)
bar:Hide()

local bg = bar:CreateTexture(nil, "BACKGROUND")
bg:SetTexture(0, 0, 0, 0.65)
bg:SetAllPoints(bar)

local border = CreateFrame("Frame", nil, bar)
border:SetPoint("TOPLEFT", bar, "TOPLEFT", -4, 4)
border:SetPoint("BOTTOMRIGHT", bar, "BOTTOMRIGHT", 4, -4)
border:SetBackdrop({
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 12, edgeSize = 12,
	insets = { left = 3, right = 3, top = 3, bottom = 3 },
})
border:SetBackdropBorderColor(1.0, 0.6, 0.2, 1)

local label = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
label:SetPoint("BOTTOM", bar, "TOP", 0, 4)
local timeText = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
timeText:SetPoint("CENTER", bar, "CENTER", 0, 0)

local caster, startAt, endAt

local function Place()
	bar:ClearAllPoints()
	if TargetFrame then
		bar:SetPoint("TOP", TargetFrame, "BOTTOM", -20, -18)
	else
		bar:SetPoint("TOP", UIParent, "TOP", 0, -140)
	end
end

local function Stop()
	caster, startAt, endAt = nil, nil, nil
	bar:Hide()
end

local function Start(who, ability, ms)
	Place()
	caster = who
	startAt = GetTime()
	endAt = startAt + ms / 1000
	bar:SetMinMaxValues(0, ms / 1000)
	bar:SetValue(0)
	if who == UnitName("target") then
		label:SetText("|cffff9933" .. (ability ~= "" and ability or "Attack") .. "|r  - shield up!")
	else
		label:SetText(who .. ":  |cffff9933" .. (ability ~= "" and ability or "Attack") .. "|r  - shield up!")
	end
	bar:Show()
end

bar:SetScript("OnUpdate", function()
	if not endAt then
		this:Hide()
		return
	end
	local now = GetTime()
	if now >= endAt then
		Stop()
		return
	end
	this:SetValue(now - startAt)
	timeText:SetText(string.format("%.1f", endAt - now))
end)

local events = CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_SYSTEM")
events:RegisterEvent("PLAYER_DEAD")
events:SetScript("OnEvent", function()
	if event == "PLAYER_DEAD" then
		Stop()
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
		if who == caster then
			Stop()
		end
	else
		Start(who, ability, ms)
	end
end)
