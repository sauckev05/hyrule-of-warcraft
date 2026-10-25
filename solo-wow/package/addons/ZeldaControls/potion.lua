-- Zelda Controls: the potion slot, like Ocarina of Time's bottle on a C button.
-- Right-click a healing or mana potion in the bags to put it in the slot (it is not drunk); the
-- potion key (6) or a click on the slot drinks one. The slot shows how many are left and remembers
-- its potion per character. At a vendor, bank, mailbox, auction house or trade, right-click works
-- as usual.

local KINDS = { "Healing Potion", "Mana Potion", "Healing Draught", "Mana Draught" }
local SIZE = 40

local function ItemId(link)
	local _, _, id = string.find(link or "", "item:(%d+)")
	return id and tonumber(id)
end

local function ItemName(link)
	local _, _, name = string.find(link or "", "%[(.-)%]")
	return name
end

local function IsPotionName(name)
	if not name then return false end
	for _, kind in ipairs(KINDS) do
		if string.find(name, kind, 1, true) then
			return true
		end
	end
	return false
end

local function Key()
	return (UnitName("player") or "?") .. "-" .. (GetRealmName and GetRealmName() or "")
end

local function Slotted()
	if not ZeldaControlsDB or not ZeldaControlsDB.potion then return nil end
	return ZeldaControlsDB.potion[Key()]
end

-- the first bag slot holding item `id`, and how many the bags hold
local function FindInBags(id)
	local firstBag, firstSlot, total = nil, nil, 0
	for bag = 0, 4 do
		for slot = 1, GetContainerNumSlots(bag) or 0 do
			if ItemId(GetContainerItemLink(bag, slot)) == id then
				local _, count = GetContainerItemInfo(bag, slot)
				total = total + (count or 1)
				if not firstBag then firstBag, firstSlot = bag, slot end
			end
		end
	end
	return firstBag, firstSlot, total
end

-- ------------------------------------------------------------------ the slot button
local button = CreateFrame("Button", "ZeldaPotionSlot", UIParent)
button:SetWidth(SIZE)
button:SetHeight(SIZE)
button:SetPoint("BOTTOM", UIParent, "BOTTOM", 290, 100)
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

local count = button:CreateFontString(nil, "OVERLAY", "NumberFontNormal")
count:SetPoint("BOTTOMRIGHT", button, "BOTTOMRIGHT", -2, 2)

local hotkey = button:CreateFontString(nil, "OVERLAY", "NumberFontNormalSmallGray")
hotkey:SetPoint("TOPLEFT", button, "TOPLEFT", 2, -2)
hotkey:SetText("6")

local label = button:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
label:SetPoint("BOTTOM", button, "TOP", 0, 3)
label:SetText("Potion")

local function Refresh()
	local id = Slotted()
	if not id then
		icon:SetTexture(nil)
		count:SetText("")
		button:SetAlpha(0.6)
		return
	end
	local bag, slot, total = FindInBags(id)
	local texture
	if bag then
		texture = GetContainerItemInfo(bag, slot)
	else
		local _, _, _, _, _, _, _, _, tex = GetItemInfo(id)
		texture = tex
	end
	icon:SetTexture(texture or "Interface\\Icons\\INV_Potion_51")
	if total > 0 then
		icon:SetVertexColor(1, 1, 1)
		count:SetText(total)
	else
		icon:SetVertexColor(0.4, 0.4, 0.4)
		count:SetText("0")
	end
	button:SetAlpha(1)
end

local origUseContainerItem = UseContainerItem

function ZeldaControls_DrinkPotion()
	local id = Slotted()
	if not id then
		UIErrorsFrame:AddMessage("No potion in the potion slot - right-click a healing or mana potion in your bags.", 1, 0.3, 0.3)
		return
	end
	local bag, slot = FindInBags(id)
	if not bag then
		local name = GetItemInfo(id)
		UIErrorsFrame:AddMessage("No " .. (name or "potion") .. " left.", 1, 0.3, 0.3)
		return
	end
	origUseContainerItem(bag, slot)
end

button:SetScript("OnClick", function()
	ZeldaControls_DrinkPotion()
end)
button:SetScript("OnDragStart", function()
	if IsShiftKeyDown() then this:StartMoving() end
end)
button:SetScript("OnDragStop", function()
	this:StopMovingOrSizing()
	if ZeldaControlsDB then
		local _, _, _, x, y = this:GetPoint()
		ZeldaControlsDB.potionPos = { x, y }
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
		GameTooltip:SetText("Potion slot", 1, 1, 1)
	end
	GameTooltip:AddLine("Press 6 or click to drink. Right-click a healing or mana potion in your bags to put it here. Shift-drag to move.", 0.6, 0.8, 1, 1)
	GameTooltip:Show()
end)
button:SetScript("OnLeave", function()
	GameTooltip:Hide()
end)

-- ------------------------------------------------------------------ right-click in the bags
local function ShopOpen()
	for _, name in ipairs({ "MerchantFrame", "BankFrame", "TradeFrame", "MailFrame", "AuctionFrame", "SendMailFrame" }) do
		local f = getglobal(name)
		if f and f:IsVisible() then
			return true
		end
	end
	return false
end

UseContainerItem = function(bag, slot, onSelf)
	if not ShopOpen() then
		local link = GetContainerItemLink(bag, slot)
		local name = ItemName(link)
		if IsPotionName(name) then
			ZeldaControlsDB = ZeldaControlsDB or {}
			ZeldaControlsDB.potion = ZeldaControlsDB.potion or {}
			ZeldaControlsDB.potion[Key()] = ItemId(link)
			UIErrorsFrame:AddMessage("Potion slot: " .. name .. " (press 6 to drink)", 0.4, 1, 0.4)
			Refresh()
			return
		end
	end
	origUseContainerItem(bag, slot, onSelf)
end

local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("BAG_UPDATE")
events:RegisterEvent("VARIABLES_LOADED")
events:SetScript("OnEvent", function()
	if event == "VARIABLES_LOADED" and ZeldaControlsDB and ZeldaControlsDB.potionPos then
		local p = ZeldaControlsDB.potionPos
		button:ClearAllPoints()
		button:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", p[1], p[2])
	end
	Refresh()
end)
