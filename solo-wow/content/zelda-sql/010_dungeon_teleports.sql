-- Zelda of Warcraft: the innkeepers' "Tell me about dungeons I could explore" list (gossip menu
-- 50238) sends you to the chosen dungeon's meeting stone instead of opening its page. Each spot is
-- a few yards from the stone, checked against the server's walkable ground (mmaps), facing it.
-- The list keeps its level conditions. Applied by the server at startup; safe to apply again.
DELETE FROM `dbscripts_on_gossip` WHERE `id` BETWEEN 900700 AND 900718;
INSERT INTO `dbscripts_on_gossip` (`id`,`delay`,`priority`,`command`,`datalong`,`datalong2`,`datalong3`,`buddy_entry`,`search_radius`,`data_flags`,`dataint`,`dataint2`,`dataint3`,`dataint4`,`datafloat`,`x`,`y`,`z`,`o`,`speed`,`condition_id`,`comments`) VALUES
(900700,0,0,6,1,0,0,0,0,0,0,0,0,0,0,1815.6,-4400.75,-16.34,5.83,0,0,'Zelda: teleport to the Ragefire meeting stone'),
(900701,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-11091.33,1563.3,50.57,5.45,0,0,'Zelda: teleport to the Deadmines meeting stone'),
(900702,0,0,6,1,0,0,0,0,0,0,0,0,0,0,-796.26,-2135.14,94.31,6.13,0,0,'Zelda: teleport to the Wailing Caverns meeting stone'),
(900703,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-247.44,1514.0,76.97,4.77,0,0,'Zelda: teleport to the Shadowfang Keep meeting stone'),
(900704,0,0,6,1,0,0,0,0,0,0,0,0,0,0,4075.15,817.21,4.54,4.71,0,0,'Zelda: teleport to the Blackfathom Deeps meeting stone'),
(900705,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-8813.49,797.75,99.75,0.1,0,0,'Zelda: teleport to the Stormwind Stockade meeting stone'),
(900706,0,0,6,1,0,0,0,0,0,0,0,0,0,0,-4468.66,-1807.51,88.54,0.14,0,0,'Zelda: teleport to the Razorfen Kraul meeting stone'),
(900707,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-5204.74,608.97,412.86,5.14,0,0,'Zelda: teleport to the Gnomeregan meeting stone'),
(900708,0,0,6,0,0,0,0,0,0,0,0,0,0,0,2658.22,-677.21,112.19,3.57,0,0,'Zelda: teleport to the Scarlet Monastery meeting stone'),
(900709,0,0,6,1,0,0,0,0,0,0,0,0,0,0,-4376.46,-1952.57,90.8,5.86,0,0,'Zelda: teleport to the Razorfen Downs meeting stone'),
(900710,0,0,6,1,0,0,0,0,0,0,0,0,0,0,-1415.92,2814.69,113.04,2.15,0,0,'Zelda: teleport to the Maraudon meeting stone'),
(900711,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-6119.44,-3299.9,259.67,0.12,0,0,'Zelda: teleport to the Uldaman meeting stone'),
(900712,0,0,6,1,0,0,0,0,0,0,0,0,0,0,-6828.11,-2877.07,10.6,1.95,0,0,'Zelda: teleport to the Zul''Farrak meeting stone'),
(900713,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-7593.02,-1140.69,261.68,0.38,0,0,'Zelda: teleport to the Blackrock Depths meeting stone'),
(900714,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-10459.0,-3805.04,18.59,5.12,0,0,'Zelda: teleport to the Sunken Temple meeting stone'),
(900715,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-7628.15,-1227.59,233.71,0.37,0,0,'Zelda: teleport to the Blackrock Spire meeting stone'),
(900716,0,0,6,1,0,0,0,0,0,0,0,0,0,0,-4430.07,1411.37,133.04,0.54,0,0,'Zelda: teleport to the Dire Maul meeting stone'),
(900717,0,0,6,0,0,0,0,0,0,0,0,0,0,0,3369.47,-3379.32,145.57,6.18,0,0,'Zelda: teleport to the Stratholme meeting stone'),
(900718,0,0,6,0,0,0,0,0,0,0,0,0,0,0,1231.81,-2574.73,91.6,1.43,0,0,'Zelda: teleport to the Scholomance meeting stone');
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900700 WHERE `menu_id` = 50238 AND `id` = 0; -- Ragefire
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900701 WHERE `menu_id` = 50238 AND `id` = 1; -- Deadmines
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900702 WHERE `menu_id` = 50238 AND `id` = 2; -- Wailing Caverns
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900703 WHERE `menu_id` = 50238 AND `id` = 3; -- Shadowfang Keep
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900704 WHERE `menu_id` = 50238 AND `id` = 4; -- Blackfathom Deeps
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900705 WHERE `menu_id` = 50238 AND `id` = 5; -- Stormwind Stockade
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900706 WHERE `menu_id` = 50238 AND `id` = 6; -- Razorfen Kraul
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900707 WHERE `menu_id` = 50238 AND `id` = 7; -- Gnomeregan
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900708 WHERE `menu_id` = 50238 AND `id` = 8; -- Scarlet Monastery
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900709 WHERE `menu_id` = 50238 AND `id` = 9; -- Razorfen Downs
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900710 WHERE `menu_id` = 50238 AND `id` = 10; -- Maraudon
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900711 WHERE `menu_id` = 50238 AND `id` = 11; -- Uldaman
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900712 WHERE `menu_id` = 50238 AND `id` = 12; -- Zul'Farrak
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900713 WHERE `menu_id` = 50238 AND `id` = 13; -- Blackrock Depths
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900714 WHERE `menu_id` = 50238 AND `id` = 14; -- Sunken Temple
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900715 WHERE `menu_id` = 50238 AND `id` = 15; -- Blackrock Spire
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900716 WHERE `menu_id` = 50238 AND `id` = 16; -- Dire Maul
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900717 WHERE `menu_id` = 50238 AND `id` = 17; -- Stratholme
UPDATE `gossip_menu_option` SET `option_icon` = 2, `action_menu_id` = -1, `action_script_id` = 900718 WHERE `menu_id` = 50238 AND `id` = 18; -- Scholomance
-- Wailing Caverns (now level 28-33) and Blackfathom Deeps (now 30-35) are listed for the levels
-- they have become: 26-35 and 28-37
DELETE FROM `conditions` WHERE `condition_entry` BETWEEN 900010 AND 900015;
INSERT INTO `conditions` (`condition_entry`,`type`,`value1`,`value2`,`value3`,`value4`,`flags`,`comments`) VALUES
(900010,15,26,1,0,0,0,'Zelda: Player Level >= 26'),
(900011,15,35,2,0,0,0,'Zelda: Player Level <= 35'),
(900012,-1,900010,900011,0,0,0,'Zelda: Wailing Caverns in the dungeon list (level 26-35)'),
(900013,15,28,1,0,0,0,'Zelda: Player Level >= 28'),
(900014,15,37,2,0,0,0,'Zelda: Player Level <= 37'),
(900015,-1,900013,900014,0,0,0,'Zelda: Blackfathom Deeps in the dungeon list (level 28-37)');
UPDATE `gossip_menu_option` SET `condition_id` = 900012 WHERE `menu_id` = 50238 AND `id` = 2; -- Wailing Caverns
UPDATE `gossip_menu_option` SET `condition_id` = 900015 WHERE `menu_id` = 50238 AND `id` = 4; -- Blackfathom Deeps
