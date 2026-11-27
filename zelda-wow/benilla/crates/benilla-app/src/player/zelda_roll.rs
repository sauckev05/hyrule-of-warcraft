//! Zelda of Warcraft: the dodge roll's tumble. The 1.12 character models have no roll clip, so the
//! hero's whole body turns once through the air instead: head over heels for the forward roll,
//! heels over head for the backflip, a cartwheel to the side for the side rolls. A model that has
//! the roll's own clips (the human male, from patch-Z: solo-wow/tools/port_roll.py) plays those
//! for the forward roll and the backflip instead, at the rate that fits the arc.
//!
//! The ZeldaControls addon calls `ZeldaRollAnim(kind)` as it asks the server for the dodge
//! (`.zroll f|l|r`, `.zflip`). The side rolls and the backflip are the server's knockbacks, or
//! nothing (on cooldown, in the air, stunned), so those requests only arm the tumble: it starts
//! when the push does within [`ARM_SECS`]. The forward roll is the client's own dash along the
//! ground, like a run at roll speed (the controller runs [`super::state::ZeldaDash`]), so it
//! starts at once. Each roll tumbles over the same window the server makes every blow a dodge
//! for (`ZeldaDodge`, ZeldaCommands.cpp).

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
/// the backflip (the young hero's attack exertions, patch-Z's copy of `SoundEntries` 2941 in his
/// own voice, build_hero.py).
const ROLL_SOUNDS: [&str; 4] = [
    "Sound\\Character\\ZeldaHero\\HumanMaleFinal\\HumanMaleMainAttackC.wav",
    "Sound\\Character\\ZeldaHero\\HumanMaleFinal\\HumanMaleMainAttackB.wav",
    "Sound\\Character\\ZeldaHero\\HumanMaleFinal\\HumanMaleMainAttackB.wav",
    "Sound\\Character\\ZeldaHero\\HumanMaleFinal\\HumanMaleMainAttackA.wav",
];
/// The forward roll's reach along the ground (yd), over its [`ROLL_SECS`].
const FORWARD_ROLL_YARDS: f32 = 14.0;
/// The double jump's front flip clip length (s): port_flip.py's 733 ms.
const FLIP_SECS: f32 = 0.733;
/// The rolls' shared cooldown, a little over the server's 0.9 s (`DODGE_COOLDOWN_MS`), so a roll the
/// client runs is one the server grants the dodge for.
const DODGE_COOLDOWN_SECS: f32 = 0.95;
/// The spurs' cooldown, the server's `ZELDA_SPUR_COOLDOWN_MS` (one red circle every 1.5 s at most),
/// so the rider strikes the mount only on a spur the server grants.
const SPUR_COOLDOWN_SECS: f32 = 1.5;
/// How long the rider's blow on the mount plays (s): AttackUnarmed's 1 s, a little quicker.
const MOUNT_PUNCH_SECS: f32 = 0.7;
/// The fist's loudness: the mount's moan beside it (its own attack file, e.g. mHorseAttack at
/// SoundEntries volume 0.7) peaks near -13 dB, the unarmed hit files near -4 dB at full volume, so
/// the hit plays about 9 dB down to sit at the moan's level.
const MOUNT_PUNCH_GAIN: f32 = 0.35;
/// The fist landing on the mount with each spur, in turn (`SoundEntries` 1014 "Unarmed_Generic").
const MOUNT_PUNCH_SOUNDS: [&str; 3] = [
    "Sound\\Item\\Weapons\\Unarmed\\UnarmedAttackMediumA.wav",
    "Sound\\Item\\Weapons\\Unarmed\\UnarmedAttackMediumB.wav",
    "Sound\\Item\\Weapons\\Unarmed\\UnarmedAttackMediumC.wav",
];
/// The body turns about this share of its head height above the feet, near the middle.
const PIVOT_SHARE: f32 = 0.5;

