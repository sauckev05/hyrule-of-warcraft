-- Zelda of Warcraft: the Silk & Lace boutique and its hosiery are retired. This removes the
-- boutique vendor (190660), her spawns and stock, and the hosiery items (190900-190949).
-- (Copies players still had are removed from the characters database at server start.)
DELETE FROM `npc_vendor` WHERE `entry` = 190660 OR `item` BETWEEN 190900 AND 190949;
DELETE FROM `creature` WHERE `id` = 190660;
DELETE FROM `creature_template` WHERE `Entry` = 190660;
DELETE FROM `item_template` WHERE `entry` BETWEEN 190900 AND 190949;
