from typing import Protocol, Sequence


class LegsDevice(Protocol):
    def legs_move(
        self,
        target_angles: Sequence[Sequence[float]],
        immediately: bool = True,
        speed: int = 50,
    ) -> None:
        ...

    def legs_stop(self) -> None:
        ...

class LegsServo:
    def __init__(self, device: LegsDevice) -> None:
        self._device = device

    def move(
        self,
        frames: Sequence[Sequence[float]],
        speed: int = 50,
        immediately: bool = True,
    ) -> None:
        if not frames:
            raise ValueError("at least one leg frame is required")
        if any(len(frame) != 8 for frame in frames):
            raise ValueError("each leg frame must contain 8 servo angles")
        self._device.legs_move(
            [list(frame) for frame in frames],
            immediately=immediately,
            speed=speed,
        )

    def stop(self) -> None:
        self._device.legs_stop()
