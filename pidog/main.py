from threading import Event
from time import monotonic

from polling import PollingLoop, SensorSnapshot
from sensor import (
    DualTouchSensor,
    ImuSensor,
    SoundDirectionSensor,
    UltrasonicSensor,
)

POLL_INTERVAL_SECONDS = 0.05
REPORT_INTERVAL_SECONDS = 1.0


def main() -> None:
    from pidog import Pidog

    dog = Pidog()
    sensors = (
        UltrasonicSensor(dog),
        DualTouchSensor(dog),
        ImuSensor(dog),
        SoundDirectionSensor(dog),
    )
    last_reported_at = 0.0

    def report(snapshot: SensorSnapshot) -> None:
        nonlocal last_reported_at
        if snapshot.timestamp - last_reported_at < REPORT_INTERVAL_SECONDS:
            return
        last_reported_at = snapshot.timestamp
        print(dict(snapshot.values))

    poller = PollingLoop(
        sensors=sensors,
        on_snapshot=report,
        interval_seconds=POLL_INTERVAL_SECONDS,
    )
    stop_event = Event()

    try:
        print("Polling PiDog sensors. Press Ctrl+C to stop.")
        poller.run(stop_event)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        dog.close()


if __name__ == "__main__":
    main()
