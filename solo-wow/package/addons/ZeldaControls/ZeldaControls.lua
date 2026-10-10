-- Zelda Controls: Ocarina of Time style combat for World of Warcraft 1.12.
-- The moves themselves run on the Azeroth Solo server (.zslash, .zspin, .zroll, .zflip, .zshield, .zhook).
-- Your equipped weapons set the style: one-hander + shield (quick, can block), two-hander like the
-- Biggoron's Sword (slow, wide, long reach, no shield), or two weapons (both hands strike, no shield).

BINDING_HEADER_ZELDA = "Zelda Controls"
BINDING_NAME_ZELDA_ATTACK = "Sword (hold, then release for Spin Attack)"
BINDING_NAME_ZELDA_SHIELD = "Shield (hold)"
BINDING_NAME_ZELDA_ROLL = "Roll forward"
BINDING_NAME_ZELDA_ROLL_LEFT = "Roll left"
BINDING_NAME_ZELDA_ROLL_RIGHT = "Roll right"
BINDING_NAME_ZELDA_FLIP = "Backflip"
BINDING_NAME_ZELDA_BOW = "Fire bow / ranged weapon"
BINDING_NAME_ZELDA_HOOK = "Hookshot to target"
BINDING_NAME_ZELDA_TARGET = "Z-Target (hold to lock on) - Shift already does this"

local SPIN_HOLD = 0.8
local attackDownAt = nil

function ZeldaControls_Command(cmd)
	SendChatMessage(cmd, "SAY")
end

function ZeldaControls_Attack(state)
	if state == "down" then
		attackDownAt = GetTime()
		ZeldaControls_Command(".zslash")
	else
		if attackDownAt and GetTime() - attackDownAt >= SPIN_HOLD then
			ZeldaControls_Command(".zspin")
		end
		attackDownAt = nil
	end
end

local shieldUp = false
function ZeldaControls_Shield(state)
	local wanted = (state == "down")
	if wanted ~= shieldUp then
		shieldUp = wanted
		ZeldaControls_Command(wanted and ".zshield on" or ".zshield off")
		if ZeldaControlsShieldText then
			if wanted then ZeldaControlsShieldText:Show() else ZeldaControlsShieldText:Hide() end
		end
	end
end

-- Hold to lock on, as in Ocarina of Time. The camera lock exists in the Zelda of Warcraft client
-- (Benilla); in the stock client this simply targets the nearest enemy.
function ZeldaControls_Target(state)
	if state == "up" then
		if ZeldaLock then ZeldaLock(0) end
		return
	end
	if not UnitExists("target") or UnitIsDead("target") or not UnitCanAttack("player", "target") then
		TargetNearestEnemy()
	end
	if ZeldaLock then ZeldaLock(1) end
end

-- default keys, applied once per account (version 4: sword 1, bow 2, shield 3, hookshot 4, roll Shift+W;
-- lock-on is the Shift key itself, watched below, since WoW cannot bind a lone modifier key)
local DEFAULT_KEYS = {
	{ "1", "ZELDA_ATTACK" },
	{ "2", "ZELDA_BOW" },
	{ "3", "ZELDA_SHIELD" },
	{ "4", "ZELDA_HOOK" },
	{ "SHIFT-W", "ZELDA_ROLL" },
	{ "SHIFT-A", "ZELDA_ROLL_LEFT" },
	{ "SHIFT-D", "ZELDA_ROLL_RIGHT" },
	{ "SHIFT-S", "ZELDA_FLIP" },
}
-- keys older versions used; freed if they still hold a Zelda move
local OLD_KEYS = { "F", "G", "R", "V", "H", "Z" }
local KEYS_VERSION = 4
local HELP = "|cff33ff99Zelda Controls|r: hold Shift to lock on (Q/E circle the target), 1 sword (hold = spin attack), 2 bow, 3 shield (hold), 4 hookshot, Shift+W roll, Shift+A/D side roll, Shift+S backflip."

local frame = CreateFrame("Frame", "ZeldaControlsFrame", UIParent)
frame:RegisterEvent("VARIABLES_LOADED")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:SetScript("OnEvent", function()
	if event == "VARIABLES_LOADED" then
		if not ZeldaControlsDB then ZeldaControlsDB = {} end
		if (ZeldaControlsDB.keysVersion or 0) < KEYS_VERSION then
			if GetBindingAction then
				for _, key in ipairs(OLD_KEYS) do
					local action = GetBindingAction(key)
					if action and string.find(action, "^ZELDA_") then
						SetBinding(key)
					end
				end
			end
			for _, kv in ipairs(DEFAULT_KEYS) do
				SetBinding(kv[1], kv[2])
			end
			SaveBindings(1)
			ZeldaControlsDB.keysVersion = KEYS_VERSION
		end
	elseif event == "PLAYER_ENTERING_WORLD" then
		DEFAULT_CHAT_FRAME:AddMessage(HELP .. " Change them in Key Bindings.")
	end
end)

-- Z-targeting on Shift: holding Shift locks on, letting go releases. Shift with W/A/D/S still rolls
-- and backflips, so those happen while locked on, like Ocarina's Z + A. Not while typing in chat.
local shiftHeld = false
local shiftWatcher = CreateFrame("Frame", "ZeldaControlsShiftWatcher", UIParent)
shiftWatcher:SetScript("OnUpdate", function()
	local down = IsShiftKeyDown() and true or false
	if down and ChatFrameEditBox and ChatFrameEditBox:IsVisible() then
		down = false
	end
	if down ~= shiftHeld then
		shiftHeld = down
		ZeldaControls_Target(down and "down" or "up")
	end
end)

-- a small "shield up" indicator above the action bar
local shieldText = UIParent:CreateFontString("ZeldaControlsShieldText", "OVERLAY", "GameFontNormalLarge")
shieldText:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 140)
shieldText:SetText("|cff66ccffSHIELD UP|r")
shieldText:Hide()

-- the server answers moves silently; hide the rare system replies about cooldowns from spamming
SLASH_ZELDA1 = "/zelda"
SlashCmdList["ZELDA"] = function()
	DEFAULT_CHAT_FRAME:AddMessage(HELP)
end
