-- Zelda Controls: putting on a bag.
--
-- The bag slots are hidden with the action bar, so right-clicking a bag in your bags puts it on:
-- into an empty bag slot, else in place of your smallest bag when the new one is bigger. The
-- smaller bag's things move to free room in your other bags first, and the smaller bag goes
-- where the new one was (the server does the moving: .zbag <bag> <slot>).

local function OtherWindowOpen()
	for _, name in ipairs({ "MerchantFrame", "BankFrame", "TradeFrame", "MailFrame", "AuctionFrame", "SendMailFrame" }) do
		local f = getglobal(name)
		if f and f:IsVisible() then
			return true
		end
	end
	return false
end

local function IsBag(bag, slot)
	local link = GetContainerItemLink(bag, slot)
	local _, _, id = string.find(link or "", "item:(%d+)")
	if not id then
		return false
	end
	local _, _, _, _, _, _, _, equipLoc = GetItemInfo(tonumber(id))
	return equipLoc == "INVTYPE_BAG"
end

local previousUse = UseContainerItem
UseContainerItem = function(bag, slot, onSelf)
	if bag and bag >= 0 and bag <= 4 and not OtherWindowOpen() and not CursorHasItem() and IsBag(bag, slot) then
		ZeldaControls_Command(".zbag " .. bag .. " " .. slot)
		return
	end
	previousUse(bag, slot, onSelf)
end
