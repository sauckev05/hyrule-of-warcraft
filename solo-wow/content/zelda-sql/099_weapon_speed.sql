-- Zelda of Warcraft: every melee weapon swings at one speed - one-handers (one-hand, main hand, off hand)
-- at 2.70, two-handers at 4.00 - with its damage per second unchanged, so a slower swing hits harder.
-- MySQL assigns left to right, so the damage columns read the old delay before it is replaced.
-- Last in the file order, after every file that adds weapons; applied at each server start (a
-- weapon already at its speed is left alone).
-- One-handed, main-hand and off-hand weapons: 2.70 speed, the damage per second kept (each hit scaled by the new speed over the old)
UPDATE `item_template` SET
    `dmg_min1` = ROUND(`dmg_min1` * 2700 / `delay`),
    `dmg_max1` = ROUND(`dmg_max1` * 2700 / `delay`),
    `dmg_min2` = ROUND(`dmg_min2` * 2700 / `delay`),
    `dmg_max2` = ROUND(`dmg_max2` * 2700 / `delay`),
    `dmg_min3` = ROUND(`dmg_min3` * 2700 / `delay`),
    `dmg_max3` = ROUND(`dmg_max3` * 2700 / `delay`),
    `dmg_min4` = ROUND(`dmg_min4` * 2700 / `delay`),
    `dmg_max4` = ROUND(`dmg_max4` * 2700 / `delay`),
    `dmg_min5` = ROUND(`dmg_min5` * 2700 / `delay`),
    `dmg_max5` = ROUND(`dmg_max5` * 2700 / `delay`),
    `delay` = 2700
WHERE `class` = 2 AND `InventoryType` IN (13,21,22) AND `delay` > 0 AND `delay` <> 2700;

-- Two-handed weapons: 4.00 speed, the damage per second kept (each hit scaled by the new speed over the old)
UPDATE `item_template` SET
    `dmg_min1` = ROUND(`dmg_min1` * 4000 / `delay`),
    `dmg_max1` = ROUND(`dmg_max1` * 4000 / `delay`),
    `dmg_min2` = ROUND(`dmg_min2` * 4000 / `delay`),
    `dmg_max2` = ROUND(`dmg_max2` * 4000 / `delay`),
    `dmg_min3` = ROUND(`dmg_min3` * 4000 / `delay`),
    `dmg_max3` = ROUND(`dmg_max3` * 4000 / `delay`),
    `dmg_min4` = ROUND(`dmg_min4` * 4000 / `delay`),
    `dmg_max4` = ROUND(`dmg_max4` * 4000 / `delay`),
    `dmg_min5` = ROUND(`dmg_min5` * 4000 / `delay`),
    `dmg_max5` = ROUND(`dmg_max5` * 4000 / `delay`),
    `delay` = 4000
WHERE `class` = 2 AND `InventoryType` IN (17) AND `delay` > 0 AND `delay` <> 4000;
