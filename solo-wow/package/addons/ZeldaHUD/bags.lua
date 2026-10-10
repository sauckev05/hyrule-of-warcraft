-- All bags in one: the backpack and the four bag slots open as a single window (B, the backpack
-- button or any bag button). Bank bags and the keyring keep their own windows.

local COLUMNS = 10
local SIZE = 37
local GAP = 4
local PAD = 10
local TOP = 30
local BOTTOM = 28

local bagFrame = CreateFrame("Frame", "ZeldaBagFrame", UIParent)
bagFrame:SetFrameStrata("HIGH")
bagFrame:SetToplevel(true)
bagFrame:SetMovable(true)
bagFrame:EnableMouse(true)
bagFrame:SetClampedToScreen(true)
bagFrame:SetPoint("BOTTOMRIGHT", UIParent, "BOTTOMRIGHT", -60, 100)
bagFrame:SetBackdrop({
	bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
	edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
	tile = true, tileSize = 32, edgeSize = 24,
	insets = { left = 6, right = 6, top = 6, bottom = 6 },
})
bagFrame:RegisterForDrag("LeftButton")
bagFrame:SetScript("OnDragStart", function() this:StartMoving() end)
bagFrame:SetScript("OnDragStop", function() this:StopMovingOrSizing() end)
bagFrame:Hide()
tinsert(UISpecialFrames, "ZeldaBagFrame")

local title = bagFrame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
title:SetPoint("TOPLEFT", bagFrame, "TOPLEFT", PAD + 2, -11)

local close = CreateFrame("Button", "ZeldaBagFrameClose", bagFrame, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", bagFrame, "TOPRIGHT", -2, -2)

local money = CreateFrame("Frame", "ZeldaBagMoney", bagFrame, "SmallMoneyFrameTemplate")
money:SetPoint("BOTTOMRIGHT", bagFrame, "BOTTOMRIGHT", 4, 10)

-- one holder per bag: the item button template finds its bag through its parent's id
local holders = {}
for bag = 0, 4 do
	local h = CreateFrame("Frame", "ZeldaBagHolder" .. bag, bagFrame)
	h:SetID(bag)
	h:SetAllPoints(bagFrame)
	holders[bag] = h
end

local buttons = {}
local function Button(bag, slot)
	local name = "ZeldaBagItem" .. bag .. "_" .. slot
	local b = getglobal(name)
	if not b then
		b = CreateFrame("Button", name, holders[bag], "ContainerFrameItemButtonTemplate")
		b:SetID(slot)
	end
	return b
end

local function Layout()
	for _, b in ipairs(buttons) do b:Hide() end
	buttons = {}
	local index = 0
	local free = 0
	for bag = 0, 4 do
		local slots = GetContainerNumSlots(bag) or 0
		for slot = 1, slots do
			local b = Button(bag, slot)
			local row = math.floor(index / COLUMNS)
			local col = index - row * COLUMNS
			b:ClearAllPoints()
			b:SetPoint("TOPLEFT", bagFrame, "TOPLEFT", PAD + col * (SIZE + GAP), -(TOP + row * (SIZE + GAP)))
			b:Show()
			table.insert(buttons, b)
			index = index + 1

			local texture, count, locked = GetContainerItemInfo(bag, slot)
			SetItemButtonTexture(b, texture)
			SetItemButtonCount(b, count)
			SetItemButtonDesaturated(b, locked, 0.5, 0.5, 0.5)
			if not texture then free = free + 1 end
			local cooldown = getglobal(b:GetName() .. "Cooldown")
			if cooldown then
				local start, duration, enable = GetContainerItemCooldown(bag, slot)
				CooldownFrame_SetTimer(cooldown, start, duration, enable)
			end
		end
	end
	local rows = math.ceil(index / COLUMNS)
	if rows < 1 then rows = 1 end
	bagFrame:SetWidth(PAD * 2 + COLUMNS * SIZE + (COLUMNS - 1) * GAP)
	bagFrame:SetHeight(TOP + rows * SIZE + (rows - 1) * GAP + BOTTOM)
	title:SetText("Bags  |cffffffff(" .. free .. " free)|r")
	MoneyFrame_Update("ZeldaBagMoney", GetMoney())
end

local function Refresh()
	if bagFrame:IsVisible() then Layout() end
end

bagFrame:SetScript("OnShow", function()
	Layout()
	PlaySound("igBackPackOpen")
end)
bagFrame:SetScript("OnHide", function()
	PlaySound("igBackPackClose")
end)

bagFrame:RegisterEvent("BAG_UPDATE")
bagFrame:RegisterEvent("ITEM_LOCK_CHANGED")
bagFrame:RegisterEvent("BAG_UPDATE_COOLDOWN")
bagFrame:RegisterEvent("PLAYER_MONEY")
bagFrame:RegisterEvent("PLAYER_ENTERING_WORLD")
bagFrame:SetScript("OnEvent", Refresh)

-- open and close: every way of opening a carried bag shows the one window
local function Toggle()
	if bagFrame:IsVisible() then bagFrame:Hide() else bagFrame:Show() end
end

local origToggleBag = ToggleBag
ToggleBag = function(id)
	if id and id >= 0 and id <= 4 then Toggle() else origToggleBag(id) end
end
ToggleBackpack = Toggle
OpenAllBags = function(forceOpen)
	if forceOpen then bagFrame:Show() else Toggle() end
end
OpenBackpack = function() bagFrame:Show() end
CloseBackpack = function() bagFrame:Hide() end
local origCloseAllBags = CloseAllBags
CloseAllBags = function()
	bagFrame:Hide()
	if origCloseAllBags then origCloseAllBags() end
end
local origOpenBag = OpenBag
OpenBag = function(id)
	if id and id >= 0 and id <= 4 then bagFrame:Show() elseif origOpenBag then origOpenBag(id) end
end
local origCloseBag = CloseBag
CloseBag = function(id)
	if id and id >= 0 and id <= 4 then bagFrame:Hide() elseif origCloseBag then origCloseBag(id) end
end
