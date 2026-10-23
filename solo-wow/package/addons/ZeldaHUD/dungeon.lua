-- Zelda HUD: dungeon clears and the dungeon map.
--
-- Under the minimap, a bar fills as the enemies of the dungeon or raid you are in fall; clearing
-- every one of them gives that dungeon's Crystal Shard. The server sends the count as a hidden
-- "ZDUNGEON:killed;total;name;raid" system line whenever it changes. Click the bar to list the
-- enemies still standing.
--
-- Inside a dungeon or raid, the world map key (M) opens a big map of the floor you are on
-- instead of the world map: the Zelda of Warcraft client draws a second, square minimap zoomed
-- far out (ZeldaDungeonMap). The mouse wheel zooms it; M or Escape closes it.

local clear = { killed = 0, total = 0, name = nil, raid = false }

local function InDungeon()
	local inside, kind = IsInInstance()
	return inside and (kind == "party" or kind == "raid")
end

-- ------------------------------------------------------------------ the clear bar
local bar = CreateFrame("StatusBar", "ZeldaClearBar", UIParent)
bar:SetWidth(132)
bar:SetHeight(14)
bar:SetFrameStrata("LOW")
bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
bar:SetMinMaxValues(0, 1)
bar:SetValue(0)
bar:EnableMouse(1)
bar:Hide()

local barBg = bar:CreateTexture(nil, "BACKGROUND")
barBg:SetTexture(0, 0, 0, 0.6)
barBg:SetAllPoints(bar)

local barBorder = CreateFrame("Frame", nil, bar)
barBorder:SetPoint("TOPLEFT", bar, "TOPLEFT", -4, 4)
barBorder:SetPoint("BOTTOMRIGHT", bar, "BOTTOMRIGHT", 4, -4)
barBorder:SetBackdrop({
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 12, edgeSize = 12,
	insets = { left = 3, right = 3, top = 3, bottom = 3 },
})
barBorder:SetBackdropBorderColor(0.7, 0.7, 0.7, 1)

local barText = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
barText:SetPoint("CENTER", bar, "CENTER", 0, 1)

local function PlaceBar()
	bar:ClearAllPoints()
	bar:SetPoint("TOP", Minimap, "BOTTOM", 0, -10)
end
PlaceBar()

local function Percent()
	if clear.total <= 0 then
		return 0
	end
	return math.floor(clear.killed * 100 / clear.total)
end

local function Colour()
	if clear.total > 0 and clear.killed >= clear.total then
		return 1.0, 0.82, 0.0              -- cleared: gold
	elseif clear.raid then
		return 0.64, 0.21, 0.93            -- raid: epic purple
	end
	return 0.0, 0.44, 0.87                 -- dungeon: rare blue
end

local mapTitle, mapProgress     -- set below with the map frame

local function ShowClear()
	if not clear.name or clear.total <= 0 then
		bar:Hide()
	else
		bar:SetMinMaxValues(0, clear.total)
		bar:SetValue(clear.killed)
		bar:SetStatusBarColor(Colour())
		barText:SetText(Percent() .. "%")
		if not ZeldaDungeonMapFrame or not ZeldaDungeonMapFrame:IsVisible() then
			bar:Show()
		end
	end
	if mapTitle then
		mapTitle:SetText(clear.name or GetRealZoneText() or "")
		if clear.name and clear.total > 0 then
			local r, g, b = Colour()
			mapProgress:SetTextColor(r, g, b)
			mapProgress:SetText(string.format("%d / %d enemies defeated  (%d%%)", clear.killed, clear.total, Percent()))
		else
			mapProgress:SetText("")
		end
	end
end

bar:SetScript("OnEnter", function()
	GameTooltip:SetOwner(this, "ANCHOR_BOTTOMLEFT")
	GameTooltip:SetText(clear.name or "Dungeon", 1, 1, 1)
	GameTooltip:AddLine(string.format("%d of %d enemies defeated (%d%%)", clear.killed, clear.total, Percent()), 1, 0.82, 0)
	GameTooltip:AddLine("Defeat every enemy to earn its Crystal Shard.", 0.8, 0.8, 0.8, 1)
	GameTooltip:AddLine("Click to list the enemies still standing.", 0.5, 0.8, 1, 1)
	GameTooltip:Show()
end)
bar:SetScript("OnLeave", function()
	GameTooltip:Hide()
end)
bar:SetScript("OnMouseUp", function()
	SendChatMessage(".zdungeon left", "SAY")
end)

