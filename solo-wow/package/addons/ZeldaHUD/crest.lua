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
