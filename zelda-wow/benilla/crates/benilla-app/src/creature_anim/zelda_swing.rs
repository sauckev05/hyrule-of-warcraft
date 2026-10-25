//! Zelda of Warcraft: the sword combo's three swings, as Link strikes. The ZeldaControls addon
//! calls `ZeldaSwingAnim(step, seconds)` as it sends a slash; the hero then plays exactly that
//! swing, at the rate that ends it in `seconds` (the server locks the sword for the same time and
//! sends its hits with `HITINFO_NOACTION`, so its own random swing does not cut the combo):
//!
//! 1. the right slash: the swing clip's variation whose sword hand crosses right to left;
//! 2. the left slash: the variation crossing left to right;
//! 3. the special strike, Heroic Strike's Special1H (Special2H with a two-hander);
//! 4. Berserker Stance's charged attack: the two-hander's leaping Special2H, whatever is held.
//!
//! Which variation crosses which way differs by model, so [`VARIATIONS`] names them per race and
//! gender, measured from the 1.12 character models (the right hand's sideways travel over the
//! 300 ms around each clip's `$CAH` impact key).

use bevy::prelude::*;

/// The swings the addon asked for since the driver last ran, `(step, seconds)`; the last wins.
/// The second field is the guard key: the shield raised, or the weapon held up to parry.
#[derive(Resource, Default)]
pub(crate) struct ZeldaSwingRequests(pub(crate) Vec<(u8, f32)>, pub(crate) ZeldaGuard);

/// Zelda of Warcraft: the guard key, from `ZeldaGuardAnim(kind, held)`. Pressing it plays the
/// guard clip once - ShieldBlock (24) with a shield (`kind` 1), the wielded weapon's parry (20-23)
/// without one (`kind` 2). While the key stays held the clip stops at its guard pose
/// ([`GUARD_POSE`] of the way through) and holds it; letting go plays the rest. A quick click
/// therefore plays the whole clip, as before.
#[derive(Default, Clone, Copy, Debug)]
pub(crate) struct ZeldaGuard {
    pub(crate) kind: u8,
    pub(crate) held: bool,
    /// A press not yet played.
    pub(crate) start: bool,
    /// The clip id playing for the guard, 0 when none.
    pub(crate) id: u16,
}

/// Where in the guard clip the pose holds while the key is down, as a fraction of its length: the
/// shield or blade is at its highest a little before the middle of the block and parry clips.
pub(super) const GUARD_POSE: f32 = 0.4;

/// The guard clip for `kind` with `main` (`(class, subclass)` of the armed main hand) in hand.
pub(super) fn guard_clip(kind: u8, main: Option<(u8, u8)>) -> u16 {
    if kind == 1 {
        return 24; // ShieldBlock
    }
    super::select::defense_anim(3, main).unwrap_or(21)
}

/// Per `(race, gender)`: the `(right, left)` variation index, in file order, of AttackUnarmed
/// (16), Attack1H (17), Attack2H (18) and Attack2HL (19).
const VARIATIONS: [(u8, u8, [(u8, u8); 4]); 16] = [
    (1, 0, [(0, 1), (0, 1), (0, 1), (0, 2)]), // HumanMale
    (1, 1, [(0, 1), (1, 0), (1, 0), (0, 2)]), // HumanFemale
    (2, 0, [(0, 1), (1, 0), (1, 0), (1, 0)]), // OrcMale
    (2, 1, [(0, 1), (1, 0), (1, 0), (0, 2)]), // OrcFemale
    (3, 0, [(0, 1), (0, 1), (0, 1), (1, 2)]), // DwarfMale
    (3, 1, [(0, 1), (0, 1), (1, 0), (0, 2)]), // DwarfFemale
    (4, 0, [(1, 0), (1, 0), (0, 1), (0, 1)]), // NightElfMale
    (4, 1, [(1, 0), (1, 0), (0, 1), (1, 2)]), // NightElfFemale
    (5, 0, [(0, 1), (2, 1), (2, 0), (2, 3)]), // ScourgeMale
    (5, 1, [(1, 0), (0, 1), (1, 0), (1, 0)]), // ScourgeFemale
    (6, 0, [(0, 1), (0, 1), (0, 1), (1, 0)]), // TaurenMale
    (6, 1, [(0, 1), (0, 1), (1, 0), (0, 1)]), // TaurenFemale
    (7, 0, [(0, 1), (0, 1), (0, 1), (0, 1)]), // GnomeMale
    (7, 1, [(0, 1), (1, 2), (0, 1), (0, 1)]), // GnomeFemale
    (8, 0, [(0, 1), (0, 1), (1, 0), (0, 1)]), // TrollMale
    (8, 1, [(1, 0), (1, 0), (1, 0), (1, 2)]), // TrollFemale
];

/// The combo swing `step` for a hero of `race`/`gender` holding `main` (`(class, subclass)` of the
/// armed main hand): the animation id and the variation index among that id's clips.
pub(super) fn combo_clip(step: u8, main: Option<(u8, u8)>, race: u8, gender: u8) -> (u16, usize) {
    let swing = super::select::swing_anim_main(main);
    if step >= 4 {
        return (58, 0); // the leaping two-handed strike, even with a one-hander
    }
    if step == 3 {
        // Heroic Strike's special strike; the play seam turns it unarmed with empty hands
        let special = if matches!(swing, 18 | 19) { 58 } else { 57 };
        return (special, 0);
    }
    let column = match swing {
        16 => Some(0),
        17 => Some(1),
        18 => Some(2),
        19 => Some(3),
        _ => None, // a dagger's stab has one variation
    };
    let (right, left) = column
        .and_then(|c| {
            VARIATIONS
                .iter()
                .find(|(r, g, _)| *r == race && *g == gender)
                .map(|(_, _, v)| v[c])
        })
        .unwrap_or((0, 1));
    (swing, usize::from(if step == 1 { right } else { left }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_combo_is_right_left_then_special() {
        let sword = Some((2, 7));
        assert_eq!(combo_clip(1, sword, 1, 0), (17, 0));
        assert_eq!(combo_clip(2, sword, 1, 0), (17, 1));
        assert_eq!(combo_clip(3, sword, 1, 0), (57, 0));
        assert_eq!(combo_clip(3, Some((2, 8)), 1, 0), (58, 0)); // two-handed sword
        assert_eq!(combo_clip(1, sword, 2, 0), (17, 1)); // an orc's arcs are the other way round
        assert_eq!(combo_clip(4, sword, 1, 0), (58, 0)); // the leap, one-hander or not
    }
}
