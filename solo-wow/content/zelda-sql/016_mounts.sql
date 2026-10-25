-- Zelda of Warcraft: riding. Apprentice Riding costs 400 gold and a regular mount 50 gold; the
-- epic training and epic mounts stay as they are. The speeds are in 006_mastery (build_mastery.py):
-- regular mounts 150% faster, epic mounts 200%. Applied by the server at startup; safe to apply again.
UPDATE `npc_trainer` SET `spellcost` = 4000000 WHERE `spell` = 33389;
UPDATE `npc_trainer_template` SET `spellcost` = 4000000 WHERE `spell` = 33389;
UPDATE `item_template` SET `BuyPrice` = 500000
WHERE `class` = 15 AND `BuyPrice` > 0 AND `spellid_1` IN (458, 459, 468, 470, 471, 472, 578, 580, 581, 6648, 6653, 6654,
    6777, 6896, 6897, 6898, 6899, 8394, 8395, 8980, 10787, 10788, 10789, 10790, 10792, 10793, 10795, 10796, 10798, 10799,
    10873, 10969, 15780, 15781, 16058, 16059, 16060, 17453, 17454, 17455, 17456, 17458, 17462, 17463, 17464, 18363,
    18989, 18990, 25675, 25858);
