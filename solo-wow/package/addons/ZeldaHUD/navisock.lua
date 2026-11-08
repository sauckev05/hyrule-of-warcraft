-- Navi's Light's trinket sockets. Navi's menu ("Navi, hold a trinket in your light.") opens a small
-- window like the bank's with two slots that take trinkets only: drop a trinket on a slot, or
-- right-click one in your bags while the window is open. Left-click a held trinket to take it back,
-- right-click it to use its Use: effect. The server keeps them (.znavisock, .znaviuse in
-- ZeldaCommands.cpp) and they work as if equipped while Navi's Light is. Hovering Navi's Light shows
-- each held trinket's own tooltip below hers.

local NAVI_LIGHT = 190601
local EMPTY_ICON = "Interface\\PaperDoll\\UI-PaperDoll-Slot-Trinket"
local PREFIX = "ZNAVISOCK:"

local sockets = { 0, 0 }            -- the trinket entries held, 0 for an empty socket

local function ItemIdFromLink(link)
	if not link then return nil end
	local _, _, id = string.find(link, "item:(%d+)")
	return id and tonumber(id)
end

local function IsTrinket(id)
	if not id then return false end
	local _, _, _, _, _, _, _, equipLoc = GetItemInfo(id)
	return equipLoc == "INVTYPE_TRINKET"
end

local function ItemLink(id)
	return "item:" .. id .. ":0:0:0"
end

-- ------------------------------------------------------------------------------- the window
local frame = CreateFrame("Frame", "ZeldaNaviSocketFrame", UIParent)
frame:SetFrameStrata("HIGH")
frame:SetToplevel(true)
frame:SetMovable(true)
frame:EnableMouse(true)
frame:SetClampedToScreen(true)
frame:SetWidth(176)
frame:SetHeight(112)
frame:SetPoint("CENTER", UIParent, "CENTER", -220, 80)
frame:SetBackdrop({
	bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
	edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
	tile = true, tileSize = 32, edgeSize = 24,
	insets = { left = 6, right = 6, top = 6, bottom = 6 },
})
frame:RegisterForDrag("LeftButton")
frame:SetScript("OnDragStart", function() this:StartMoving() end)
frame:SetScript("OnDragStop", function() this:StopMovingOrSizing() end)
frame:Hide()
tinsert(UISpecialFrames, "ZeldaNaviSocketFrame")

local title = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
title:SetPoint("TOP", frame, "TOP", 0, -12)
title:SetText("Navi's Light")

local hint = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
hint:SetPoint("BOTTOM", frame, "BOTTOM", 0, 12)
hint:SetText("Trinkets only")

local close = CreateFrame("Button", "ZeldaNaviSocketFrameClose", frame, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -2, -2)

-- the trinket picked up from the bags last, so a drop on a socket knows where it came from
local held = nil
local origPickupContainerItem = PickupContainerItem
PickupContainerItem = function(bag, slot)
	if CursorHasItem() then
		held = nil
	else
		held = { bag = bag, slot = slot }
	end
	return origPickupContainerItem(bag, slot)
end

local function PutFromBags(bag, slot, index)
	if not IsTrinket(ItemIdFromLink(GetContainerItemLink(bag, slot))) then
		UIErrorsFrame:AddMessage("Only a trinket fits in Navi's Light.", 1.0, 0.1, 0.1, 1.0)
		return
	end
	SendChatMessage(".znavisock put " .. bag .. " " .. slot .. " " .. (index or 0), "SAY")
end

local slots = {}
local function Refresh()
	for i = 1, 2 do
		local b = slots[i]
		local id = sockets[i]
		local icon = getglobal(b:GetName() .. "IconTexture")
		if id and id ~= 0 then
			local _, _, _, _, _, _, _, _, texture = GetItemInfo(id)
			icon:SetTexture(texture or "Interface\\Icons\\INV_Misc_QuestionMark")
			icon:SetVertexColor(1, 1, 1)
		else
			icon:SetTexture(EMPTY_ICON)
			icon:SetVertexColor(1, 1, 1)
		end
	end
end

local function DropOnSocket(index)
	if not CursorHasItem() then return false end
	if held then
		PutFromBags(held.bag, held.slot, index)
	else
		UIErrorsFrame:AddMessage("Bring the trinket from your bags.", 1.0, 0.1, 0.1, 1.0)
	end
	ClearCursor()
	held = nil
	return true
end

