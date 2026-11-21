from typing import Protocol


class SoundDirectionReader(Protocol):
    def isdetected(self) -> bool:
        ...

    def read(self) -> int:
        ...


class SoundDirectionSource(Protocol):
    ears: SoundDirectionReader


class SoundDirectionSensor:
    name = "sound_direction"

    def __init__(self, source: SoundDirectionSource) -> None:
        self._reader = source.ears

    def read(self) -> int:
        if not self._reader.isdetected():
            return -1
        return self._reader.read()
