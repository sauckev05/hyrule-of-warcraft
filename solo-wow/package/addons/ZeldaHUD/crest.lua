-- Zelda HUD: a crest of your own. Without a guild, the tabard vendor's "Create crest." designs a
-- crest for you alone, and the Universal Tabard shows it. The server keeps the crest and sends it
-- as a hidden "ZCREST:emblem;color;border;borderColor;background" line; this hands it to the
-- Zelda of Warcraft client (ZeldaSetCrest), which paints it on your tabard.

local function Parse(msg)
	local _, _, a, b, c, d, e = string.find(msg, "^ZCREST:(%-?%d+);(%-?%d+);(%-?%d+);(%-?%d+);(%-?%d+)")
	if a and ZeldaSetCrest then
		ZeldaSetCrest(tonumber(a), tonumber(b), tonumber(c), tonumber(d), tonumber(e))
	end
end

-- keep the server's line out of the chat window
local origChatFrameOnEvent = ChatFrame_OnEvent
ChatFrame_OnEvent = function(event)
	if event == "CHAT_MSG_SYSTEM" and arg1 and string.sub(arg1, 1, 7) == "ZCREST:" then
		return
	end
	origChatFrameOnEvent(event)
end

local f = CreateFrame("Frame")
f:RegisterEvent("CHAT_MSG_SYSTEM")
f:RegisterEvent("PLAYER_ENTERING_WORLD")
f:SetScript("OnEvent", function()
	if event == "CHAT_MSG_SYSTEM" then
		if arg1 and string.sub(arg1, 1, 7) == "ZCREST:" then
			Parse(arg1)
		end
	else
		SendChatMessage(".zcrest", "SAY")
	end
end)

-- The stock designer lets only a guild master accept. A hero without a guild may always design
-- her own crest: while the designer is open, Accept stays enabled for her. (Checked every frame: the stock TabardFrame_Update re-greys the button
-- on every change, and it may be defined after this addon loads.)
local CREST_GREETING = "Design a crest of your own. Wear a Universal Tabard to show it."

local function CanSaveOwnCrest()
	-- the client still checks the design and the money when Accept is pressed
	return not IsInGuild() and TabardModel ~= nil
end

local watcher = CreateFrame("Frame", "ZeldaCrestWatcher", UIParent)
watcher:SetScript("OnUpdate", function()
	if not TabardFrame or not TabardFrame:IsVisible() then
		return
	end
	if CanSaveOwnCrest() then
		if TabardFrameGreetingText:GetText() ~= CREST_GREETING then
			TabardFrameGreetingText:SetText(CREST_GREETING)
		end
		if not TabardFrameAcceptButton:IsEnabled() or TabardFrameAcceptButton:IsEnabled() == 0 then
			TabardFrameAcceptButton:Enable()
		end
	end
end)
