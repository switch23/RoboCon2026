from typing import Protocol, Sequence


class HeadDevice(Protocol):
    def head_move(
        self,
        target_yrps: Sequence[Sequence[float]],
        immediately: bool = True,
        speed: int = 50,
    ) -> None:
        ...

    def head_stop(self) -> None:
        ...


class HeadServo:
    def __init__(self, device: HeadDevice) -> None:
        self._device = device

    def move(
        self,
        yaw: float,
        roll: float,
        pitch: float,
        speed: int = 50,
        immediately: bool = True,
    ) -> None:
        self._device.head_move(
            [[yaw, roll, pitch]],
            immediately=immediately,
            speed=speed,
        )

    def stop(self) -> None:
        self._device.head_stop()
