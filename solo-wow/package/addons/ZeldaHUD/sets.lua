-- Zelda armor sets in item tooltips: the set's name with how many pieces you wear, every piece (lit
-- when worn, with where it drops when not), and the 2/3/6 piece bonuses, green once they are active.
-- The bonuses themselves are applied by the Azeroth Solo server. Set data: setsdata.lua.

local setOfItem = {}
for setId, set in pairs(ZELDA_SETS or {}) do
	for _, piece in ipairs(set.items) do
		setOfItem[piece[1]] = setId
	end
end

local function ItemIdFromLink(link)
	if not link then return nil end
	local _, _, id = string.find(link, "item:(%d+)")
	return id and tonumber(id)
end

local function WornPieces()
	local worn = {}
	for slot = 1, 19 do
		local id = ItemIdFromLink(GetInventoryItemLink("player", slot))
		if id and setOfItem[id] then
			worn[id] = true
		end
	end
	return worn
end

local function AddSetLines(tooltip, link)
	local setId = setOfItem[ItemIdFromLink(link) or 0]
	if not setId then return end
	local set = ZELDA_SETS[setId]
	local worn = WornPieces()
	local count, total = 0, 0
	for _, piece in ipairs(set.items) do
		total = total + 1
		if worn[piece[1]] then count = count + 1 end
	end

	tooltip:AddLine(" ")
	tooltip:AddLine(set.name .. " (" .. count .. "/" .. total .. ")", 1, 0.82, 0)
	for _, piece in ipairs(set.items) do
		if worn[piece[1]] then
			tooltip:AddLine("  " .. piece[2], 1, 1, 0.6)
		else
			tooltip:AddLine("  " .. piece[2] .. " - " .. piece[3], 0.5, 0.5, 0.5)
		end
	end
	tooltip:AddLine(" ")
	for _, bonus in ipairs(set.bonuses) do
		if count >= bonus[1] then
			tooltip:AddLine(bonus[2], 0, 1, 0, 1)
		else
			tooltip:AddLine(bonus[2], 0.5, 0.5, 0.5, 1)
		end
	end
	tooltip:Show()
end

local function Hook(method, linkOf)
	local orig = GameTooltip[method]
	if not orig then return end
	GameTooltip[method] = function(self, a1, a2, a3)
		local r1, r2, r3 = orig(self, a1, a2, a3)
		AddSetLines(self, linkOf(a1, a2, a3))
		return r1, r2, r3
	end
end

Hook("SetBagItem", function(bag, slot) return GetContainerItemLink(bag, slot) end)
Hook("SetInventoryItem", function(unit, slot) return GetInventoryItemLink(unit, slot) end)
Hook("SetLootItem", function(slot) return GetLootSlotLink(slot) end)
Hook("SetHyperlink", function(link) return link end)
Hook("SetMerchantItem", function(index) return GetMerchantItemLink(index) end)
Hook("SetQuestItem", function(kind, index) return GetQuestItemLink(kind, index) end)
Hook("SetQuestLogItem", function(kind, index) return GetQuestLogItemLink(kind, index) end)

-- the gear comparison tooltips show the set too
for i = 1, 2 do
	local tip = getglobal("ZeldaCompareTooltip" .. i)
	if tip then
		local orig = tip.SetInventoryItem
		tip.SetInventoryItem = function(self, unit, slot)
			local r1, r2, r3 = orig(self, unit, slot)
			AddSetLines(self, GetInventoryItemLink(unit, slot))
			return r1, r2, r3
		end
	end
end
