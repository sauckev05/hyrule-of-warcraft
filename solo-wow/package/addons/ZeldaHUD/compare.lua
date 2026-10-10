-- Gear comparison: hovering an item in your bags also shows what you have equipped in that slot
-- (both rings, both trinkets, or main and off hand), labelled "Currently Equipped".

local SLOTS = {
	INVTYPE_HEAD = { 1 }, INVTYPE_NECK = { 2 }, INVTYPE_SHOULDER = { 3 }, INVTYPE_BODY = { 4 },
	INVTYPE_CHEST = { 5 }, INVTYPE_ROBE = { 5 }, INVTYPE_WAIST = { 6 }, INVTYPE_LEGS = { 7 },
	INVTYPE_FEET = { 8 }, INVTYPE_WRIST = { 9 }, INVTYPE_HAND = { 10 }, INVTYPE_FINGER = { 11, 12 },
	INVTYPE_TRINKET = { 13, 14 }, INVTYPE_CLOAK = { 15 }, INVTYPE_WEAPON = { 16, 17 },
	INVTYPE_2HWEAPON = { 16 }, INVTYPE_WEAPONMAINHAND = { 16 }, INVTYPE_WEAPONOFFHAND = { 17 },
	INVTYPE_SHIELD = { 17 }, INVTYPE_HOLDABLE = { 17 }, INVTYPE_RANGED = { 18 },
	INVTYPE_RANGEDRIGHT = { 18 }, INVTYPE_THROWN = { 18 }, INVTYPE_RELIC = { 18 }, INVTYPE_TABARD = { 19 },
}

local tips = {}
for i = 1, 2 do
	local tip = CreateFrame("GameTooltip", "ZeldaCompareTooltip" .. i, UIParent, "GameTooltipTemplate")
	tip:SetFrameStrata("TOOLTIP")
	local label = tip:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
	label:SetPoint("BOTTOMLEFT", tip, "TOPLEFT", 4, 1)
	label:SetText("Currently Equipped")
	tips[i] = tip
end

local function HideCompare()
	tips[1]:Hide()
	tips[2]:Hide()
end

local function ItemIdFromLink(link)
	if not link then return nil end
	local _, _, id = string.find(link, "item:(%d+)")
	return id and tonumber(id)
end

local function ShowCompare(bag, slot)
	HideCompare()
	local id = ItemIdFromLink(GetContainerItemLink(bag, slot))
	if not id then return end
	local _, _, _, _, _, _, _, equipLoc = GetItemInfo(id)
	local slots = equipLoc and SLOTS[equipLoc]
	if not slots then return end

	-- on the side of the screen with more room
	local onLeft = (GameTooltip:GetRight() or 0) > (UIParent:GetRight() or 1024) - 320
	local anchor = GameTooltip
	local shown = 0
	for _, invSlot in ipairs(slots) do
		if GetInventoryItemLink("player", invSlot) then
			shown = shown + 1
			local tip = tips[shown]
			tip:SetOwner(GameTooltip, "ANCHOR_NONE")
			tip:ClearAllPoints()
			if onLeft then
				tip:SetPoint("TOPRIGHT", anchor, "TOPLEFT", -2, 0)
			else
				tip:SetPoint("TOPLEFT", anchor, "TOPRIGHT", 2, 0)
			end
			tip:SetInventoryItem("player", invSlot)
			tip:Show()
			anchor = tip
		end
	end
end

local origSetBagItem = GameTooltip.SetBagItem
GameTooltip.SetBagItem = function(self, bag, slot)
	local a, b, c = origSetBagItem(self, bag, slot)
	ShowCompare(bag, slot)
	return a, b, c
end

local origOnHide = GameTooltip:GetScript("OnHide")
GameTooltip:SetScript("OnHide", function()
	if origOnHide then origOnHide() end
	HideCompare()
end)
