from gymnasium.envs.registration import register

register(
    id="PidogJump-v0",
    entry_point="pidog_jump_rl.envs.jump_env:PidogJumpEnv",
)
