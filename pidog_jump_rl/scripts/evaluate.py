"""Evaluate jump height and stable-landing success for a trained PPO policy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO

import pidog_jump_rl  # noqa: F401


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=str, default="models/pidog_jump_ppo_v6.zip")
    parser.add_argument("--episodes", type=int, default=20)
    args = parser.parse_args()

    env = gym.make("PidogJump-v0")
    model = PPO.load(args.model)
    heights = []
    apex_symmetries = []
    apex_joint_engagements = []
    successes = 0
    stable_landings = 0
    try:
        for episode in range(args.episodes):
            observation, _info = env.reset()
            terminated = truncated = False
            info = {}
            while not (terminated or truncated):
                action, _state = model.predict(observation, deterministic=True)
                observation, _reward, terminated, truncated, info = env.step(action)

            height = float(info.get("jump_height_m", 0.0))
            apex_symmetry = float(info.get("apex_symmetry_score", 0.0))
            apex_joint_engagement = float(
                info.get("apex_joint_engagement_score", 0.0)
            )
            landing_stance = float(info.get("landing_stance_score", 0.0))
            stable = bool(info.get("landed_stable", False))
            success = bool(info.get("is_success", False))
            heights.append(height)
            apex_symmetries.append(apex_symmetry)
            apex_joint_engagements.append(apex_joint_engagement)
            stable_landings += int(stable)
            successes += int(success)
            print(
                f"Episode {episode + 1}: "
                f"height={height:.3f} m, "
                f"apex_symmetry={apex_symmetry:.2f}, "
                f"apex_joint_use={apex_joint_engagement:.2f}, "
                f"landing_stance={landing_stance:.2f}, "
                f"contacts={info.get('foot_contacts', 0)}/4, "
                f"stable_steps={info.get('landing_stable_steps', 0)}, "
                f"stable_landing={stable}, success={success}"
                f", bounce={info.get('bounce_detected', False)}"
                f", ended_by={info.get('termination_reason', 'unknown')}"
            )
    finally:
        env.close()

    print(
        f"Summary: mean_height={np.mean(heights):.3f} m, "
        f"mean_apex_symmetry={np.mean(apex_symmetries):.2f}, "
        f"mean_apex_joint_use={np.mean(apex_joint_engagements):.2f}, "
        f"stable_landings={stable_landings}/{args.episodes}, "
        f"successes={successes}/{args.episodes}"
    )


if __name__ == "__main__":
    main()
