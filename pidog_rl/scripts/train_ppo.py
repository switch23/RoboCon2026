"""Train PPO (PyTorch backend, via Stable-Baselines3) on the Pidog-v0 task.

Usage:
    uv run scripts/train_ppo.py --timesteps 2_000_000
    uv run tensorboard --logdir runs
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
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecMonitor

import pidog_rl  # noqa: F401  (registers the "Pidog-v0" environment)

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timesteps", type=int, default=2_000_000)
    parser.add_argument("--n-envs", type=int, default=8)
    parser.add_argument("--run-name", type=str, default="pidog_ppo")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    vec_env = make_vec_env("Pidog-v0", n_envs=args.n_envs, seed=args.seed)
    vec_env = VecMonitor(vec_env)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        device=device,
        tensorboard_log=str(RUNS_DIR),
        n_steps=2048 // args.n_envs if args.n_envs <= 2048 else 1,
        batch_size=256,
        learning_rate=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        seed=args.seed,
    )

    model.learn(total_timesteps=args.timesteps, tb_log_name=args.run_name, progress_bar=True)

    save_path = MODELS_DIR / f"{args.run_name}.zip"
    model.save(str(save_path))
    print(f"Saved trained model to {save_path}")


if __name__ == "__main__":
    main()
