from typing import Protocol


class Sensor(Protocol):
    name: str

    def read(self) -> object:
        ...
