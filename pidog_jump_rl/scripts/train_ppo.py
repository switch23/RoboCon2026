"""Train PPO on the PidogJump-v0 MuJoCo task."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

import pidog_jump_rl  # noqa: F401

PROJECT_DIR = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timesteps", type=int, default=2_000_000)
    parser.add_argument("--n-envs", type=int, default=8)
    parser.add_argument("--run-name", type=str, default="pidog_jump_ppo_v6")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    env = make_vec_env("PidogJump-v0", n_envs=args.n_envs, seed=args.seed)
    models_dir = PROJECT_DIR / "models"
    runs_dir = PROJECT_DIR / "runs"
    models_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        device=device,
        tensorboard_log=str(runs_dir),
        n_steps=max(64, 2048 // args.n_envs),
        batch_size=256,
        learning_rate=1e-4,
        n_epochs=3,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        target_kl=0.02,
        seed=args.seed,
    )
    try:
        model.learn(
            total_timesteps=args.timesteps,
            tb_log_name=args.run_name,
            progress_bar=True,
        )
        model_path = models_dir / f"{args.run_name}.zip"
        model.save(str(model_path))
        print(f"Saved trained model to {model_path}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
