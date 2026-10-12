"""Replay a trained PPO policy on Pidog-v0 with the MuJoCo viewer.

Usage:
    uv run scripts/play.py --model models/pidog_ppo.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure "src" is importable even if the project's editable install (.pth file)
# could not be picked up, which can happen when the repository path contains
# non-ASCII characters (a known Windows `site`-module encoding limitation).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import gymnasium as gym
from stable_baselines3 import PPO

import pidog_rl  # noqa: F401  (registers the "Pidog-v0" environment)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=str, default="models/pidog_ppo.zip")
    parser.add_argument("--episodes", type=int, default=5)
    args = parser.parse_args()

    env = gym.make("Pidog-v0", render_mode="human")
    model = PPO.load(args.model)

    for episode in range(args.episodes):
        obs, _info = env.reset()
        terminated = truncated = False
        episode_reward = 0.0
        while not (terminated or truncated):
            action, _state = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _info = env.step(action)
            episode_reward += float(reward)
        print(f"Episode {episode + 1}: reward={episode_reward:.2f}")

    env.close()


if __name__ == "__main__":
    main()
