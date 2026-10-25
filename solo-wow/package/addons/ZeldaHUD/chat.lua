-- Zelda HUD: no chat window.
--
-- The chat windows (and the combat log) are hidden. What still matters - skill-ups, things you
-- learn, loot, money, experience, reputation, whispers and the server's notices - shows in front
-- of the screen in the warning text area instead, each in its usual chat colour. The Enter key
-- still opens the chat box to talk or type commands.

local HIDDEN_LINE = "^Z%u+:"           -- the server's hidden lines for the other Zelda HUD parts

-- event -> the ChatTypeInfo colour it uses
local RELAY = {
	CHAT_MSG_SKILL = "SKILL",
	CHAT_MSG_SYSTEM = "SYSTEM",
	CHAT_MSG_LOOT = "LOOT",
	CHAT_MSG_MONEY = "MONEY",
	CHAT_MSG_COMBAT_XP_GAIN = "COMBAT_XP_GAIN",
	CHAT_MSG_COMBAT_FACTION_CHANGE = "COMBAT_FACTION_CHANGE",
	CHAT_MSG_WHISPER = "WHISPER",
	CHAT_MSG_MONSTER_WHISPER = "MONSTER_WHISPER",
	CHAT_MSG_MONSTER_EMOTE = "MONSTER_EMOTE",
}

local HOLD = 5                         -- seconds a line stays before it fades

local function Colour(kind)
	local info = ChatTypeInfo and ChatTypeInfo[kind]
	if info and info.r then
		return info.r, info.g, info.b
	end
	if kind == "SKILL" then
		return 0.33, 0.33, 1.0
	end
	return 1.0, 1.0, 0.0
end

local function Show(text, kind)
	if not text or text == "" or not UIErrorsFrame then
		return
	end
	local r, g, b = Colour(kind)
	UIErrorsFrame:AddMessage(text, r, g, b, 1.0, HOLD)
end

local function Relay(event)
	local kind = RELAY[event]
	if not kind or not arg1 then
		return
	end
	if event == "CHAT_MSG_SYSTEM" and string.find(arg1, HIDDEN_LINE) then
		return
	end
	local text = arg1
	if event == "CHAT_MSG_WHISPER" or event == "CHAT_MSG_MONSTER_WHISPER" then
		text = (arg2 or "") .. " whispers: " .. arg1
	elseif event == "CHAT_MSG_MONSTER_EMOTE" then
		text = string.gsub(arg1, "%%s", arg2 or "")
	end
	Show(text, kind)
end

-- ------------------------------------------------------------------ hide the windows
local function HideNamed(name)
	local f = getglobal(name)
	if f and f.IsVisible and f:IsVisible() then
		f:Hide()
	end
end

local function HideChat()
	local windows = NUM_CHAT_WINDOWS or 7
	for i = 1, windows do
		HideNamed("ChatFrame" .. i)
		HideNamed("ChatFrame" .. i .. "Tab")
		HideNamed("ChatFrame" .. i .. "TabDockRegion")
	end
	HideNamed("ChatFrameMenuButton")
	HideNamed("ChatMenu")
	-- the chat box must not go with the window it sits under
	local box = ChatFrameEditBox
	if box and box.GetParent and box:GetParent() ~= UIParent then
		pcall(box.SetParent, box, UIParent)
	end
end

local relay = CreateFrame("Frame", "ZeldaChatRelay", UIParent)
for event in pairs(RELAY) do
	relay:RegisterEvent(event)
end
relay:RegisterEvent("PLAYER_ENTERING_WORLD")
relay:RegisterEvent("UPDATE_CHAT_WINDOWS")
relay:SetScript("OnEvent", function()
	if event == "PLAYER_ENTERING_WORLD" or event == "UPDATE_CHAT_WINDOWS" then
		HideChat()
	else
		Relay(event)
	end
end)

-- the stock UI shows the windows again now and then (tabs on mouse-over, docking, new windows)
local since = 0
relay:SetScript("OnUpdate", function()
	since = since + (arg1 or 0)
	if since >= 0.5 then
		since = 0
		HideChat()
	end
end)

HideChat()

-- With no chat window a script error would go unseen: show it in front of the screen instead.
pcall(function()
	local previous = geterrorhandler and geterrorhandler()
	seterrorhandler(function(msg)
		if UIErrorsFrame then
			UIErrorsFrame:AddMessage("Interface error: " .. tostring(msg), 1.0, 0.25, 0.25, 1.0, 12)
		end
		if previous then
			return previous(msg)
		end
	end)
end)