-- "ZDUNGEON:killed;total;name;raid", or "ZDUNGEON:" outside a dungeon
local function ParseClear(msg)
	local body = string.sub(msg, 10)
	local _, _, killed, total, name, raid = string.find(body, "^(%d+);(%d+);(.-);(%d)$")
	if killed then
		clear.killed, clear.total, clear.name, clear.raid = tonumber(killed), tonumber(total), name, raid == "1"
	else
		clear.killed, clear.total, clear.name, clear.raid = 0, 0, nil, false
	end
	ShowClear()
end

-- keep the server's count out of the chat window
local origChatFrameOnEvent = ChatFrame_OnEvent
ChatFrame_OnEvent = function(event)
	if event == "CHAT_MSG_SYSTEM" and arg1 and string.sub(arg1, 1, 9) == "ZDUNGEON:" then
		return
	end
	origChatFrameOnEvent(event)
end

-- ------------------------------------------------------------------ the dungeon map
local ZOOMS = 4
local zoom = 1

local map = CreateFrame("Frame", "ZeldaDungeonMapFrame", UIParent)
map:SetWidth(700)
map:SetHeight(740)
map:SetPoint("CENTER", UIParent, "CENTER", 0, 10)
map:SetFrameStrata("HIGH")
map:SetToplevel(1)
map:EnableMouse(1)
map:EnableMouseWheel(1)
map:SetBackdrop({
	bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
	edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
	tile = true, tileSize = 32, edgeSize = 32,
	insets = { left = 11, right = 12, top = 12, bottom = 11 },
})
map:Hide()
tinsert(UISpecialFrames, "ZeldaDungeonMapFrame")

mapTitle = map:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
mapTitle:SetPoint("TOP", map, "TOP", 0, -20)

mapProgress = map:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
mapProgress:SetPoint("TOP", mapTitle, "BOTTOM", 0, -6)

local hint = map:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
hint:SetPoint("BOTTOM", map, "BOTTOM", 0, 18)
hint:SetText("Mouse wheel: zoom    M or Escape: close")

local close = CreateFrame("Button", nil, map, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", map, "TOPRIGHT", -6, -6)

local view = CreateFrame("Minimap", "ZeldaDungeonMapView", map)
view:SetWidth(640)
view:SetHeight(640)
view:SetPoint("CENTER", map, "CENTER", 0, -12)

local viewBorder = CreateFrame("Frame", nil, map)
viewBorder:SetPoint("TOPLEFT", view, "TOPLEFT", -5, 5)
viewBorder:SetPoint("BOTTOMRIGHT", view, "BOTTOMRIGHT", 5, -5)
viewBorder:SetBackdrop({
	edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
	tile = true, tileSize = 16, edgeSize = 16,
	insets = { left = 4, right = 4, top = 4, bottom = 4 },
})
viewBorder:SetBackdropBorderColor(0.6, 0.6, 0.6, 1)

map:SetScript("OnShow", function()
	if MinimapCluster then
		MinimapCluster:Hide()
	end
	bar:Hide()
	ZeldaDungeonMap(1, zoom)
	ShowClear()
	SendChatMessage(".zdungeon", "SAY")
end)
map:SetScript("OnHide", function()
	ZeldaDungeonMap(0, zoom)
	if MinimapCluster then
		MinimapCluster:Show()
	end
	ShowClear()
end)
map:SetScript("OnMouseWheel", function()
	if arg1 > 0 then
		zoom = math.min(ZOOMS - 1, zoom + 1)
	else
		zoom = math.max(0, zoom - 1)
	end
	ZeldaDungeonMap(1, zoom)
end)

-- M opens the dungeon map inside a dungeon or raid, the world map everywhere else
local origToggleWorldMap = ToggleWorldMap
ToggleWorldMap = function()
	if map:IsVisible() then
		map:Hide()
	elseif InDungeon() then
		if WorldMapFrame and WorldMapFrame:IsVisible() then
			HideUIPanel(WorldMapFrame)
		end
		map:Show()
	else
		origToggleWorldMap()
	end
end

-- ------------------------------------------------------------------ events
local events = CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_SYSTEM")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("ZONE_CHANGED_NEW_AREA")
events:SetScript("OnEvent", function()
	if event == "CHAT_MSG_SYSTEM" then
		if arg1 and string.sub(arg1, 1, 9) == "ZDUNGEON:" then
			ParseClear(arg1)
		end
	else
		if map:IsVisible() and not InDungeon() then
			map:Hide()
		end
		PlaceBar()
		SendChatMessage(".zdungeon", "SAY")
	end
end)
