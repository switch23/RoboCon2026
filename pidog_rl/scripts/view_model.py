"""Load the PiDog MJCF model and visualize it interactively with MuJoCo Viewer.

Usage:
    uv run scripts/view_model.py
    uv run scripts/view_model.py --action-sweep   # cycle actuators to sanity-check joints
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent.parent / "src" / "pidog_rl" / "assets" / "pidog.xml"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--action-sweep",
        action="store_true",
        help="Continuously sweep all actuators with a sine wave to verify joint limits.",
    )
    args = parser.parse_args()

    model = mujoco.MjModel.from_xml_string(MODEL_PATH.read_text(encoding="utf-8"))
    data = mujoco.MjData(model)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        start = time.time()
        while viewer.is_running():
            step_start = time.time()

            if args.action_sweep:
                t = time.time() - start
                data.ctrl[:] = 30.0 * np.sin(2.0 * np.pi * 0.5 * t + np.arange(model.nu))

            mujoco.mj_step(model, data)
            viewer.sync()

            time_until_next_step = model.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)


if __name__ == "__main__":
    main()
