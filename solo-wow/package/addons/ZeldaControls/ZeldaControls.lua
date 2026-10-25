-- Zelda Controls: Ocarina of Time style combat for World of Warcraft 1.12.
-- The moves themselves run on the Azeroth Solo server (.zslash, .zspin, .zroll, .zflip, .zshield, .zboomerang, .zbow).
-- Your equipped weapons set the style: one-hander + shield (quick, can block), two-hander like the
-- Biggoron's Sword (slow, wide, long reach, no shield), or two weapons (both hands strike, no shield).

BINDING_HEADER_ZELDA = "Zelda Controls"
BINDING_NAME_ZELDA_ATTACK = "Sword (hold, then release for Spin Attack / Shield Slam in Defensive Stance)"
BINDING_NAME_ZELDA_SHIELD = "Shield / parry (hold)"
BINDING_NAME_ZELDA_ROLL = "Roll forward"
BINDING_NAME_ZELDA_ROLL_LEFT = "Roll left"
BINDING_NAME_ZELDA_ROLL_RIGHT = "Roll right"
BINDING_NAME_ZELDA_FLIP = "Backflip"
BINDING_NAME_ZELDA_BOW = "Fire bow / ranged weapon"
BINDING_NAME_ZELDA_HOOK = "Boomerang (stuns or disarms)"
BINDING_NAME_ZELDA_POTION = "Drink the potion in the potion slot"
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

