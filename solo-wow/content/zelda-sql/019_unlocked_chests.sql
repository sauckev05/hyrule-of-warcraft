-- Zelda of Warcraft: no locked chests. Every chest that needed a key (or lockpicking alone) opens like
-- an ordinary chest: its lock becomes the plain chest lock (Lock.dbc 57: open, treasure). Quest pillars,
-- runes, mounds and relics that take a key are left as they are. Applied by the server at startup; safe
-- to apply again.
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 2039 AND `type` = 3; -- Hidden Strongbox (was lock 46)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 3239 AND `type` = 3; -- Benedict's Chest (was lock 68)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 3642 AND `type` = 3; -- Kolkars' Booty (was lock 70)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 19022 AND `type` = 3; -- Worn Chest (was lock 89)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 19596 AND `type` = 3; -- Sleepers' Cache (was lock 94)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 19597 AND `type` = 3; -- Druids' Cache (was lock 94)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 19598 AND `type` = 3; -- Barrow Cache (was lock 94)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 19877 AND `type` = 3; -- Velinde's Locker (was lock 90)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 20691 AND `type` = 3; -- Cozzle's Footlocker (was lock 97)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 85563 AND `type` = 3; -- Dead-tooth's Strongbox (was lock 239)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 142184 AND `type` = 3; -- Captain's Chest (was lock 460)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 142477 AND `type` = 3; -- Thermaplugg's Safe (was lock 479)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 152608 AND `type` = 3; -- Kolkar's Booty (was lock 70)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 152618 AND `type` = 3; -- Kolkar's Booty (was lock 70)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 178464 AND `type` = 3; -- Dark Cleric Salem's Chest (was lock 1419)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 178504 AND `type` = 3; -- Stolen Chest (was lock 1439)
UPDATE `gameobject_template` SET `data0` = 57 WHERE `entry` = 184304 AND `type` = 3; -- Locked Chest (was lock 1620)
