-- Zelda of Warcraft: the hero's look (build_hero.py). Human male players wear their own display
-- (17560, the young HumanMaleHero model, client patch-Z and the server's DBCs); its model info is
-- the stock human male's. Applied by the server at startup; safe to apply again.
DELETE FROM `creature_model_info` WHERE `modelid` = 17560;
INSERT INTO `creature_model_info` (`modelid`, `bounding_radius`, `combat_reach`, `SpeedWalk`, `SpeedRun`, `gender`,
    `modelid_other_gender`, `modelid_other_team`)
SELECT 17560, `bounding_radius`, `combat_reach`, `SpeedWalk`, `SpeedRun`, `gender`, 50, `modelid_other_team`
FROM `creature_model_info` WHERE `modelid` = 49;
