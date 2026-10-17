-- Zelda HUD: combat stats beside the character sheet - melee and ranged crit, hit bonus, weapon
-- skill, spell crit and hit, dodge, parry and block. The 1.12 interface cannot read crit or hit
-- chance, so while the sheet is open the panel asks the server once a second (".zstats"); the
-- answer comes back as a "ZSTATS:" system line, which is kept out of the chat.

local REFRESH = 1.0

local ROWS = {
	-- { label, value index in the ZSTATS line, format }
	{ "Melee Crit", 1, "%.2f%%" },
	{ "Melee Hit Bonus", 4, "+%.2f%%" },
	{ "Weapon Skill", 9, nil },        -- skill / cap, formatted below
	{ "Ranged Crit", 2, "%.2f%%" },
	{ "Spell Crit", 3, "%.2f%%" },
	{ "Spell Hit Bonus", 5, "+%.2f%%" },
	{ "Dodge", 6, "%.2f%%" },
	{ "Parry", 7, "%.2f%%" },
	{ "Block", 8, "%.2f%%" },
}

local panel = CreateFrame("Frame", "ZeldaStatsPanel", UIParent)
panel:SetWidth(170)
panel:SetHeight(32 + 16 * table.getn(ROWS))
panel:SetFrameStrata("MEDIUM")
panel:SetBackdrop({
	bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 16, edgeSize = 16,
	insets = { left = 4, right = 4, top = 4, bottom = 4 },
})
panel:SetBackdropColor(0, 0, 0, 0.85)
panel:SetBackdropBorderColor(0.6, 0.6, 0.6, 1)
panel:Hide()

local title = panel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
title:SetPoint("TOP", panel, "TOP", 0, -10)
title:SetText("Combat Stats")

local labels, values = {}, {}
for i, row in ipairs(ROWS) do
	local y = -14 - 16 * i
	local label = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
	label:SetPoint("TOPLEFT", panel, "TOPLEFT", 12, y)
	label:SetText(row[1])
	local value = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
	value:SetPoint("TOPRIGHT", panel, "TOPRIGHT", -12, y)
	value:SetText("...")
	labels[i], values[i] = label, value
end

local function Show(stats)
	for i, row in ipairs(ROWS) do
		local v = stats[row[2]]
		if v == nil then
			values[i]:SetText("-")
		elseif row[3] then
			values[i]:SetText(string.format(row[3], v))
		else
			values[i]:SetText(string.format("%d / %d", v, stats[10] or 0))
		end
	end
end

-- "ZSTATS:a;b;c;..." -> { a, b, c, ... }
local function Parse(msg)
	local stats = {}
	local pos = 8
	while true do
		local s, e, v = string.find(msg, "([^;]+)", pos)
		if not s then break end
		table.insert(stats, tonumber(v))
		pos = e + 1
	end
	return stats
end

-- keep the server's answers out of the chat window
local origChatFrameOnEvent = ChatFrame_OnEvent
ChatFrame_OnEvent = function(event)
	if event == "CHAT_MSG_SYSTEM" and arg1 and string.sub(arg1, 1, 7) == "ZSTATS:" then
		return
	end
	origChatFrameOnEvent(event)
end

panel:RegisterEvent("CHAT_MSG_SYSTEM")
panel:SetScript("OnEvent", function()
	if event == "CHAT_MSG_SYSTEM" and arg1 and string.sub(arg1, 1, 7) == "ZSTATS:" then
		Show(Parse(arg1))
	end
end)

local sinceAsk = REFRESH
panel:SetScript("OnUpdate", function()
	sinceAsk = sinceAsk + arg1
	if sinceAsk >= REFRESH then
		sinceAsk = 0
		SendChatMessage(".zstats", "SAY")
	end
end)

-- shown with the character sheet's paper doll, to its right
local watcher = CreateFrame("Frame", "ZeldaStatsWatcher", UIParent)
watcher:SetScript("OnUpdate", function()
	local open = PaperDollFrame and PaperDollFrame:IsVisible()
	if open and not panel:IsVisible() then
		panel:ClearAllPoints()
		panel:SetPoint("TOPLEFT", CharacterFrame, "TOPRIGHT", -32, -14)
		sinceAsk = REFRESH
		panel:Show()
	elseif not open and panel:IsVisible() then
		panel:Hide()
	end
end)
