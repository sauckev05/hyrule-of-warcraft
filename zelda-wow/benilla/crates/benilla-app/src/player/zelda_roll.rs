//! Zelda of Warcraft: the dodge roll's tumble. The 1.12 character models have no roll clip, so the
//! hero's whole body turns once through the air instead: head over heels for the forward roll,
//! heels over head for the backflip, a cartwheel to the side for the side rolls. A model that has
//! the roll's own clips (the human male, from patch-Z: solo-wow/tools/port_roll.py) plays those
//! for the forward roll and the backflip instead, at the rate that fits the arc.
//!
//! The ZeldaControls addon calls `ZeldaRollAnim(kind)` as it asks the server for the dodge
//! (`.zroll f|l|r`, `.zflip`). The server answers with a knockback, or not at all (on cooldown, in
//! the air, stunned), so the request only arms the tumble: it starts when the body actually leaves
//! the ground within [`ARM_SECS`], and turns once over the arc's time in the air, which is the
//! same window the server makes every blow a dodge for (`ZeldaDodge`, ZeldaCommands.cpp).

use std::f32::consts::TAU;

use bevy::prelude::*;

use super::camera::{model_pivot_height, CameraPivot, FlyCam};
use super::state::Player;
use crate::net::Embodied;

/// How long an asked-for roll waits for the server's push before it is dropped (s).
const ARM_SECS: f32 = 0.5;
/// How long each roll tumbles (s), by kind: the forward roll, the side rolls and the backflip. The
/// server makes every blow a dodge for the same time (`HandleZeldaRollCommand`,
/// `HandleZeldaFlipCommand`); the forward roll ends a little after its arc lands.
const ROLL_SECS: [f32; 4] = [0.65, 0.36, 0.36, 0.726];
/// The backflip's own clip is its turn up to the landing (port_roll.py keeps 500 ms of 600): it
/// plays at the pace the whole 600 ms had over the arc, and the arc's last moment is the fall pose.
const BACKFLIP_CLIP_SHARE: f32 = 500.0 / 600.0;
/// The hero's grunt as each roll leaves the ground, by kind: the forward roll, the side rolls and
/// the backflip (the human male's attack exertions, `SoundEntries` 2941).
const ROLL_SOUNDS: [&str; 4] = [
    "Sound\\Character\\PlayerExertions\\HumanMaleFinal\\HumanMaleMainAttackC.wav",
    "Sound\\Character\\PlayerExertions\\HumanMaleFinal\\HumanMaleMainAttackB.wav",
    "Sound\\Character\\PlayerExertions\\HumanMaleFinal\\HumanMaleMainAttackB.wav",
    "Sound\\Character\\PlayerExertions\\HumanMaleFinal\\HumanMaleMainAttackA.wav",
];
/// The body turns about this share of its head height above the feet, near the middle.
const PIVOT_SHARE: f32 = 0.5;

/// The roll asked for this frame, from the script ([`crate::script_calls`]).
#[derive(Resource, Default)]
pub(crate) struct ZeldaRollRequest {
    pub(crate) pending: Option<u8>,
}

/// The tumble in progress, or the one waiting for the push.
#[derive(Resource, Default)]
pub(super) struct ZeldaRollState {
    /// `(kind, asked at)`: waiting for the body to leave the ground.
    armed: Option<(u8, f32)>,
    /// `(kind, started at, lasts, its own clip plays)`: turning.
    rolling: Option<(u8, f32, f32, bool)>,
    /// What the turn last wrote onto the body, and the upright pose it turned: a frame `control`
    /// skipped still holds the written pose, which must not be turned again.
    written: Option<(Transform, Transform)>,
}

fn trace(msg: impl FnOnce() -> String) {
    if benilla_assets::trace::enabled_for("zroll") {
        benilla_assets::trace::line("zroll", &msg());
    }
}

/// The clip a model of its own plays for the roll `kind` (the human male's, from patch-Z), and the
/// combo step that asks the animation driver for it: the forward roll and the backflip.
fn own_clip(kind: u8) -> Option<(u16, u8)> {
    match kind {
        1 => Some((crate::creature_anim::ROLL_CLIP, 5)),
        4 => Some((crate::creature_anim::BACKFLIP_CLIP, 6)),
        _ => None,
    }
}

pub(super) fn plugin(app: &mut App) {
    app.init_resource::<ZeldaRollRequest>()
        .init_resource::<ZeldaRollState>()
        .add_systems(
            Update,
            tumble
                .in_set(benilla_world::schedule::WorldStage::Input)
                .after(super::control)
                .run_if(not(resource_exists::<crate::run_mode::CaptureMode>))
                .in_set(crate::char_select::InWorldGated),
        )
        // the turn itself goes on last, after every Update writer of the body, just before the
        // transforms propagate to the model
        .add_systems(
            PostUpdate,
            turn_body
                .before(bevy::transform::TransformSystems::Propagate)
                .run_if(not(resource_exists::<crate::run_mode::CaptureMode>)),
        );
}

/// The turn about `kind`'s axis, in the model's own frame (forward −Z, left −X, up +Y), `angle`
/// of the way round: a positive turn about +X lifts the nose (the swim pitch), one about +Z tips
/// the head to the left.
fn spin(kind: u8, angle: f32) -> Quat {
    match kind {
        2 => Quat::from_rotation_z(angle),  // cartwheel to the left
        3 => Quat::from_rotation_z(-angle), // and to the right
        4 => Quat::from_rotation_x(angle),  // backflip: heels over head
        _ => Quat::from_rotation_x(-angle), // forward roll: head over heels
    }
}

