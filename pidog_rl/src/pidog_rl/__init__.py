def main() -> None:
    print("Hello from pidog-rl!")


# Registers the "Pidog-v0" Gymnasium environment as a side effect of importing
# the package, so `gymnasium.make("Pidog-v0")` works right after `import pidog_rl`.
from pidog_rl import envs as _envs  # noqa: E402,F401