/// The roll asked for this frame, from the script ([`crate::script_calls`]).
#[derive(Resource, Default)]
pub(crate) struct ZeldaRollRequest {
    pub(crate) pending: Option<u8>,
    /// The press came from key 5: in the saddle it spurs the mount, and the rider strikes it.
    pub(crate) key5: bool,
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
    /// When the last roll started (elapsed secs), for the forward roll's own cooldown.
    last_start: f32,
    /// When the rider last struck the mount (elapsed secs), and how many times so far (which hit
    /// sound comes next).
    last_spur: Option<f32>,
    spurs: usize,
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
    mut player: ResMut<Player>,
    mut knocks: MessageReader<crate::net::KnockBackMessage>,
    mut request: ResMut<ZeldaRollRequest>,
    mut state: ResMut<ZeldaRollState>,
    mut swings: Option<ResMut<crate::creature_anim::ZeldaSwingRequests>>,
    mut sounds: MessageWriter<crate::sound::ZeldaRollSound>,
    body: Query<Option<&benilla_assets::ModelAnimations>, (With<Embodied>, Without<FlyCam>)>,
    own: Query<&crate::net::ObjectStore, (With<Embodied>, Without<FlyCam>)>,
) {
    let now = time.elapsed_secs();
    // in the saddle the forward roll's key spurs the mount (the server's ZeldaSpur): no dash, which
    // would hold the horse to roll speed for the dash's time
    let mounted = own.single().is_ok_and(|s| s.0.unit_mount_display_id() != 0);
    let mut forward_now = false;
    // key 5 in the saddle spurs the mount (the server's ZeldaSpur, which wants it on the move): the
    // rider strikes it with his fist, on the upper body over the riding pose, and the blow lands
    // the sword in the air is the plunge: script_calls turns the swing into it while this says the
    // hero is airborne, and asks here for the dive, which the mover runs to the ground
    if let Some(sw) = swings.as_deref_mut() {
        let airborne = player.airborne_since.is_some() && !player.swimming && !mounted && !player.server_riding;
        sw.2 = airborne;
        if std::mem::take(&mut sw.3) && airborne {
            player.zelda_plunge = true;
            sounds.write(crate::sound::ZeldaRollSound(ROLL_SOUNDS[3], 1.0));
            trace(|| "plunge".to_string());
        }
    }
    let key5 = std::mem::take(&mut request.key5);
    if key5 && mounted && !player.server_riding {
        use crate::creature_anim::move_flags as f;
        let moving = player.move_flags & (f::FORWARD | f::BACKWARD | f::STRAFE_LEFT | f::STRAFE_RIGHT) != 0;
        let ready = state.last_spur.is_none_or(|t| now - t >= SPUR_COOLDOWN_SECS);
        if moving && ready {
            state.last_spur = Some(now);
            if let Some(swings) = swings.as_deref_mut() {
                swings.0.push((8, MOUNT_PUNCH_SECS));
            }
            sounds.write(crate::sound::ZeldaRollSound(MOUNT_PUNCH_SOUNDS[state.spurs % MOUNT_PUNCH_SOUNDS.len()], MOUNT_PUNCH_GAIN));
            state.spurs += 1;
        }
        trace(|| format!("spur key5 moving={moving} ready={ready}"));
    }
    if let Some(kind) = request.pending.take() {
        trace(|| format!("asked kind={kind} rolling={}", state.rolling.is_some()));
        if kind == 1 {
            // the forward roll is ours to run: on the ground, off cooldown, a dash along it (the
            // server only makes every blow a dodge for its time, `ZeldaDodge`)
            let ready = state.rolling.is_none()
                && now - state.last_start >= DODGE_COOLDOWN_SECS
                && player.airborne_since.is_none()
                && !player.swimming
                && !player.server_riding
                && !mounted;
            if ready {
                let lasts = ROLL_SECS[0];
                player.zelda_dash = Some(super::state::ZeldaDash {
                    yaw: player.face_yaw,
                    speed: FORWARD_ROLL_YARDS / lasts,
                    until: now + lasts,
                });
                state.armed = Some((kind, now));
                forward_now = true;
            } else {
                trace(|| format!("refused kind=1: rolling={} since_last={:.3} airborne={} mounted={mounted}",
                                 state.rolling.is_some(), now - state.last_start, player.airborne_since.is_some()));
            }
        } else if state.rolling.is_none() {
            state.armed = Some((kind, now));
        }
    }
    // the double jump's front flip (the mover launched it): the model's own clip when it has one
    if player.zelda_flip_at.take().is_some() {
        let has_clip = body.single().ok().flatten().is_some_and(|a| {
            a.clips.iter().any(|c| c.anim_id == crate::creature_anim::FLIP_CLIP)
        });
        if let (true, Some(swings)) = (has_clip, swings.as_deref_mut()) {
            swings.0.push((7, FLIP_SECS));
        }
        sounds.write(crate::sound::ZeldaRollSound(ROLL_SOUNDS[0], 1.0));
        trace(|| format!("double jump flip own_clip={has_clip}"));
    }
    // the server's push for the asked roll: the turn starts with it
    let pushed = knocks.read().count() > 0;
    if let Some((kind, asked)) = state.armed {
        // the forward roll starts at once, with its dash
        let started = if forward_now || pushed {
            Some(now)
        } else {
            player.airborne_since.filter(|&since| since >= asked - 0.05)
        };
        match started {
            // the push landed: the arc's time in the air is the turn's
            Some(since) => {
                let lasts = ROLL_SECS[usize::from(kind.clamp(1, 4) - 1)];
                sounds.write(crate::sound::ZeldaRollSound(ROLL_SOUNDS[usize::from(kind.clamp(1, 4) - 1)], 1.0));
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
                trace(|| format!("start kind={kind} pushed={pushed} dash={} lasts={lasts:.3} own_clip={has_clip} body={}",
                                 player.zelda_dash.is_some(), body.single().is_ok()));
                state.rolling = Some((kind, since, lasts, has_clip));
                state.last_start = since;
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