/// Ease in and out, so the tuck and the landing read slower than the middle of the turn.
fn ease(p: f32) -> f32 {
    let p = p.clamp(0.0, 1.0);
    p * p * (3.0 - 2.0 * p)
}

#[allow(clippy::type_complexity)]
fn tumble(
    time: Res<Time>,
    player: Res<Player>,
    mut knocks: MessageReader<crate::net::KnockBackMessage>,
    mut request: ResMut<ZeldaRollRequest>,
    mut state: ResMut<ZeldaRollState>,
    mut swings: Option<ResMut<crate::creature_anim::ZeldaSwingRequests>>,
    mut sounds: MessageWriter<crate::sound::ZeldaRollSound>,
    body: Query<Option<&benilla_assets::ModelAnimations>, (With<Embodied>, Without<FlyCam>)>,
) {
    let now = time.elapsed_secs();
    if let Some(kind) = request.pending.take() {
        trace(|| format!("asked kind={kind} rolling={}", state.rolling.is_some()));
        if state.rolling.is_none() {
            state.armed = Some((kind, now));
        }
    }
    // the server's push for the asked roll: the turn starts with it
    let pushed = knocks.read().count() > 0;
    if let Some((kind, asked)) = state.armed {
        let started = if pushed {
            Some(now)
        } else {
            player.airborne_since.filter(|&since| since >= asked - 0.05)
        };
        match started {
            // the push landed: the arc's time in the air is the turn's
            Some(since) => {
                let lasts = ROLL_SECS[usize::from(kind.clamp(1, 4) - 1)];
                sounds.write(crate::sound::ZeldaRollSound(ROLL_SOUNDS[usize::from(kind.clamp(1, 4) - 1)]));
                // a model with the roll's own clip plays it over the arc; the rest turn whole
                let has_clip = own_clip(kind).is_some_and(|(clip, _)| {
                    body.single()
                        .ok()
                        .flatten()
                        .is_some_and(|a| a.clips.iter().any(|c| c.anim_id == clip))
                });
                if let (true, Some((_, step)), Some(swings)) = (has_clip, own_clip(kind), swings.as_deref_mut()) {
                    let clip_secs = if kind == 4 { lasts * BACKFLIP_CLIP_SHARE } else { lasts };
                    swings.0.push((step, clip_secs));
                }
                trace(|| format!("start kind={kind} pushed={pushed} lasts={lasts:.3} own_clip={has_clip} body={}",
                                 body.single().is_ok()));
                state.rolling = Some((kind, since, lasts, has_clip));
                state.armed = None;
            }
            None if now - asked > ARM_SECS => {
                trace(|| format!("dropped kind={kind}: no push in {ARM_SECS} s"));
                state.armed = None;
            }
            None => {}
        }
    }
    if let Some((_, start, lasts, _)) = state.rolling {
        // done when its time is up, landed or not (the forward roll finishes on the ground)
        if (now - start) / lasts >= 1.0 {
            trace(|| format!("end after {:.3} s", now - start));
            state.rolling = None;
        }
    }
}

/// Turns the body through the roll, last thing before the transforms propagate.
#[allow(clippy::type_complexity)]
fn turn_body(
    time: Res<Time>,
    mut state: ResMut<ZeldaRollState>,
    mut body: Query<
        (&mut Transform, Option<&CameraPivot>, Option<&crate::net::NetEntity>),
        (With<Embodied>, Without<FlyCam>),
    >,
) {
    let Some((kind, start, lasts, own)) = state.rolling else {
        state.written = None;
        return;
    };
    // the clip turns the body itself
    if own {
        return;
    }
    let p = (time.elapsed_secs() - start) / lasts;
    let Ok((mut t, pivot, net)) = body.single_mut() else {
        return;
    };
    // a frame whose Update did not set the body upright again still holds the last turn
    if let Some((written, upright)) = state.written {
        if *t == written {
            *t = upright;
        }
    }
    let upright = *t;
    let height = pivot.map_or(1.0, |p| model_pivot_height(p, net.map_or(1.0, |n| n.scale), false));
    let up = Vec3::Y * height * PIVOT_SHARE;
    // `control` has just set the body upright at its feet: turn it about its middle instead
    let base = t.rotation;
    let turn = spin(kind, ease(p) * TAU);
    let world_turn = base * turn * base.inverse();
    let center = t.translation + up;
    t.translation = center - world_turn * up;
    t.rotation = base * turn;
    state.written = Some((*t, upright));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_forward_roll_tips_the_head_forward() {
        // a quarter of the way round, the head (+Y) points along the model's forward (−Z)
        let head = spin(1, TAU / 4.0) * Vec3::Y;
        assert!((head - Vec3::NEG_Z).length() < 1e-5, "{head}");
        // the backflip takes it backward
        let head = spin(4, TAU / 4.0) * Vec3::Y;
        assert!((head - Vec3::Z).length() < 1e-5, "{head}");
    }

    #[test]
    fn the_side_rolls_tip_toward_their_side() {
        // the model's left is −X (WoW +Y)
        let head = spin(2, TAU / 4.0) * Vec3::Y;
        assert!((head - Vec3::NEG_X).length() < 1e-5, "{head}");
        let head = spin(3, TAU / 4.0) * Vec3::Y;
        assert!((head - Vec3::X).length() < 1e-5, "{head}");
    }

    #[test]
    fn the_turn_is_whole_and_eased() {
        assert_eq!(ease(0.0), 0.0);
        assert_eq!(ease(1.0), 1.0);
        assert!((ease(0.5) - 0.5).abs() < 1e-6);
    }
}
