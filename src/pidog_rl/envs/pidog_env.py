"""Gymnasium environment wrapping the simplified PiDog MuJoCo model."""

from pathlib import Path

import mujoco
import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box

MODEL_PATH = Path(__file__).resolve().parent.parent / "assets" / "pidog.xml"

DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": 0,
    "distance": 0.8,
    "lookat": np.array((0.0, 0.0, 0.1)),
    "elevation": -20.0,
}


class PidogEnv(MujocoEnv, utils.EzPickle):
    """Quadruped walking task for the PiDog robot.

    Observation: joint positions/velocities, torso orientation and
    linear/angular velocity (from the MJCF <sensor> block).
    Action: target angles (deg) for the 8 leg servos (position actuators).
    Reward: forward (+x) velocity, minus energy and orientation penalties,
    plus a small per-step survival bonus. Episode ends early if the robot
    falls (torso too low or tilted too much).
    """

    metadata = {
        "render_modes": ["human", "rgb_array", "depth_array"],
        "render_fps": 50,
    }

    def __init__(
        self,
        forward_reward_weight: float = 1.0,
        ctrl_cost_weight: float = 0.01,
        healthy_reward: float = 0.5,
        healthy_z_range: tuple[float, float] = (0.05, 0.3),
        healthy_pitch_roll_limit: float = 0.9,
        reset_noise_scale: float = 0.05,
        **kwargs,
    ):
        utils.EzPickle.__init__(
            self,
            forward_reward_weight,
            ctrl_cost_weight,
            healthy_reward,
            healthy_z_range,
            healthy_pitch_roll_limit,
            reset_noise_scale,
            **kwargs,
        )

        self._forward_reward_weight = forward_reward_weight
        self._ctrl_cost_weight = ctrl_cost_weight
        self._healthy_reward = healthy_reward
        self._healthy_z_range = healthy_z_range
        self._healthy_pitch_roll_limit = healthy_pitch_roll_limit
        self._reset_noise_scale = reset_noise_scale

        # 8 joint positions + 8 joint velocities + 4 (quat) + 3 (linvel) + 3 (angvel) + 1 (height)
        observation_space = Box(low=-np.inf, high=np.inf, shape=(27,), dtype=np.float64)

        MujocoEnv.__init__(
            self,
            str(MODEL_PATH),
            frame_skip=4,
            observation_space=observation_space,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )

    def _initialize_simulation(self):
        # Load from the raw XML text (rather than mujoco.MjModel.from_xml_path)
        # because MuJoCo's native file loader cannot open paths containing
        # non-ASCII characters on some Windows locale configurations, which
        # breaks if the repository lives under a non-ASCII directory name.
        xml_string = Path(self.fullpath).read_text(encoding="utf-8")
        model = mujoco.MjModel.from_xml_string(xml_string)
        model.vis.global_.offwidth = max(model.vis.global_.offwidth, self.width)
        model.vis.global_.offheight = max(model.vis.global_.offheight, self.height)
        data = mujoco.MjData(model)
        return model, data

    def _get_obs(self) -> np.ndarray:
        qpos = self.data.qpos.flatten()[7:]  # skip free joint (xyz + quat)
        qvel = self.data.qvel.flatten()[6:]  # skip free joint velocities
        torso_quat = self.data.sensor("torso_quat").data
        torso_linvel = self.data.sensor("torso_linvel").data
        torso_angvel = self.data.sensor("torso_angvel").data
        torso_height = np.array([self.data.qpos[2]])
        return np.concatenate(
            [qpos, qvel, torso_quat, torso_linvel, torso_angvel, torso_height]
        ).astype(np.float64)

    @property
    def is_healthy(self) -> bool:
        z = self.data.qpos[2]
        min_z, max_z = self._healthy_z_range
        quat = self.data.sensor("torso_quat").data
        # Tilt estimate: 1 - 2*(qx^2 + qy^2) is the cosine of the up-vector tilt.
        upright = 1.0 - 2.0 * (quat[1] ** 2 + quat[2] ** 2)
        return bool(min_z < z < max_z and upright > self._healthy_pitch_roll_limit)

    def step(self, action: np.ndarray):
        x_before = self.data.qpos[0]
        self.do_simulation(action, self.frame_skip)
        x_after = self.data.qpos[0]

        forward_velocity = (x_after - x_before) / self.dt
        forward_reward = self._forward_reward_weight * forward_velocity
        ctrl_cost = self._ctrl_cost_weight * float(np.sum(np.square(action)))
        healthy_reward = self._healthy_reward if self.is_healthy else 0.0

        reward = forward_reward + healthy_reward - ctrl_cost
        terminated = not self.is_healthy
        observation = self._get_obs()

        info = {
            "forward_reward": forward_reward,
            "ctrl_cost": ctrl_cost,
            "healthy_reward": healthy_reward,
            "x_position": x_after,
        }

        if self.render_mode == "human":
            self.render()

        return observation, reward, terminated, False, info

    def reset_model(self) -> np.ndarray:
        noise = self._reset_noise_scale
        qpos = self.init_qpos + self.np_random.uniform(
            low=-noise, high=noise, size=self.model.nq
        )
        qvel = self.init_qvel + self.np_random.uniform(
            low=-noise, high=noise, size=self.model.nv
        )
        self.set_state(qpos, qvel)
        return self._get_obs()
