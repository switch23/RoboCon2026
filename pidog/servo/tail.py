from typing import Protocol, Sequence


class TailDevice(Protocol):
    def tail_move(
        self,
        target_angles: Sequence[Sequence[float]],
        immediately: bool = True,
        speed: int = 50,
    ) -> None:
        ...

    def tail_stop(self) -> None:
        ...


class TailServo:
    def __init__(self, device: TailDevice) -> None:
        self._device = device

    def move(
        self,
        angles: Sequence[float],
        speed: int = 50,
        immediately: bool = True,
    ) -> None:
        if not angles:
            raise ValueError("at least one tail angle is required")
        self._device.tail_move(
            [[angle] for angle in angles],
            immediately=immediately,
            speed=speed,
        )

    def stop(self) -> None:
        self._device.tail_stop()
