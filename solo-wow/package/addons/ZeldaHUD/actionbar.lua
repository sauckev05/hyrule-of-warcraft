-- Zelda HUD: no action bar. The main bar's art, buttons, micro buttons and bag buttons are hidden
-- (the Zelda keys, the potion and mount slots, 8 for the bags and 9 for the Subscreen do their
-- work); only the experience bar stays, at the very bottom of the screen, with the reputation bar
-- just above it. The stance buttons sit in a row just under the magic (rage) meter, top left.

local HIDE = {
	"MainMenuBarArtFrame", "BonusActionBarFrame", "MultiBarBottomLeft", "MultiBarBottomRight",
	"MultiBarLeft", "MultiBarRight", "MainMenuBarPerformanceBarFrame", "ShapeshiftBarLeft",
	"ShapeshiftBarMiddle", "ShapeshiftBarRight", "PetActionBarFrame",
}

local function Hide(f)
	if f and f.IsVisible and f:IsVisible() then
		f:Hide()
	end
end

local function Place(f, point, relative, relPoint, x, y)
	if not f then return end
	local p, r, rp, px, py = f:GetPoint()
	if p ~= point or r ~= relative or rp ~= relPoint or math.abs((px or 0) - x) > 0.5 or math.abs((py or 0) - y) > 0.5 then
		f:ClearAllPoints()
		f:SetPoint(point, relative, relPoint, x, y)
	end
end

local function Layout()
	for _, name in ipairs(HIDE) do
		Hide(getglobal(name))
	end
	for i = 1, 12 do
		Hide(getglobal("ActionButton" .. i))
		Hide(getglobal("BonusActionButton" .. i))
	end
	-- the experience bar at the bottom edge, the reputation bar right above it
	if MainMenuExpBar then
		Place(MainMenuExpBar, "BOTTOM", UIParent, "BOTTOM", 0, 0)
	end
	if ReputationWatchBar and MainMenuExpBar then
		Place(ReputationWatchBar, "BOTTOM", MainMenuExpBar, "TOP", 0, 2)
	end
	-- The stance bar keeps its own frame and place (moving the frame itself broke the mouse); its
	-- buttons are moved instead, into a row just under the magic (rage) meter.
	if ShapeshiftBarFrame and ShapeshiftBarFrame.EnableMouse then
		ShapeshiftBarFrame:EnableMouse(false)
	end
	if MainMenuBar and MainMenuBar.EnableMouse then
		MainMenuBar:EnableMouse(false)          -- its art is gone: let clicks reach the world
	end
	local forms = GetNumShapeshiftForms and GetNumShapeshiftForms() or 0
	if forms > 0 and ShapeshiftButton1 then
		if ZeldaHUDMagic then
			-- just under the magic (rage) meter, below its gold frame
			Place(ShapeshiftButton1, "TOPLEFT", ZeldaHUDMagic, "BOTTOMLEFT", -4, -16)
		else
			Place(ShapeshiftButton1, "TOPLEFT", UIParent, "TOPRIGHT", -(205 + forms * 37), -150)
		end
	end
end

-- The stance buttons' lit one follows the stance you are in now: the stock bar lit it when the
-- stance change was announced, before the new stance had landed, so it stayed on the old one.
local function LightStance()
	local forms = GetNumShapeshiftForms and GetNumShapeshiftForms() or 0
	for i = 1, forms do
		local button = getglobal("ShapeshiftButton" .. i)
		if button and button.SetChecked then
			local _, _, active = GetShapeshiftFormInfo(i)
			if active then button:SetChecked(1) else button:SetChecked(nil) end
		end
	end
end

local watcher = CreateFrame("Frame", "ZeldaActionBarWatcher", UIParent)
local since = 0
watcher:SetScript("OnUpdate", function()
	since = since + (arg1 or 0)
	if since >= 0.25 then
		since = 0
		Layout()
	end
	LightStance()
end)
watcher:RegisterEvent("PLAYER_ENTERING_WORLD")
watcher:RegisterEvent("UPDATE_SHAPESHIFT_FORMS")
watcher:RegisterEvent("UPDATE_FACTION")
watcher:SetScript("OnEvent", Layout)
