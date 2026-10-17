-- Zelda of Warcraft: two Kirin Tor portal mages. One stands in the basement of the Wizard's Sanctum
-- (the Stormwind Mage Tower, by the mage trainers) and sends you to the Kirin Tor camp outside sealed
-- Dalaran (Alterac Mountains, beside Archmage Ansirem Runeweaver); the other stands there and sends
-- you back. Applied by the server at startup; safe to apply again.
DELETE FROM `creature` WHERE `id` IN (190670, 190671);
DELETE FROM `creature_template` WHERE `Entry` IN (190670, 190671);
DELETE FROM `gossip_menu` WHERE `entry` IN (64101, 64102);
DELETE FROM `gossip_menu_option` WHERE `menu_id` IN (64101, 64102);
DELETE FROM `npc_text` WHERE `ID` IN (900101, 900102);
DELETE FROM `dbscripts_on_gossip` WHERE `id` IN (900670, 900671);

INSERT INTO `creature_template` (`Entry`,`Name`,`SubName`,`MinLevel`,`MaxLevel`,`DisplayId1`,`DisplayIdProbability1`,`Faction`,`Scale`,`CreatureType`,`InhabitType`,`RegenerateStats`,`NpcFlags`,`UnitFlags`,`SpeedWalk`,`SpeedRun`,`UnitClass`,`Rank`,`HealthMultiplier`,`PowerMultiplier`,`DamageMultiplier`,`ArmorMultiplier`,`ExperienceMultiplier`,`MeleeBaseAttackTime`,`RangedBaseAttackTime`,`EquipmentTemplateId`,`GossipMenuId`,`AIName`,`ScriptName`) VALUES
(190670,'Archmage Elandra','Portal to Dalaran',60,60,3292,100,35,1.0,7,3,3,1,768,1.0,1.14286,8,0,1.0,1.0,1.0,1.0,0,2000,2000,0,64101,'',''),
(190671,'Magister Aldwyn','Portal to Stormwind',60,60,1484,100,35,1.0,7,3,3,1,768,1.0,1.14286,8,0,1.0,1.0,1.0,1.0,0,2000,2000,0,64102,'','');

INSERT INTO `creature` (`guid`,`id`,`map`,`spawnMask`,`position_x`,`position_y`,`position_z`,`orientation`,`spawntimesecsmin`,`spawntimesecsmax`,`spawndist`,`MovementType`) VALUES
(9102001,190670,0,1,-8996.0,856.0,29.71,1.95,300,300,0,0),
(9102002,190671,0,1,34.9,253.3,42.3,3.21,300,300,0,0);

INSERT INTO `npc_text` (`ID`,`text0_0`,`text0_1`,`lang0`,`prob0`,`em0_0`,`em0_1`) VALUES
(900101,'The Kirin Tor keep a watch outside the barrier of Dalaran, $N. I can send you to their camp in the Alterac Mountains.','The Kirin Tor keep a watch outside the barrier of Dalaran, $N. I can send you to their camp in the Alterac Mountains.',0,1,0,1),
(900102,'Behind that shimmering wall the city of Dalaran sleeps, sealed away. When you have seen enough, I can send you back to the Wizard''s Sanctum in Stormwind.','Behind that shimmering wall the city of Dalaran sleeps, sealed away. When you have seen enough, I can send you back to the Wizard''s Sanctum in Stormwind.',0,1,0,1);

INSERT INTO `gossip_menu` (`entry`,`text_id`,`script_id`,`condition_id`) VALUES
(64101,900101,0,0),
(64102,900102,0,0);

INSERT INTO `gossip_menu_option` (`menu_id`,`id`,`option_icon`,`option_text`,`option_broadcast_text`,`option_id`,`npc_option_npcflag`,`action_menu_id`,`action_poi_id`,`action_script_id`,`box_coded`,`box_money`,`box_text`,`box_broadcast_text`,`condition_id`) VALUES
(64101,0,2,'Send me to Dalaran.',0,1,1,-1,0,900670,0,0,'',0,0),
(64102,0,2,'Send me back to Stormwind.',0,1,1,-1,0,900671,0,0,'',0,0);

INSERT INTO `dbscripts_on_gossip` (`id`,`delay`,`priority`,`command`,`datalong`,`datalong2`,`datalong3`,`buddy_entry`,`search_radius`,`data_flags`,`dataint`,`dataint2`,`dataint3`,`dataint4`,`datafloat`,`x`,`y`,`z`,`o`,`speed`,`condition_id`,`comments`) VALUES
(900670,0,0,6,0,0,0,0,0,0,0,0,0,0,0,30.5,255.5,42.8,0.06,0,0,'Zelda: teleport to the Kirin Tor camp outside Dalaran'),
(900671,0,0,6,0,0,0,0,0,0,0,0,0,0,0,-8998.5,860.5,30.2,5.1,0,0,'Zelda: teleport to the Wizard''s Sanctum, Stormwind');
