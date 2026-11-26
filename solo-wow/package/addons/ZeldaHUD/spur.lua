-- Zelda HUD: Epona's spurs. Riding, key 5 spurs the mount on (the server's ZeldaSpur): each spur 20%
-- faster, up to five, one dropping every 3 sec without a new one. Like Ocarina of Time's carrots, five
-- red circles show them while he rides, just above the enemy charge-up bar (castbar.lua) over the
-- target's health bar (targetbar.lua); the server sends a hidden "ZSPUR:n" line
-- (n spurs, -1 when he is not riding), and says it again every few seconds while he rides.

local COUNT, SIZE, GAP = 5, 22, 8

local frame = CreateFrame("Frame", "ZeldaSpurFrame", UIParent)
frame:SetWidth(COUNT * SIZE + (COUNT - 1) * GAP)
frame:SetHeight(SIZE)
-- the charge-up bar sits 28 px over the target bar's anchor and is 10 px tall with a 3 px border:
-- the circles go a little above its top edge
if ZeldaTargetAnchor then
	frame:SetPoint("BOTTOM", ZeldaTargetAnchor, "TOP", 0, 58)
else
	frame:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 175)
end
frame:SetFrameStrata("MEDIUM")
frame:Hide()

local circles = {}
for i = 1, COUNT do
	local t = frame:CreateTexture(nil, "ARTWORK")
	t:SetTexture("Interface\\AddOns\\ZeldaHUD\\media\\spur")
	t:SetWidth(SIZE)
	t:SetHeight(SIZE)
	t:SetPoint("LEFT", frame, "LEFT", (i - 1) * (SIZE + GAP), 0)
	circles[i] = t
end

local function Show(n)
	if not n or n < 0 then
		frame:Hide()
		return
	end
	for i = 1, COUNT do
		if i <= n then
			circles[i]:SetVertexColor(0.95, 0.12, 0.1)     -- a spur: red
			circles[i]:SetAlpha(1)
		else
			circles[i]:SetVertexColor(0.25, 0.25, 0.25)    -- not yet: a dark empty circle
			circles[i]:SetAlpha(0.55)
		end
	end
	frame:Show()
end

local events = CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_SYSTEM")
events:SetScript("OnEvent", function()
	if arg1 and string.sub(arg1, 1, 6) == "ZSPUR:" then
		local _, _, n = string.find(arg1, "^ZSPUR:(%-?%d+)")
		Show(tonumber(n))
	end
end)
