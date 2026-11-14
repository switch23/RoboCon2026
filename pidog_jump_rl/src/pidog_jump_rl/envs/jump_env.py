"""MuJoCo jump task for a simplified PiDog quadruped."""

from pathlib import Path

import mujoco
import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box

MODEL_PATH = Path(__file__).resolve().parent.parent / "assets" / "pidog_jump.xml"
FOOT_GEOMS = ("fl_foot", "fr_foot", "bl_foot", "br_foot")

DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": 0,
    "distance": 0.8,
    "lookat": np.array((0.0, 0.0, 0.14)),
    "elevation": -20.0,
}


class PidogJumpEnv(MujocoEnv, utils.EzPickle):
    """Reward a vertical jump and a controlled, stable landing.

    The jump height is the torso's peak vertical displacement from its reset
    height. A successful episode requires all four feet on the floor,
    an upright/quiet posture, and 0.5 seconds of continuous stability after
    the jump.
    """

    metadata = {
        "render_modes": ["human", "rgb_array", "depth_array"],
        "render_fps": 50,
    }

    def __init__(
        self,
        minimum_jump_height: float = 0.04,
        landing_stable_time: float = 0.5,
        max_episode_steps: int = 600,
        reset_noise_scale: float = 0.01,
        **kwargs,
    ):
        utils.EzPickle.__init__(
            self,
            minimum_jump_height,
            landing_stable_time,
            max_episode_steps,
            reset_noise_scale,
            **kwargs,
        )
        self._minimum_jump_height = minimum_jump_height
        self._landing_stable_steps_required = max(
            1, round(landing_stable_time / (0.005 * 4))
        )
        self._max_episode_steps = max_episode_steps
        self._reset_noise_scale = reset_noise_scale
        self._start_z = 0.14
        self._elapsed_steps = 0
        self._airborne = False
        self._landing_started = False
        self._landing_contact_seen = False
        self._peak_height = 0.0
        self._apex_reached = False
        self._peak_symmetry_score = 0.0
        self._peak_joint_engagement = 0.0
        self._apex_quality = 0.0
        self._standing_joint_positions = np.zeros(8, dtype=np.float64)
        self._leg_joint_excursions = np.zeros(4, dtype=np.float64)
        self._joint_engagement_score = 0.0
        self._previous_vertical_velocity = 0.0
        self._stable_landing_steps = 0
        self._landing_quality = 0.0

        observation_space = Box(
            low=-np.inf,
            high=np.inf,
            shape=(41,),
            dtype=np.float64,
        )
        action_space = Box(
            low=-1.0,
            high=1.0,
            shape=(8,),
            dtype=np.float32,
        )
        MujocoEnv.__init__(
            self,
            str(MODEL_PATH),
            frame_skip=4,
            observation_space=observation_space,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )
        self.action_space = action_space

    def _initialize_simulation(self):
        xml_string = Path(self.fullpath).read_text(encoding="utf-8")
        model = mujoco.MjModel.from_xml_string(xml_string)
        model.vis.global_.offwidth = max(model.vis.global_.offwidth, self.width)
        model.vis.global_.offheight = max(model.vis.global_.offheight, self.height)
        return model, mujoco.MjData(model)

    def _foot_contacts(self) -> np.ndarray:
        floor_id = self.model.geom("floor").id
        foot_ids = [self.model.geom(name).id for name in FOOT_GEOMS]
        touching_geoms = set()
        for index in range(self.data.ncon):
            contact = self.data.contact[index]
            if contact.geom1 == floor_id:
                touching_geoms.add(contact.geom2)
            elif contact.geom2 == floor_id:
                touching_geoms.add(contact.geom1)
        return np.asarray(
            [geom_id in touching_geoms for geom_id in foot_ids],
            dtype=np.float64,
        )

    def _upright_score(self) -> float:
        quat = self.data.qpos[3:7]
        return float(1.0 - 2.0 * (quat[1] ** 2 + quat[2] ** 2))

    def _symmetry_score(self) -> float:
        joint_angles = self.data.qpos[7:]
        pair_differences = (
            abs(joint_angles[0] - joint_angles[2]),
            abs(joint_angles[1] - joint_angles[3]),
            abs(joint_angles[4] - joint_angles[6]),
            abs(joint_angles[5] - joint_angles[7]),
        )
        mean_difference = float(np.mean(pair_differences))
        return float(np.clip(1.0 - mean_difference / np.pi, 0.0, 1.0))

    def _joint_scores(self) -> tuple[float, float]:
        deviations = np.abs(self.data.qpos[7:] - self._standing_joint_positions)
        landing_stance = float(np.exp(-np.mean(deviations) / 0.5))
        return self._joint_engagement_score, landing_stance

    def _update_joint_engagement(self) -> None:
        deviations = np.abs(self.data.qpos[7:] - self._standing_joint_positions)
        per_leg_excursion = np.mean(
            np.clip(deviations.reshape(4, 2) / 0.6, 0.0, 1.0),
            axis=1,
        )
        self._leg_joint_excursions = np.maximum(
            self._leg_joint_excursions, per_leg_excursion
        )
        self._joint_engagement_score = float(np.min(self._leg_joint_excursions))

    def _get_obs(self) -> np.ndarray:
        qpos = self.data.qpos[7:]
        qvel = self.data.qvel[6:]
        torso_quat = self.data.sensor("torso_quat").data
        torso_linvel = self.data.sensor("torso_linvel").data
        torso_angvel = self.data.sensor("torso_angvel").data
        relative_height = self.data.qpos[2] - self._start_z
        return np.concatenate(
            [
                qpos,
                qvel,
                torso_quat,
                torso_linvel,
                torso_angvel,
                np.array([relative_height]),
                self._foot_contacts(),
                np.array(
                    [
                        float(self._airborne),
                        float(self._landing_started),
                        float(self._landing_contact_seen),
                        float(self._apex_reached),
                        self._peak_height,
                        self._peak_symmetry_score,
                        self._peak_joint_engagement,
                        self._apex_quality,
                        self._joint_engagement_score,
                        self._stable_landing_steps
                        / self._landing_stable_steps_required,
                    ]
                ),
            ]
        ).astype(np.float64)

    def reset_model(self) -> np.ndarray:
        noise = self._reset_noise_scale
        qpos = self.init_qpos.copy()
        qpos[7:] += self.np_random.uniform(-noise, noise, size=qpos[7:].shape)
        qvel = self.init_qvel + self.np_random.uniform(
            -noise, noise, size=self.init_qvel.shape
        )
        self.set_state(qpos, qvel)

        self._start_z = float(self.data.qpos[2])
        self._elapsed_steps = 0
        self._airborne = False
        self._landing_started = False
        self._landing_contact_seen = False
        self._peak_height = 0.0
        self._apex_reached = False
        self._peak_symmetry_score = 0.0
        self._peak_joint_engagement = 0.0
        self._apex_quality = 0.0
        self._previous_vertical_velocity = float(self.data.qvel[2])
        self._stable_landing_steps = 0
        self._landing_quality = 0.0
        self._standing_joint_positions = self.data.qpos[7:].copy()
        self._leg_joint_excursions = np.zeros(4, dtype=np.float64)
        self._joint_engagement_score = 0.0
        return self._get_obs()

    def step(self, action: np.ndarray):
        normalized_action = np.clip(np.asarray(action, dtype=np.float64), -1.0, 1.0)
        self.do_simulation(normalized_action * 90.0, self.frame_skip)
        self._elapsed_steps += 1

        torso_z = float(self.data.qpos[2])
        relative_height = torso_z - self._start_z
        vertical_velocity = float(self.data.qvel[2])
        feet_on_ground = self._foot_contacts()
        contact_count = int(np.sum(feet_on_ground))
        takeoff = (
            not self._airborne
            and contact_count <= 1
            and relative_height > 0.02
            and vertical_velocity > 0.05
        )
        if takeoff:
            self._airborne = True

        previous_peak = self._peak_height
        if self._airborne:
            self._peak_height = max(self._peak_height, relative_height, 0.0)

        upright = self._upright_score()
        upright_quality = float(np.clip((upright - 0.15) / 0.70, 0.0, 1.0))
        symmetry_score = self._symmetry_score()
        self._update_joint_engagement()
        joint_engagement_score, landing_stance_score = self._joint_scores()
        angular_speed = float(np.linalg.norm(self.data.qvel[3:6]))
        horizontal_speed = float(np.linalg.norm(self.data.qvel[:2]))
        joint_speed = float(np.mean(np.abs(self.data.qvel[6:])))
        apex_event = (
            self._airborne
            and not self._apex_reached
            and self._previous_vertical_velocity > 0.05
            and vertical_velocity <= 0.05
        )
        apex_reward = 0.0
        if apex_event:
            self._apex_reached = True
            self._peak_symmetry_score = symmetry_score
            self._peak_joint_engagement = joint_engagement_score
            angular_quality = float(np.exp(-angular_speed))
            self._apex_quality = (
                0.50 * symmetry_score
                + 0.25 * upright_quality
                + 0.10 * angular_quality
                + 0.15 * joint_engagement_score
            )
            apex_reward = 8.0 * self._apex_quality

        if self._airborne and vertical_velocity < -0.05:
            self._landing_started = True
        if self._landing_started and contact_count > 0:
            self._landing_contact_seen = True
        bounce_detected = (
            self._landing_contact_seen
            and contact_count == 0
            and vertical_velocity > 0.25
        )

        previous_landing_quality = self._landing_quality
        landing_quality = 0.0
        if self._landing_started:
            contact_quality = contact_count / len(FOOT_GEOMS)
            height_quality = float(np.exp(-abs(relative_height) / 0.08))
            vertical_speed_quality = float(np.exp(-abs(vertical_velocity) / 0.6))
            angular_speed_quality = float(np.exp(-angular_speed))
            horizontal_speed_quality = float(np.exp(-horizontal_speed / 0.5))
            landing_quality = (
                0.25 * contact_quality
                + 0.20 * upright_quality
                + 0.20 * symmetry_score
                + 0.15 * landing_stance_score
                + 0.08 * height_quality
                + 0.06 * vertical_speed_quality
                + 0.04 * angular_speed_quality
                + 0.02 * horizontal_speed_quality
            )

        previous_stability_progress = (
            self._stable_landing_steps / self._landing_stable_steps_required
        )
        stable_posture = (
            contact_count == len(FOOT_GEOMS)
            and self._start_z - 0.025 <= torso_z <= self._start_z + 0.05
            and upright > 0.85
            and abs(vertical_velocity) < 0.25
            and angular_speed < 0.6
            and horizontal_speed < 0.2
            and joint_speed < 0.6
        )
        if self._airborne and stable_posture:
            self._stable_landing_steps += 1
        else:
            self._stable_landing_steps = 0
        stability_progress = (
            self._stable_landing_steps / self._landing_stable_steps_required
        )
        self._landing_quality = landing_quality

        landed_stable = (
            self._stable_landing_steps >= self._landing_stable_steps_required
        )
        is_success = (
            landed_stable and self._peak_height >= self._minimum_jump_height
        )
        healthy = 0.07 < torso_z < 0.6 and upright > 0.15
        fallen = not healthy

        reward = (
            80.0 * (self._peak_height - previous_peak)
            + (1.0 if takeoff else 0.0)
            - 0.002 * float(np.mean(np.square(normalized_action)))
            - 0.02 * max(0.0, 1.0 - upright)
        )
        reward += 4.0 * (landing_quality - previous_landing_quality)
        reward += 2.0 * (stability_progress - previous_stability_progress)
        reward += apex_reward
        terminated = fallen or landed_stable or bounce_detected
        truncated = not terminated and self._elapsed_steps >= self._max_episode_steps
        if landed_stable:
            if is_success:
                reward += (
                    15.0
                    + 20.0 * self._peak_height
                    + 5.0 * symmetry_score
                    + 3.0 * self._peak_joint_engagement
                    + 2.0 * landing_stance_score
                )
            else:
                reward += (
                    5.0
                    + 2.0 * symmetry_score
                    + 2.0 * self._peak_joint_engagement
                    + 2.0 * landing_stance_score
                )
        elif bounce_detected:
            reward -= 15.0
        elif fallen:
            reward -= 10.0
        elif truncated:
            reward -= 5.0

        termination_reason = (
            "rebound"
            if bounce_detected
            else "fallen"
            if fallen
            else "stable_landing"
            if landed_stable
            else "timeout"
            if truncated
            else "running"
        )
        info = {
            "jump_height_m": self._peak_height,
            "torso_height_m": torso_z,
            "airborne": self._airborne,
            "landing_started": self._landing_started,
            "landing_contact_seen": self._landing_contact_seen,
            "bounce_detected": bounce_detected,
            "landing_quality": landing_quality,
            "symmetry_score": symmetry_score,
            "joint_engagement_score": joint_engagement_score,
            "landing_stance_score": landing_stance_score,
            "apex_reached": self._apex_reached,
            "apex_symmetry_score": self._peak_symmetry_score,
            "apex_joint_engagement_score": self._peak_joint_engagement,
            "apex_quality": self._apex_quality,
            "foot_contacts": contact_count,
            "landing_stable_steps": self._stable_landing_steps,
            "landing_stability_progress": stability_progress,
            "landed_stable": landed_stable,
            "is_success": is_success,
            "termination_reason": termination_reason,
        }
        self._previous_vertical_velocity = vertical_velocity
        if self.render_mode == "human":
            self.render()
        return self._get_obs(), float(reward), terminated, truncated, info
