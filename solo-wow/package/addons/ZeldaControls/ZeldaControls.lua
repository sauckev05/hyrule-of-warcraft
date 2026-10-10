-- Zelda Controls: Ocarina of Time style combat for World of Warcraft 1.12.
-- The moves themselves run on the Azeroth Solo server (.zslash, .zspin, .zroll, .zflip, .zshield, .zhook).

BINDING_HEADER_ZELDA = "Zelda Controls"
BINDING_NAME_ZELDA_ATTACK = "Sword (hold, then release for Spin Attack)"
BINDING_NAME_ZELDA_SHIELD = "Shield (hold)"
BINDING_NAME_ZELDA_ROLL = "Roll forward"
BINDING_NAME_ZELDA_ROLL_LEFT = "Roll left"
BINDING_NAME_ZELDA_ROLL_RIGHT = "Roll right"
BINDING_NAME_ZELDA_FLIP = "Backflip"
BINDING_NAME_ZELDA_HOOK = "Hookshot to target"
BINDING_NAME_ZELDA_TARGET = "Z-Target (hold to lock on)"

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

-- default keys, applied once per account
local DEFAULT_KEYS = {
	{ "F", "ZELDA_ATTACK" },
	{ "R", "ZELDA_SHIELD" },
	{ "V", "ZELDA_ROLL" },
	{ "SHIFT-A", "ZELDA_ROLL_LEFT" },
	{ "SHIFT-D", "ZELDA_ROLL_RIGHT" },
	{ "SHIFT-S", "ZELDA_FLIP" },
	{ "H", "ZELDA_HOOK" },
	{ "Z", "ZELDA_TARGET" },
}

local frame = CreateFrame("Frame", "ZeldaControlsFrame", UIParent)
frame:RegisterEvent("VARIABLES_LOADED")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:SetScript("OnEvent", function()
	if event == "VARIABLES_LOADED" then
		if not ZeldaControlsDB then ZeldaControlsDB = {} end
		if not ZeldaControlsDB.keysSet then
			for _, kv in ipairs(DEFAULT_KEYS) do
				SetBinding(kv[1], kv[2])
			end
			SaveBindings(1)
			ZeldaControlsDB.keysSet = true
		end
	elseif event == "PLAYER_ENTERING_WORLD" then
		DEFAULT_CHAT_FRAME:AddMessage("|cff33ff99Zelda Controls|r: F sword (hold = spin attack), R shield, V roll, Shift+A/D side roll, Shift+S backflip, H hookshot, hold Z to lock on. Change them in Key Bindings.")
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
	DEFAULT_CHAT_FRAME:AddMessage("|cff33ff99Zelda Controls|r: F sword (hold = spin attack), R shield, V roll, Shift+A/D side roll, Shift+S backflip, H hookshot, hold Z to lock on.")
end
