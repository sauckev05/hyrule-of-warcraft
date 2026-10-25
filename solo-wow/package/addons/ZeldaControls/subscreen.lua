-- Zelda Controls: the inventory key (8) and the Subscreen (9).
--
-- 8 opens (or closes) the character sheet, every bag and the key ring together.
-- 9 opens the Subscreen, like Ocarina of Time's pause menu: one screen at a time - Spellbook &
-- Abilities, Talents, Quest Log, World Map, Main Menu - and Left / Right (the arrow keys, or the
-- arrows on its title bar) turn to the next screen. 9 or Escape closes it.

-- ------------------------------------------------------------------ inventory
local function KeyRingOpen()
	return KEYRING_CONTAINER and IsBagOpen and IsBagOpen(KEYRING_CONTAINER)
end

function ZeldaControls_Inventory()
	if CharacterFrame and CharacterFrame:IsVisible() then
		HideUIPanel(CharacterFrame)
		if CloseAllBags then CloseAllBags() end
		if KeyRingOpen() and ToggleKeyRing then ToggleKeyRing() end
		return
	end
	if ToggleCharacter then ToggleCharacter("PaperDollFrame") end
	if OpenAllBags then OpenAllBags(1) end
	if not KeyRingOpen() and ToggleKeyRing then ToggleKeyRing() end
end

-- ------------------------------------------------------------------ subscreen
local PAGES = {
	{ name = "Spellbook & Abilities", frame = "SpellBookFrame",
	  open = function() if ToggleSpellBook then ToggleSpellBook(BOOKTYPE_SPELL or "spell") end end },
	{ name = "Talents", frame = "TalentFrame",
	  open = function() if ToggleTalentFrame then ToggleTalentFrame() end end },
	{ name = "Quest Log", frame = "QuestLogFrame",
	  open = function() if ToggleQuestLog then ToggleQuestLog() end end },
	{ name = "World Map", frame = "WorldMapFrame", alt = "ZeldaDungeonMapFrame",
	  open = function() if ToggleWorldMap then ToggleWorldMap() end end },
	{ name = "Main Menu", frame = "GameMenuFrame",
	  open = function() if GameMenuFrame then ShowUIPanel(GameMenuFrame) end end },
}

local page = 0              -- 0 = closed
local switching = 0         -- a moment while one screen closes and the next opens
local savedLeft, savedRight

local function PageFrame(p)
	local f = getglobal(p.frame)
	if p.alt and (not f or not f:IsVisible()) then
		local alt = getglobal(p.alt)
		if alt and alt:IsVisible() then return alt end
	end
	return f
end

local bar = CreateFrame("Frame", "ZeldaSubscreenBar", UIParent)
bar:SetWidth(420)
bar:SetHeight(44)
bar:SetPoint("TOP", UIParent, "TOP", 0, -8)
bar:SetFrameStrata("FULLSCREEN_DIALOG")
bar:SetBackdrop({
	bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
	edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
	tile = true, tileSize = 32, edgeSize = 24,
	insets = { left = 6, right = 6, top = 6, bottom = 6 },
})
bar:Hide()

local title = bar:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
title:SetPoint("CENTER", bar, "CENTER", 0, 4)
local dots = bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
dots:SetPoint("TOP", title, "BOTTOM", 0, -1)

local function Arrow(direction, point, x)
	local b = CreateFrame("Button", nil, bar)
	b:SetWidth(28)
	b:SetHeight(28)
	b:SetPoint(point, bar, point, x, 0)
	local path = direction < 0 and "Interface\\Buttons\\UI-SpellbookIcon-PrevPage" or "Interface\\Buttons\\UI-SpellbookIcon-NextPage"
	b:SetNormalTexture(path .. "-Up")
	b:SetPushedTexture(path .. "-Down")
	b:SetHighlightTexture("Interface\\Buttons\\UI-Common-MouseHilight", "ADD")
	b:SetScript("OnClick", function()
		if direction < 0 then ZeldaControls_SubscreenPrev() else ZeldaControls_SubscreenNext() end
	end)
	return b
end
Arrow(-1, "LEFT", 10)
Arrow(1, "RIGHT", -10)

local function ShowTitle()
	local p = PAGES[page]
	title:SetText(p and p.name or "")
	local s = ""
	for i = 1, table.getn(PAGES) do
		s = s .. (i == page and "|cffffd100o|r " or "|cff808080o|r ")
	end
	dots:SetText(s .. "   |cff808080Left / Right|r")
end

local function ClosePage(p)
	local f = p and PageFrame(p)
	if f and f:IsVisible() then
		if p.frame == "WorldMapFrame" or p.alt and f:GetName() == p.alt then
			p.open()                    -- the map toggles itself shut
		else
			HideUIPanel(f)
		end
	end
end

local function GoTo(newPage)
	switching = GetTime() + 0.4
	ClosePage(PAGES[page])
	page = newPage
	PAGES[page].open()
	ShowTitle()
end

local function BindArrows(on)
	if on then
		savedLeft = GetBindingAction and GetBindingAction("LEFT") or nil
		savedRight = GetBindingAction and GetBindingAction("RIGHT") or nil
		SetBinding("LEFT", "ZELDA_SUB_PREV")
		SetBinding("RIGHT", "ZELDA_SUB_NEXT")
	else
		SetBinding("LEFT", savedLeft ~= "" and savedLeft or nil)
		SetBinding("RIGHT", savedRight ~= "" and savedRight or nil)
	end
end

local function CloseSubscreen()
	if page == 0 then return end
	ClosePage(PAGES[page])
	page = 0
	bar:Hide()
	BindArrows(false)
end

function ZeldaControls_Subscreen()
	if page ~= 0 then
		CloseSubscreen()
		return
	end
	BindArrows(true)
	bar:Show()
	GoTo(1)
end

function ZeldaControls_SubscreenNext()
	if page == 0 then return end
	local n = table.getn(PAGES)
	GoTo(page >= n and 1 or page + 1)
end

function ZeldaControls_SubscreenPrev()
	if page == 0 then return end
	local n = table.getn(PAGES)
	GoTo(page <= 1 and n or page - 1)
end

-- Escape (or the screen's own close button) closes the whole Subscreen
bar:SetScript("OnUpdate", function()
	if page == 0 or GetTime() < switching then return end
	local f = PageFrame(PAGES[page])
	if not f or not f:IsVisible() then
		page = 0
		this:Hide()
		BindArrows(false)
	end
end)
