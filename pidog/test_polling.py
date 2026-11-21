import unittest
from threading import Event

from polling import PollingLoop, SensorSnapshot


class FakeSensor:
    def __init__(self, name: str, value: object) -> None:
        self.name = name
        self.value = value
        self.read_count = 0

    def read(self) -> object:
        self.read_count += 1
        return self.value


class PollingLoopTests(unittest.TestCase):
    def test_poll_once_reads_sensors_and_publishes_snapshot(self) -> None:
        sensor = FakeSensor("distance", 42.0)
        snapshots = []
        loop = PollingLoop([sensor], snapshots.append)

        snapshot = loop.poll_once()

        self.assertEqual(sensor.read_count, 1)
        self.assertEqual(snapshot.values["distance"], 42.0)
        self.assertIs(snapshots[0], snapshot)
        self.assertIsInstance(snapshot, SensorSnapshot)
        with self.assertRaises(TypeError):
            snapshot.values["distance"] = 10.0

    def test_run_stops_when_handler_sets_stop_event(self) -> None:
        sensor = FakeSensor("touch", "N")
        stop_event = Event()
        snapshots = []

        def stop_after_two_polls(snapshot: SensorSnapshot) -> None:
            snapshots.append(snapshot)
            if len(snapshots) == 2:
                stop_event.set()

        loop = PollingLoop(
            [sensor],
            stop_after_two_polls,
            interval_seconds=0.001,
        )
        loop.run(stop_event)

        self.assertEqual(sensor.read_count, 2)

    def test_rejects_duplicate_sensor_names(self) -> None:
        with self.assertRaises(ValueError):
            PollingLoop(
                [FakeSensor("same", 1), FakeSensor("same", 2)],
                lambda snapshot: None,
            )

    def test_rejects_non_positive_interval(self) -> None:
        with self.assertRaises(ValueError):
            PollingLoop([], lambda snapshot: None, interval_seconds=0)


if __name__ == "__main__":
    unittest.main()
