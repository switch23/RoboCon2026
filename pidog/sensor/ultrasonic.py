from typing import Protocol


class DistanceSource(Protocol):
    def read_distance(self) -> float:
        ...


class UltrasonicSensor:
    name = "ultrasonic"

    def __init__(self, source: DistanceSource) -> None:
        self._source = source

    def read(self) -> float:
        return float(self._source.read_distance())
