#pragma once

// "Hyrule of Warcraft" - World of Warcraft style RPG systems layered on top of Ocarina of Time.
// C-callable entry points used by the decomp source (collision + player damage).

#ifdef __cplusplus
extern "C" {
#endif

// Called from CollisionCheck_ApplyDamage. Returns the (possibly modified) damage an actor takes.
float Azeroth_ModifyOutgoingDamage(void* play, void* collider, float damage);

// Called from the player damage path. healthChange is negative for damage (16 units = 1 heart).
int Azeroth_ModifyIncomingDamage(void* play, int healthChange);

#ifdef __cplusplus
}
#endif
