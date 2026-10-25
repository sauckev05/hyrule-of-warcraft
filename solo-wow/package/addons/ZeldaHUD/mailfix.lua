-- Zelda HUD: the mailbox and the auction house no longer show a script error.
--
-- The stock open-letter view refreshes on every inbox change, also when the letter it last showed
-- is gone (taken, deleted, or the inbox re-read when the auction house sends its mail): it then
-- compares that letter's missing money with zero and fails. Such a refresh now just closes the
-- letter view.

local function LetterGone(id)
	if not id or not GetInboxNumItems or id > GetInboxNumItems() then
		return true
	end
	local _, _, _, _, money, cod = GetInboxHeaderInfo(id)
	return money == nil or cod == nil
end

local function CloseLetter()
	if InboxFrame then
		InboxFrame.openMailID = nil
	end
	if OpenMailFrame and OpenMailFrame:IsVisible() then
		HideUIPanel(OpenMailFrame)
	end
end

local stock = OpenMail_Update
if stock then
	OpenMail_Update = function()
		local id = InboxFrame and InboxFrame.openMailID
		if not id then
			return stock()
		end
		if LetterGone(id) then
			CloseLetter()
			return
		end
		local ok = pcall(stock)
		if not ok then
			CloseLetter()
		end
	end
end
