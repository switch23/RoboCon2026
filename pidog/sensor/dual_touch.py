from typing import Protocol


class TouchReader(Protocol):
    def read(self) -> str:
        ...


class TouchSource(Protocol):
    dual_touch: TouchReader


class DualTouchSensor:
    name = "dual_touch"

    def __init__(self, source: TouchSource) -> None:
        self._reader = source.dual_touch

    def read(self) -> str:
        return self._reader.read()
