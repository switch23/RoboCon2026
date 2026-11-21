from dataclasses import dataclass
from typing import Protocol, Sequence, Tuple


class ImuSource(Protocol):
    accData: Sequence[float]
    gyroData: Sequence[float]


@dataclass(frozen=True)
class ImuReading:
    acceleration: Tuple[float, float, float]
    gyroscope: Tuple[float, float, float]


class ImuSensor:
    name = "imu"

    def __init__(self, source: ImuSource) -> None:
        self._source = source

    def read(self) -> ImuReading:
        acceleration = tuple(float(value) for value in self._source.accData)
        gyroscope = tuple(float(value) for value in self._source.gyroData)
        if len(acceleration) != 3 or len(gyroscope) != 3:
            raise ValueError("IMU acceleration and gyroscope readings must have 3 axes")
        return ImuReading(
            acceleration=acceleration,
            gyroscope=gyroscope,
        )
