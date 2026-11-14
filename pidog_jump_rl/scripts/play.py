"""Replay a trained jumping policy in the MuJoCo viewer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import gymnasium as gym
from stable_baselines3 import PPO

import pidog_jump_rl  # noqa: F401


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=str, default="models/pidog_jump_ppo_v6.zip")
    parser.add_argument("--episodes", type=int, default=3)
    args = parser.parse_args()

    env = gym.make("PidogJump-v0", render_mode="human")
    model = PPO.load(args.model)
    try:
        for episode in range(args.episodes):
            observation, _info = env.reset()
            terminated = truncated = False
            info = {}
            while not (terminated or truncated):
                action, _state = model.predict(observation, deterministic=True)
                observation, _reward, terminated, truncated, info = env.step(action)
            print(
                f"Episode {episode + 1}: "
                f"height={info.get('jump_height_m', 0.0):.3f} m, "
                f"apex_symmetry={info.get('apex_symmetry_score', 0.0):.2f}, "
                f"apex_joint_use={info.get('apex_joint_engagement_score', 0.0):.2f}, "
                f"landing_stance={info.get('landing_stance_score', 0.0):.2f}, "
                f"contacts={info.get('foot_contacts', 0)}/4, "
                f"stable_landing={info.get('landed_stable', False)}, "
                f"success={info.get('is_success', False)}, "
                f"ended_by={info.get('termination_reason', 'unknown')}"
            )
    finally:
        env.close()


if __name__ == "__main__":
    main()
