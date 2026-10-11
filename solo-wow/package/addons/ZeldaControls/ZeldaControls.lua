-- Zelda Controls: Ocarina of Time style combat for World of Warcraft 1.12.
-- The moves themselves run on the Azeroth Solo server (.zslash, .zspin, .zroll, .zflip, .zshield, .zboomerang, .zbow).
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
BINDING_NAME_ZELDA_HOOK = "Boomerang (stuns or disarms)"
BINDING_NAME_ZELDA_TARGET = "Z-Target (hold to lock on) - tapping Shift already toggles it"

local SPIN_HOLD = 0.8
local attackDownAt = nil

function ZeldaControls_Command(cmd)
	SendChatMessage(cmd, "SAY")
end

-- The Spin Attack's charge bar: a cast bar (like Slam's) that fills while the sword key is held,
-- and turns green when the spin is ready to be let go.
local SPIN_BAR_DELAY = 0.15        -- a quick tap never shows the bar
local spinBar = CreateFrame("StatusBar", "ZeldaSpinBar", UIParent)
spinBar:SetWidth(195)
spinBar:SetHeight(13)
spinBar:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 175)
spinBar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
spinBar:SetMinMaxValues(0, SPIN_HOLD)
spinBar:SetValue(0)
spinBar:Hide()
local spinBg = spinBar:CreateTexture(nil, "BACKGROUND")
spinBg:SetAllPoints(spinBar)
spinBg:SetTexture(0, 0, 0, 0.5)
local spinBorder = spinBar:CreateTexture(nil, "OVERLAY")
spinBorder:SetTexture("Interface\\CastingBar\\UI-CastingBar-Border")
spinBorder:SetWidth(256)
spinBorder:SetHeight(64)
spinBorder:SetPoint("TOP", spinBar, "TOP", 0, 28)
local spinSpark = spinBar:CreateTexture(nil, "OVERLAY")
spinSpark:SetTexture("Interface\\CastingBar\\UI-CastingBar-Spark")
spinSpark:SetBlendMode("ADD")
spinSpark:SetWidth(32)
spinSpark:SetHeight(32)
local spinText = spinBar:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
spinText:SetPoint("TOP", spinBar, "TOP", 0, 5)

local function SpinRageShort()
	return UnitPowerType("player") == 1 and UnitMana("player") < 50
end

spinBar:SetScript("OnUpdate", function()
	if not attackDownAt then
		this:Hide()
		return
	end
	local held = GetTime() - attackDownAt
	this:SetValue(math.min(held, SPIN_HOLD))
	spinSpark:SetPoint("CENTER", this, "LEFT", 195 * math.min(held, SPIN_HOLD) / SPIN_HOLD, 0)
	if held >= SPIN_HOLD then
		if SpinRageShort() then
			this:SetStatusBarColor(0.6, 0.6, 0.6)
			spinText:SetText("Spin Attack - not enough rage")
		else
			this:SetStatusBarColor(0.0, 1.0, 0.0)
			spinText:SetText("Spin Attack - release!")
		end
		spinSpark:Hide()
	else
		this:SetStatusBarColor(1.0, 0.7, 0.0)
		spinText:SetText("Spin Attack")
		spinSpark:Show()
	end
end)

-- shows the bar once the key has been held a moment
local spinWatch = CreateFrame("Frame", "ZeldaSpinWatch", UIParent)
spinWatch:SetScript("OnUpdate", function()
	if attackDownAt and not spinBar:IsVisible() and GetTime() - attackDownAt >= SPIN_BAR_DELAY then
		spinBar:Show()
	end
end)

function ZeldaControls_Attack(state)
	if state == "down" then
		attackDownAt = GetTime()
		ZeldaControls_Command(".zslash")
	else
		if attackDownAt and GetTime() - attackDownAt >= SPIN_HOLD then
			ZeldaControls_Command(".zspin")
		end
		attackDownAt = nil
		spinBar:Hide()
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

-- A Shift combo (side roll, backflip) was used during this Shift press, so releasing Shift must
-- not toggle the lock.
local shiftComboUsed = false
function ZeldaControls_ShiftMove(cmd)
	shiftComboUsed = true
	ZeldaControls_Command(cmd)
end

-- Tap Shift to lock on, tap again to let go. A dead or missing target picks the nearest enemy.
function ZeldaControls_ToggleLock()
	if not UnitExists("target") or UnitIsDead("target") or not UnitCanAttack("player", "target") then
		TargetNearestEnemy()
		if ZeldaLock then ZeldaLock(1) end
	elseif ZeldaLock then
		ZeldaLock(2) -- toggle
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

-- default keys, applied once per account (version 5: sword 1, bow 2, shield 3, boomerang 4, roll 5,
-- Shift+Q/E side roll, Shift+S backflip; lock-on is a tap of the Shift key itself, watched below,
-- since WoW cannot bind a lone modifier key)
local DEFAULT_KEYS = {
	{ "1", "ZELDA_ATTACK" },
	{ "2", "ZELDA_BOW" },
	{ "3", "ZELDA_SHIELD" },
	{ "4", "ZELDA_HOOK" },
	{ "5", "ZELDA_ROLL" },
	{ "SHIFT-Q", "ZELDA_ROLL_LEFT" },
	{ "SHIFT-E", "ZELDA_ROLL_RIGHT" },
	{ "SHIFT-S", "ZELDA_FLIP" },
}
-- keys older versions used; freed if they still hold a Zelda move
local OLD_KEYS = { "F", "G", "R", "V", "H", "Z", "SHIFT-W", "SHIFT-A", "SHIFT-D" }
local KEYS_VERSION = 5
local HELP = "|cff33ff99Zelda Controls|r: tap Shift to lock on / let go, 1 sword (hold = spin attack, 50 rage), 2 bow, 3 shield (hold), 4 boomerang, 5 roll, Shift+Q/E side roll, Shift+S backflip."

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

-- Z-targeting on Shift: a quick tap toggles the lock (on, then off with the next tap). Holding
-- Shift for a Shift combo (side roll, backflip) or for longer than a tap does not toggle it. Not
-- while typing in chat.
local SHIFT_TAP = 0.35
local shiftHeld = false
local shiftDownAt = 0
local shiftWatcher = CreateFrame("Frame", "ZeldaControlsShiftWatcher", UIParent)
shiftWatcher:SetScript("OnUpdate", function()
	local down = IsShiftKeyDown() and true or false
	if down and ChatFrameEditBox and ChatFrameEditBox:IsVisible() then
		down = false
		shiftComboUsed = true
	end
	if down == shiftHeld then return end
	shiftHeld = down
	if down then
		shiftDownAt = GetTime()
		shiftComboUsed = false
	elseif not shiftComboUsed and GetTime() - shiftDownAt <= SHIFT_TAP then
		ZeldaControls_ToggleLock()
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
