from gymnasium.envs.registration import register

from .pidog_env import PidogEnv

register(
    id="Pidog-v0",
    entry_point="pidog_rl.envs.pidog_env:PidogEnv",
    max_episode_steps=1000,
)

__all__ = ["PidogEnv"]
