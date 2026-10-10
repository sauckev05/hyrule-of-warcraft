-- Zelda HUD: 20 hearts in place of the health bar and a green magic meter in place of the rage
-- bar, top left like Ocarina of Time. The player frame is hidden, and enemies show no health bar
-- (the target frame keeps its name and portrait; enemy nameplates are turned off).

local MEDIA = "Interface\\AddOns\\ZeldaHUD\\media\\"
local HEARTS = 20
local PER_ROW = 10
local HEART_SIZE = 26
local HEART_GAP = 1

local hud = CreateFrame("Frame", "ZeldaHUDFrame", UIParent)
hud:SetWidth(PER_ROW * (HEART_SIZE + HEART_GAP))
hud:SetHeight(2 * (HEART_SIZE + HEART_GAP) + 26)
hud:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 18, -14)
hud:SetFrameStrata("LOW")

local hearts = {}
for i = 1, HEARTS do
	local t = hud:CreateTexture("ZeldaHUDHeart" .. i, "ARTWORK")
	t:SetWidth(HEART_SIZE)
	t:SetHeight(HEART_SIZE)
	local row = math.floor((i - 1) / PER_ROW)
	local col = (i - 1) - row * PER_ROW
	t:SetPoint("TOPLEFT", hud, "TOPLEFT", col * (HEART_SIZE + HEART_GAP), -row * (HEART_SIZE + HEART_GAP))
	t:SetTexture(MEDIA .. "heart4")
	hearts[i] = t
end

-- the magic meter: a green bar inside a gold frame
local magic = CreateFrame("StatusBar", "ZeldaHUDMagic", hud)
magic:SetWidth(200)
magic:SetHeight(12)
magic:SetPoint("TOPLEFT", hud, "TOPLEFT", 8, -(2 * (HEART_SIZE + HEART_GAP) + 9))
magic:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
magic:SetStatusBarColor(0.15, 0.85, 0.2)
magic:SetMinMaxValues(0, 100)
magic:SetValue(0)
local magicBg = magic:CreateTexture(nil, "BACKGROUND")
magicBg:SetAllPoints(magic)
magicBg:SetTexture(0, 0, 0, 0.6)
local magicFrame = magic:CreateTexture(nil, "OVERLAY")
magicFrame:SetTexture(MEDIA .. "magicframe")
magicFrame:SetPoint("TOPLEFT", magic, "TOPLEFT", -9, 10)
magicFrame:SetPoint("BOTTOMRIGHT", magic, "BOTTOMRIGHT", 9, -10)

-- a low-health warning, as Ocarina beeps: the hearts pulse at three hearts or less
local lowHealth = false
local pulse = 0

local function UpdateHearts()
	local hp, max = UnitHealth("player"), UnitHealthMax("player")
	local quarters = 0
	if max and max > 0 and hp and hp > 0 then
		quarters = math.ceil(hp / max * HEARTS * 4)
	end
	for i = 1, HEARTS do
		local q = quarters - (i - 1) * 4
		if q < 0 then q = 0 elseif q > 4 then q = 4 end
		hearts[i]:SetTexture(MEDIA .. "heart" .. q)
	end
	lowHealth = quarters > 0 and quarters <= 12
	if not lowHealth then
		for i = 1, HEARTS do hearts[i]:SetAlpha(1) end
	end
end

local function UpdateMagic()
	local power, max = UnitMana("player"), UnitManaMax("player")
	if not max or max <= 0 then max = 100 end
	magic:SetMinMaxValues(0, max)
	magic:SetValue(power or 0)
end

hud:SetScript("OnUpdate", function()
	if not lowHealth then return end
	pulse = pulse + arg1
	local a = 0.55 + 0.45 * math.abs(math.cos(pulse * 3))
	for i = 1, HEARTS do hearts[i]:SetAlpha(a) end
end)

-- the player frame goes away for good; the hearts and magic meter replace it
local function HidePlayerFrame()
	if PlayerFrame then
		PlayerFrame:Hide()
		PlayerFrame:SetScript("OnShow", function() this:Hide() end)
	end
end

-- enemies show no health bar: the target frame's bars are made invisible and nameplates are off
local function HideEnemyBars()
	local names = { "TargetFrameHealthBar", "TargetFrameManaBar", "TargetFrameHealthBarText", "TargetFrameManaBarText" }
	for _, name in ipairs(names) do
		local f = getglobal(name)
		if f then f:SetAlpha(0) end
	end
	if HideNameplates then HideNameplates() end
end

-- the target frame moves right so the hearts have the corner
local function MoveTargetFrame()
	if TargetFrame then
		TargetFrame:ClearAllPoints()
		TargetFrame:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 320, -4)
	end
end

hud:RegisterEvent("PLAYER_ENTERING_WORLD")
hud:RegisterEvent("UNIT_HEALTH")
hud:RegisterEvent("UNIT_MAXHEALTH")
hud:RegisterEvent("UNIT_RAGE")
hud:RegisterEvent("UNIT_MAXRAGE")
hud:RegisterEvent("UNIT_MANA")
hud:RegisterEvent("UNIT_MAXMANA")
hud:RegisterEvent("UNIT_ENERGY")
hud:RegisterEvent("UNIT_MAXENERGY")
hud:RegisterEvent("UNIT_DISPLAYPOWER")
hud:RegisterEvent("PLAYER_TARGET_CHANGED")
hud:SetScript("OnEvent", function()
	if event == "PLAYER_ENTERING_WORLD" then
		HidePlayerFrame()
		MoveTargetFrame()
		HideEnemyBars()
		UpdateHearts()
		UpdateMagic()
	elseif event == "PLAYER_TARGET_CHANGED" then
		HideEnemyBars()
	elseif arg1 == "player" then
		if event == "UNIT_HEALTH" or event == "UNIT_MAXHEALTH" then
			UpdateHearts()
		else
			UpdateMagic()
		end
	end
end)
