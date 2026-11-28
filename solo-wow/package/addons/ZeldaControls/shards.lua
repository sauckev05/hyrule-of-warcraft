-- Zelda Controls: the Crystal Shards screen, a page of the Subscreen (9) before Main Menu.
--
-- Like Ocarina of Time's Quest Status: every dungeon's shard round a stone ring, the raids' a hexagon
-- round Naxxramas. A shard the hero has earned shines in its slot; one still to win is its empty
-- socket. An earned raid shard lights its line on to the next raid (the hexagon's rainbow) and its
-- line in to Naxxramas (in its own colour). The art and its layout (shardsdata.lua) come from
-- shard_screen.py; which shards are earned, from the server (".zshards" -> "ZSHARDS:item,item,...").

local DATA = ZeldaShardScreen
local K = 600 / DATA.width                      -- the 840 x 860 picture shown 600 wide

local owned = {}

local frame = CreateFrame("Frame", "ZeldaShardFrame", UIParent)
frame:SetWidth(DATA.width * K)
frame:SetHeight(DATA.height * K)
frame:SetPoint("TOP", UIParent, "TOP", 0, -56)
frame:SetFrameStrata("HIGH")
frame:EnableMouse(true)
frame:Hide()
tinsert(UISpecialFrames, "ZeldaShardFrame")     -- Escape closes it

local bg = frame:CreateTexture(nil, "BACKGROUND")
bg:SetTexture("Interface\\Zelda\\Shards\\Background")
bg:SetTexCoord(0, DATA.width / DATA.texture, 0, DATA.height / DATA.texture)
bg:SetAllPoints(frame)

-- a square overlay at its place in the picture
local function Overlay(layer, tex, left, top, size)
	local t = frame:CreateTexture(nil, layer)
	t:SetTexture(tex)
	t:SetWidth(size * K)
	t:SetHeight(size * K)
	t:SetPoint("TOPLEFT", frame, "TOPLEFT", left * K, -top * K)
	t:Hide()
	return t
end

local lines = {}
for i = 1, table.getn(DATA.lines) do
	local l = DATA.lines[i]
	lines[i] = { item = l.item, tex = Overlay("BORDER", l.tex, l.left, l.top, l.size) }
end

local slots = {}
for i = 1, table.getn(DATA.slots) do
	local s = DATA.slots[i]
	local crystal = Overlay("ARTWORK", s.tex, s.left, s.top, s.size)
	-- the slot answers the mouse: its name, and whether it is won
	local b = CreateFrame("Button", nil, frame)
	b:SetWidth(s.r * 1.4 * K)
	b:SetHeight(s.r * 2 * K)
	b:SetPoint("CENTER", frame, "TOPLEFT", s.x * K, -s.y * K)
	b.slot = s
	b:SetScript("OnEnter", function()
		local slot = this.slot
		GameTooltip:SetOwner(this, "ANCHOR_RIGHT")
		if slot.raid then
			GameTooltip:SetText(slot.name, 0.64, 0.21, 0.93)
		else
			GameTooltip:SetText(slot.name, 0.0, 0.44, 0.87)
		end
		if owned[slot.item] then
			GameTooltip:AddLine("Crystal Shard earned", 0.2, 1.0, 0.6)
		else
			GameTooltip:AddLine("Defeat every foe inside to earn its shard", 0.6, 0.6, 0.6)
		end
		GameTooltip:Show()
	end)
	b:SetScript("OnLeave", function() GameTooltip:Hide() end)
	slots[i] = { item = s.item, crystal = crystal }
end

local count = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
count:SetPoint("BOTTOM", frame, "BOTTOM", 0, 14 * K + 4)

local function Refresh()
	local n = 0
	for i = 1, table.getn(slots) do
		if owned[slots[i].item] then
			slots[i].crystal:Show()
			n = n + 1
		else
			slots[i].crystal:Hide()
		end
	end
	for i = 1, table.getn(lines) do
		if owned[lines[i].item] then lines[i].tex:Show() else lines[i].tex:Hide() end
	end
	count:SetText(n .. " / " .. table.getn(slots))
end

frame:SetScript("OnShow", function()
	Refresh()
	SendChatMessage(".zshards", "SAY")
end)

local events = CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_SYSTEM")
events:SetScript("OnEvent", function()
	if arg1 and string.sub(arg1, 1, 8) == "ZSHARDS:" then
		owned = {}
		for id in string.gfind(string.sub(arg1, 9), "(%d+)") do
			owned[tonumber(id)] = true
		end
		Refresh()
	end
end)

-- keep the server's answer out of the chat window
local origChatFrameOnEvent = ChatFrame_OnEvent
ChatFrame_OnEvent = function(event)
	if event == "CHAT_MSG_SYSTEM" and arg1 and string.sub(arg1, 1, 8) == "ZSHARDS:" then
		return
	end
	origChatFrameOnEvent(event)
end
