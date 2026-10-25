-- Zelda of Warcraft: like Ocarina of Time's bottles, a hero carries at most 10 of each healing and
-- mana potion, in one stack of 10. Applied by the server at startup; safe to apply again.
UPDATE `item_template` SET `maxcount` = 10, `stackable` = 10
WHERE `class` = 0 AND `entry` IN (118, 858, 929, 1710, 3928, 4596, 13446, 18839, 17348, 17349,
                                  2455, 3385, 3827, 6149, 13443, 13444, 18841, 17351, 17352);