for i = 1, 2 do
	local b = CreateFrame("Button", "ZeldaNaviSocket" .. i, frame, "ItemButtonTemplate")
	b:SetID(i)
	b:SetPoint("TOP", frame, "TOP", (i == 1) and -26 or 26, -38)
	b:RegisterForClicks("LeftButtonUp", "RightButtonUp")
	b:RegisterForDrag("LeftButton")
	b:SetScript("OnReceiveDrag", function()
		DropOnSocket(this:GetID())
	end)
	b:SetScript("OnClick", function()
		local index = this:GetID()
		if DropOnSocket(index) then return end
		if sockets[index] == 0 then return end
		if arg1 == "RightButton" then
			SendChatMessage(".znaviuse " .. index, "SAY")
		else
			SendChatMessage(".znavisock take " .. index, "SAY")
		end
	end)
	b:SetScript("OnEnter", function()
		GameTooltip:SetOwner(this, "ANCHOR_RIGHT")
		local id = sockets[this:GetID()]
		if id and id ~= 0 then
			GameTooltip:SetHyperlink(ItemLink(id))
			GameTooltip:AddLine("Left-click: take it back.  Right-click: use it.", 0.5, 0.8, 1.0)
		else
			GameTooltip:SetText("Empty socket")
			GameTooltip:AddLine("Drop a trinket here, or right-click one in your bags.", 0.5, 0.8, 1.0)
		end
		GameTooltip:Show()
	end)
	b:SetScript("OnLeave", function() GameTooltip:Hide() end)
	slots[i] = b
end

-- the icons of trinkets the client has not cached yet arrive a moment later
local retry = 0
frame:SetScript("OnUpdate", function()
	retry = retry + arg1
	if retry >= 1 then
		retry = 0
		Refresh()
	end
end)
frame:SetScript("OnShow", function()
	Refresh()
	PlaySound("igMainMenuOpen")
	OpenBackpack()
end)
frame:SetScript("OnHide", function() PlaySound("igMainMenuClose") end)

-- right-click a trinket in the bags while the window is open: into the first empty socket, as the
-- bank takes an item
local origUseContainerItem = UseContainerItem
UseContainerItem = function(bag, slot, a, b, c)
	if frame:IsVisible() and IsTrinket(ItemIdFromLink(GetContainerItemLink(bag, slot))) then
		PutFromBags(bag, slot, 0)
		return
	end
	return origUseContainerItem(bag, slot, a, b, c)
end

-- --------------------------------------------------------------------- the server's answers
local function Parse(msg)
	local body = string.sub(msg, string.len(PREFIX) + 1)
	local open = false
	if string.sub(body, 1, 5) == "OPEN;" then
		open = true
		body = string.sub(body, 6)
	end
	local _, _, a, b = string.find(body, "^(%d+);(%d+)")
	sockets[1] = tonumber(a) or 0
	sockets[2] = tonumber(b) or 0
	return open
end

local origChatFrameOnEvent = ChatFrame_OnEvent
ChatFrame_OnEvent = function(event)
	if event == "CHAT_MSG_SYSTEM" and arg1 and string.sub(arg1, 1, string.len(PREFIX)) == PREFIX then
		return
	end
	origChatFrameOnEvent(event)
end

local events = CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_SYSTEM")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:SetScript("OnEvent", function()
	if event == "PLAYER_ENTERING_WORLD" then
		SendChatMessage(".znavisock", "SAY")
	elseif arg1 and string.sub(arg1, 1, string.len(PREFIX)) == PREFIX then
		if Parse(arg1) then frame:Show() end
		if frame:IsVisible() then Refresh() end
	end
end)

-- ------------------------------------------- Navi's Light's tooltip: the held trinkets below it
local tips = {}
for i = 1, 2 do
	local tip = CreateFrame("GameTooltip", "ZeldaNaviSocketTooltip" .. i, UIParent, "GameTooltipTemplate")
	tip:SetFrameStrata("TOOLTIP")
	tips[i] = tip
end

local function HideHeld()
	tips[1]:Hide()
	tips[2]:Hide()
end

local function ShowHeld(link)
	HideHeld()
	if ItemIdFromLink(link) ~= NAVI_LIGHT then return end
	local anchor = GameTooltip
	local shown = 0
	for i = 1, 2 do
		if sockets[i] ~= 0 then
			shown = shown + 1
			local tip = tips[shown]
			tip:SetOwner(GameTooltip, "ANCHOR_NONE")
			tip:ClearAllPoints()
			tip:SetPoint("TOPLEFT", anchor, "BOTTOMLEFT", 0, -2)
			tip:SetHyperlink(ItemLink(sockets[i]))
			tip:Show()
			anchor = tip
		end
	end
end

local origSetBagItem = GameTooltip.SetBagItem
GameTooltip.SetBagItem = function(self, bag, slot)
	local a, b, c = origSetBagItem(self, bag, slot)
	ShowHeld(GetContainerItemLink(bag, slot))
	return a, b, c
end

local origSetInventoryItem = GameTooltip.SetInventoryItem
GameTooltip.SetInventoryItem = function(self, unit, slot)
	local a, b, c = origSetInventoryItem(self, unit, slot)
	if unit == "player" then
		ShowHeld(GetInventoryItemLink("player", slot))
	else
		HideHeld()
	end
	return a, b, c
end

local origOnHide = GameTooltip:GetScript("OnHide")
GameTooltip:SetScript("OnHide", function()
	if origOnHide then origOnHide() end
	HideHeld()
end)
