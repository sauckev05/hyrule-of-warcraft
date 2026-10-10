//! Zelda of Warcraft: Z-targeting, as in Ocarina of Time. While the lock is on, the hero turns to
//! face the selected unit and the camera swings in behind him to frame it; A and D strafe instead
//! of turning ([`super::input::move_axes`] reads [`Player::zelda_locked`]), so walking sideways
//! circles the target. The lock is driven by the `ZeldaLock(mode)` script global, which the
//! ZeldaControls addon binds to a key, and lets go when the target is gone, dead-far, or deselected.

use bevy::prelude::*;

use super::camera::FlyCam;
use super::follow::{bearing_to, steer, wrap_pi};
use super::state::Player;
use crate::target::Selection;

/// Past this many yards the lock lets go, like Ocarina's lock breaking when the enemy runs off.
const LOCK_RANGE: f32 = 45.0;
/// How fast the hero turns onto the target, radians per second (much faster than a keyboard turn).
const FACE_RATE: f32 = 4.0 * std::f32::consts::PI;
/// How quickly the camera settles behind the hero, as a fraction of the gap closed per second.
const CAMERA_CATCH_UP: f32 = 8.0;

/// The Z-targeting state; [`ZeldaLock::request`] queues a change from the script.
#[derive(Resource, Default)]
pub(crate) struct ZeldaLock {
    on: bool,
    pending: Option<i32>,
}

impl ZeldaLock {
    /// `0` off, `1` on, anything else toggles.
    pub(crate) fn request(&mut self, mode: i32) {
        self.pending = Some(mode);
    }
}

pub(super) fn plugin(app: &mut App) {
    app.init_resource::<ZeldaLock>().add_systems(
        Update,
        steer_zelda_lock
            .in_set(benilla_world::schedule::WorldStage::Input)
            .before(super::control)
            .in_set(crate::char_select::InWorldGated),
    );
}

fn steer_zelda_lock(
    time: Res<Time>,
    mut lock: ResMut<ZeldaLock>,
    mut player: ResMut<Player>,
    selection: Res<Selection>,
    transforms: Query<&Transform, Without<FlyCam>>,
    mut cams: Query<&mut FlyCam>,
) {
    let target_pos = selection
        .target
        .and_then(|e| transforms.get(e).ok())
        .map(|t| t.translation);

    if let Some(mode) = lock.pending.take() {
        let want = match mode {
            0 => false,
            1 => true,
            _ => !lock.on,
        };
        if want && target_pos.is_none() {
            info!("zelda: Z-target — nothing selected to lock onto");
        } else if want != lock.on {
            info!("zelda: Z-target {}", if want { "on" } else { "off" });
        }
        lock.on = want && target_pos.is_some();
    }

    let usable = player.active && !player.detached && !player.control_lost && !player.server_riding;
    let Some(target) = target_pos.filter(|_| lock.on && usable) else {
        if lock.on && target_pos.is_none() {
            info!("zelda: Z-target released — the target is gone");
        }
        lock.on = lock.on && usable && target_pos.is_some();
        player.zelda_locked = false;
        return;
    };

    let delta = target - player.pos;
    let flat = Vec3::new(delta.x, 0.0, delta.z);
    let distance = flat.length();
    if distance > LOCK_RANGE {
        info!("zelda: Z-target released — out of range ({distance:.0} yd)");
        lock.on = false;
        player.zelda_locked = false;
        return;
    }
    player.zelda_locked = true;
    if distance < 0.3 {
        return; // standing on top of it: no meaningful bearing
    }

    let dt = time.delta_secs();
    let bearing = bearing_to(flat);
    player.face_yaw = wrap_pi(steer(player.face_yaw, bearing, FACE_RATE, dt));

    // Swing the camera in behind the hero, framing the target past his shoulder.
    let catch_up = (CAMERA_CATCH_UP * dt).min(1.0);
    for mut cam in &mut cams {
        let gap = wrap_pi(player.face_yaw - cam.yaw);
        cam.yaw = wrap_pi(cam.yaw + gap * catch_up);
    }
}
