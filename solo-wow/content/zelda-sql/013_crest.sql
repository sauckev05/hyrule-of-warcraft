-- Zelda of Warcraft: crests without a guild. The tabard vendors' option is just "Create crest.",
-- and the Guild Tabard is the Universal Tabard (250 gold), which shows the crest its wearer
-- designed (the core keeps a guildless hero's crest; the client paints it on this tabard).
-- Applied by the server at startup; safe to apply again.
UPDATE `gossip_menu_option` SET `option_text` = 'Create crest.', `option_broadcast_text` = 0 WHERE `option_id` = 11;
UPDATE `item_template` SET `name` = 'Universal Tabard', `BuyPrice` = 2500000, `SellPrice` = 625000,
  `description` = 'Shows the crest you design at a tabard vendor.' WHERE `entry` = 5976;