-- The charged attack follows the stance: in Defensive Stance with a shield a Shield Slam (stuns the
-- enemies in front for 2 seconds, damage = the shield's armor), in Berserker Stance a Leaping
-- Strike (one enemy in front, twice the attack power), otherwise the Spin Attack.
local LEAP_SECONDS = 1.2          -- the leap's animation length
local function ChargedAttackName()
	for i = 1, (GetNumShapeshiftForms and GetNumShapeshiftForms() or 0) do
		local _, name, active = GetShapeshiftFormInfo(i)
		if active and name == "Berserker Stance" then
			return "Leaping Strike"
		end
		if active and name == "Defensive Stance" then
			local link = GetInventoryItemLink("player", 17)
			local _, _, id = string.find(link or "", "item:(%d+)")
			if id then
				local _, _, _, _, _, _, _, equipLoc = GetItemInfo(tonumber(id))
				if equipLoc == "INVTYPE_SHIELD" then
					return "Shield Slam"
				end
			end
		end
	end
	return "Spin Attack"
end

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
			spinText:SetText(ChargedAttackName() .. " - not enough rage")
		else
			this:SetStatusBarColor(0.0, 1.0, 0.0)
			spinText:SetText(ChargedAttackName() .. " - release!")
		end
		spinSpark:Hide()
	else
		this:SetStatusBarColor(1.0, 0.7, 0.0)
		spinText:SetText(ChargedAttackName())
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

-- The sword combo, as Link swings: a right slash, a left slash, then a special strike (Heroic
-- Strike's). A swing locks the sword until its animation is done - pressing mid-swing does
-- nothing - and how long that takes follows the weapon's speed. Keep in step with the server's
-- SlashDurationMs (ZeldaCommands.cpp).
local COMBO_STEPS = 3
local COMBO_CHAIN = 1.1          -- seconds after a swing ends that the next one still continues the combo
local swingReadyAt = 0
local comboStep = 0

local TWO_HANDED_SLOWER = 1.5   -- a two-handed weapon swings 50% slower

local function MainHandTwoHanded()
	local link = GetInventoryItemLink("player", 16)
	if not link then return false end
	local _, _, id = string.find(link, "item:(%d+)")
	if not id then return false end
	local _, _, _, _, _, _, _, equipLoc = GetItemInfo(tonumber(id))
	return equipLoc == "INVTYPE_2HWEAPON"
end

-- Flurry speeds every combo swing by its percentage (10% per rank step: 10/15/20/25/30) instead
-- of the auto attack. Keep in step with the server's ZeldaFlurryPercent.
local function FlurryPercent()
	local up = false
	for i = 1, 32 do
		local texture = UnitBuff("player", i)
		if not texture then break end
		if string.find(string.lower(texture), "ghoulfrenzy") then
			up = true
			break
		end
	end
	if not up then return 0 end
	for tab = 1, (GetNumTalentTabs() or 0) do
		for i = 1, (GetNumTalents(tab) or 0) do
			local name, _, _, _, rank = GetTalentInfo(tab, i)
			if name == "Flurry" then
				return (rank and rank > 0) and (5 + 5 * rank) or 0
			end
		end
	end
	return 0
end

function ZeldaControls_SwingTime(step)
	local speed = UnitAttackSpeed("player") or 2.0
	local t
	if step >= COMBO_STEPS then
		t = math.min(1.4, math.max(0.4, speed * 0.35))
	else
		t = math.min(1.0, math.max(0.3, speed * 0.25))
	end
	if MainHandTwoHanded() then
		t = t * TWO_HANDED_SLOWER
	end
	return t / (1 + FlurryPercent() / 100)
end

function ZeldaControls_Slash()
	local now = GetTime()
	if now < swingReadyAt then
		return
	end
	if now > swingReadyAt + COMBO_CHAIN or comboStep >= COMBO_STEPS then
		comboStep = 0
	end
	comboStep = comboStep + 1
	local duration = ZeldaControls_SwingTime(comboStep)
	swingReadyAt = now + duration
	-- the Zelda of Warcraft client (Benilla) plays the exact swing; the stock client gets the
	-- server's usual swing animation
	if ZeldaSwingAnim then
		ZeldaSwingAnim(comboStep, duration)
		ZeldaControls_Command(".zslash " .. comboStep .. " 1")
	else
		ZeldaControls_Command(".zslash " .. comboStep .. " 0")
	end
end

function ZeldaControls_Attack(state)
	if state == "down" then
		attackDownAt = GetTime()
		ZeldaControls_Slash()
	else
		if attackDownAt and GetTime() - attackDownAt >= SPIN_HOLD then
			-- the Zelda client plays the Leaping Strike's leap itself
			if ChargedAttackName() == "Leaping Strike" and ZeldaSwingAnim and not SpinRageShort() then
				ZeldaSwingAnim(4, LEAP_SECONDS)
				ZeldaControls_Command(".zspin 1")
			else
				ZeldaControls_Command(".zspin")
			end
		end
		attackDownAt = nil
		spinBar:Hide()
	end
end

-- The guard key: with a shield it raises the shield (80% less damage from the front); with only a
-- weapon the hero holds it up to parry (every melee blow from the front is parried). Holding the
-- key holds the guard pose - the Zelda of Warcraft client stops the block or parry clip at its
-- highest point (ZeldaGuardAnim) - and a quick click plays the whole clip once.
local shieldUp = false
local guardKind = 1

local function HasShield()
	local link = GetInventoryItemLink("player", 17)
	local _, _, id = string.find(link or "", "item:(%d+)")
	if not id then
		return false
	end
	local _, _, _, _, _, _, _, equipLoc = GetItemInfo(tonumber(id))
	return equipLoc == "INVTYPE_SHIELD"
end

function ZeldaControls_Shield(state)
	local wanted = (state == "down")
	if wanted ~= shieldUp then
		shieldUp = wanted
		if wanted then
			guardKind = HasShield() and 1 or 2
			if guardKind == 2 and not GetInventoryItemLink("player", 16) then
				guardKind = 0      -- empty hands: nothing to guard with (the server says so)
			end
		end
		if ZeldaGuardAnim and guardKind > 0 then
			ZeldaGuardAnim(guardKind, wanted)
		end
		ZeldaControls_Command(wanted and ".zshield on" or ".zshield off")
		if ZeldaControlsShieldText then
			ZeldaControlsShieldText:SetText(guardKind == 2 and "|cffffcc66PARRY|r" or "|cff66ccffSHIELD UP|r")
			if wanted and guardKind > 0 then ZeldaControlsShieldText:Show() else ZeldaControlsShieldText:Hide() end
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
	{ "6", "ZELDA_POTION" },
	{ "SHIFT-Q", "ZELDA_ROLL_LEFT" },
	{ "SHIFT-E", "ZELDA_ROLL_RIGHT" },
	{ "SHIFT-S", "ZELDA_FLIP" },
}
-- keys older versions used; freed if they still hold a Zelda move
local OLD_KEYS = { "F", "G", "R", "V", "H", "Z", "SHIFT-W", "SHIFT-A", "SHIFT-D" }
local KEYS_VERSION = 6
local HELP = "|cff33ff99Zelda Controls|r: tap Shift to lock on / let go, 1 sword (hold = spin attack; shield slam in Defensive Stance; leaping strike in Berserker Stance; 50 rage), 2 bow, 3 shield (hold; parry without a shield), 4 boomerang, 5 roll, 6 potion slot (right-click a healing or mana potion to put it there), Shift+Q/E side roll, Shift+S backflip."

local frame = CreateFrame("Frame", "ZeldaControlsFrame", UIParent)
frame:RegisterEvent("VARIABLES_LOADED")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:SetScript("OnEvent", function()
	if event == "VARIABLES_LOADED" then
		if not ZeldaControlsDB then ZeldaControlsDB = {} end
		if (ZeldaControlsDB.keysVersion or 0) == 5 then
			-- version 6 only adds the potion key: keep everything else as it was set
			SetBinding("6", "ZELDA_POTION")
			SaveBindings(1)
			ZeldaControlsDB.keysVersion = KEYS_VERSION
		elseif (ZeldaControlsDB.keysVersion or 0) < KEYS_VERSION then
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
