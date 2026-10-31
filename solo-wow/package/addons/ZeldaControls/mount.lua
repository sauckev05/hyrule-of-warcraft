-- Zelda Controls: the mount slot (key 7), next to the potion slot.
-- Right-click a mount in the bags to put it in the slot (it is not summoned); the mount key (7) or a
-- click on the slot rides it, and pressing it again while mounted gets off. The server does the
-- riding (.zmount), so the slot works from anywhere in the bags.

local MOUNTS = {}
for _, id in ipairs({
	823, 842, 875, 901, 902, 903, 1041, 1042, 1043, 1044, 1122, 1123, 1124, 1132, 1133, 1134,
	2411, 2413, 2414, 2415, 5655, 5656, 5663, 5665, 5668, 5864, 5872, 5873, 5874, 5875, 8563, 8583,
	8586, 8588, 8589, 8590, 8591, 8592, 8595, 8627, 8628, 8629, 8630, 8631, 8632, 8633, 12302, 12303,
	12325, 12326, 12327, 12330, 12351, 12353, 12354, 13086, 13317, 13321, 13322, 13323, 13324, 13325, 13326, 13327,
	13328, 13329, 13331, 13332, 13333, 13334, 13335, 14062, 15277, 15290, 15292, 15293, 16338, 16339, 16343, 16344,
	18063, 18241, 18242, 18243, 18244, 18245, 18246, 18247, 18248, 18766, 18767, 18768, 18772, 18773, 18774, 18776,
	18777, 18778, 18785, 18786, 18787, 18788, 18789, 18790, 18791, 18793, 18794, 18795, 18796, 18797, 18798, 18902,
	19029, 19030, 19872, 19902, 20221, 21044, 21218, 21321, 21323, 21324, 21736, 23193, 23720,
	191161, -- the Reins of the Scarlet Warhorse (Cold Words in the Downs)
}) do
	MOUNTS[id] = true
end
local SIZE = 40

local function ItemId(link)
	local _, _, id = string.find(link or "", "item:(%d+)")
	return id and tonumber(id)
end

local function ItemName(link)
	local _, _, name = string.find(link or "", "%[(.-)%]")
	return name
end

local function Key()
	return (UnitName("player") or "?") .. "-" .. (GetRealmName and GetRealmName() or "")
end

local function Slotted()
	if not ZeldaControlsDB or not ZeldaControlsDB.mount then return nil end
	return ZeldaControlsDB.mount[Key()]
end

local function FindInBags(id)
	for bag = 0, 4 do
		for slot = 1, GetContainerNumSlots(bag) or 0 do
			if ItemId(GetContainerItemLink(bag, slot)) == id then
				return bag, slot
			end
		end
	end
	return nil
end

local button = CreateFrame("Button", "ZeldaMountSlot", UIParent)
button:SetWidth(SIZE)
button:SetHeight(SIZE)
button:SetPoint("LEFT", ZeldaPotionSlot or UIParent, ZeldaPotionSlot and "RIGHT" or "CENTER", 14, 0)
button:SetMovable(1)
button:EnableMouse(1)
button:RegisterForDrag("LeftButton")
button:RegisterForClicks("LeftButtonUp", "RightButtonUp")
button:SetFrameStrata("MEDIUM")

local back = button:CreateTexture(nil, "BACKGROUND")
back:SetTexture("Interface\\Buttons\\UI-EmptySlot-Disabled")
back:SetWidth(SIZE * 1.6)
back:SetHeight(SIZE * 1.6)
back:SetPoint("CENTER", button, "CENTER", 0, 0)

local icon = button:CreateTexture(nil, "ARTWORK")
icon:SetAllPoints(button)

local hotkey = button:CreateFontString(nil, "OVERLAY", "NumberFontNormalSmallGray")
hotkey:SetPoint("TOPLEFT", button, "TOPLEFT", 2, -2)
hotkey:SetText("7")

local label = button:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
label:SetPoint("BOTTOM", button, "TOP", 0, 3)
label:SetText("Mount")

local function Refresh()
	local id = Slotted()
	if not id then
		icon:SetTexture(nil)
		button:SetAlpha(0.6)
		return
	end
	local bag, slot = FindInBags(id)
	local texture
	if bag then
		texture = GetContainerItemInfo(bag, slot)
	else
		local _, _, _, _, _, _, _, _, tex = GetItemInfo(id)
		texture = tex
	end
	icon:SetTexture(texture or "Interface\\Icons\\Ability_Mount_RidingHorse")
	if bag then icon:SetVertexColor(1, 1, 1) else icon:SetVertexColor(0.4, 0.4, 0.4) end
	button:SetAlpha(1)
end

function ZeldaControls_Ride()
	local id = Slotted()
	if not id then
		UIErrorsFrame:AddMessage("No mount in the mount slot - right-click a mount in your bags.", 1, 0.3, 0.3)
		return
	end
	SendChatMessage(".zmount " .. id, "SAY")
end

button:SetScript("OnClick", function() ZeldaControls_Ride() end)
button:SetScript("OnDragStart", function()
	if IsShiftKeyDown() then this:StartMoving() end
end)
button:SetScript("OnDragStop", function()
	this:StopMovingOrSizing()
	if ZeldaControlsDB then
		local _, _, _, x, y = this:GetPoint()
		ZeldaControlsDB.mountPos = { x, y }
	end
end)
button:SetScript("OnEnter", function()
	GameTooltip:SetOwner(this, "ANCHOR_TOP")
	local id = Slotted()
	local bag, slot = nil, nil
	if id then bag, slot = FindInBags(id) end
	if bag then
		GameTooltip:SetBagItem(bag, slot)
	else
		GameTooltip:SetText("Mount slot", 1, 1, 1)
	end
	GameTooltip:AddLine("Press 7 or click to ride; again to get off. Right-click a mount in your bags to put it here. Shift-drag to move.", 0.6, 0.8, 1, 1)
	GameTooltip:Show()
end)
button:SetScript("OnLeave", function() GameTooltip:Hide() end)

local function ShopOpen()
	for _, name in ipairs({ "MerchantFrame", "BankFrame", "TradeFrame", "MailFrame", "AuctionFrame", "SendMailFrame" }) do
		local f = getglobal(name)
		if f and f:IsVisible() then
			return true
		end
	end
	return false
end

local nextUseContainerItem = UseContainerItem
UseContainerItem = function(bag, slot, onSelf)
	if not ShopOpen() then
		local link = GetContainerItemLink(bag, slot)
		local id = ItemId(link)
		if id and MOUNTS[id] then
			ZeldaControlsDB = ZeldaControlsDB or {}
			ZeldaControlsDB.mount = ZeldaControlsDB.mount or {}
			ZeldaControlsDB.mount[Key()] = id
			UIErrorsFrame:AddMessage("Mount slot: " .. (ItemName(link) or "mount") .. " (press 7 to ride)", 0.4, 1, 0.4)
			Refresh()
			return
		end
	end
	nextUseContainerItem(bag, slot, onSelf)
end

local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("BAG_UPDATE")
events:RegisterEvent("VARIABLES_LOADED")
events:SetScript("OnEvent", function()
	if event == "VARIABLES_LOADED" and ZeldaControlsDB and ZeldaControlsDB.mountPos then
		local p = ZeldaControlsDB.mountPos
		button:ClearAllPoints()
		button:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", p[1], p[2])
	end
	Refresh()
end)
