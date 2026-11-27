-- Zelda of Warcraft: a way out of a battleground at any time. The stock scoreboard (WorldStateFrame)
-- only shows its "Return to World" button once the battle has a winner; here it stays shown while
-- you are inside a battleground, reading "Leave Battleground" until there is a winner.

local function InBattleground()
    for i = 1, MAX_BATTLEFIELD_QUEUES or 3 do
        local status = GetBattlefieldStatus(i)
        if status == "active" then
            return true
        end
    end
    return false
end

local function ZeldaHUD_BGLeave_Update()
    local button = WorldStateScoreFrameLeaveButton
    if not button then
        return
    end
    if GetBattlefieldWinner() then
        button:SetText(RETURN_TO_WORLD)              -- the stock end-of-battle button, as it was
        return
    end
    if InBattleground() then
        button:SetText("Leave Battleground")
        button:Show()
    end
end

local original = WorldStateScoreFrame_Update
if original then
    WorldStateScoreFrame_Update = function()
        original()
        ZeldaHUD_BGLeave_Update()
    end
end
