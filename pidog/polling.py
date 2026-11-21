from dataclasses import dataclass
from time import monotonic
from threading import Event
from types import MappingProxyType
from typing import Callable, Mapping, Sequence

from sensor.base import Sensor

@dataclass(frozen=True)
class SensorSnapshot:
    timestamp: float
    values: Mapping[str, object]


class PollingLoop:
    def __init__(
        self,
        sensors: Sequence[Sensor],
        on_snapshot: Callable[[SensorSnapshot], None],
        interval_seconds: float = 0.05,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be greater than zero")

        names = [sensor.name for sensor in sensors]
        if len(names) != len(set(names)):
            raise ValueError("sensor names must be unique")

        self._sensors = tuple(sensors)
        self._on_snapshot = on_snapshot
        self._interval_seconds = interval_seconds

    def poll_once(self) -> SensorSnapshot:
        values = {sensor.name: sensor.read() for sensor in self._sensors}
        snapshot = SensorSnapshot(
            timestamp=monotonic(),
            values=MappingProxyType(values),
        )
        self._on_snapshot(snapshot)
        return snapshot

    def run(self, stop_event: Event) -> None:
        while not stop_event.is_set():
            started_at = monotonic()
            self.poll_once()
            remaining = self._interval_seconds - (monotonic() - started_at)
            if remaining > 0:
                stop_event.wait(remaining)
