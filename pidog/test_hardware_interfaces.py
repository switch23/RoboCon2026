import unittest

from sensor import (
    DualTouchSensor,
    ImuReading,
    ImuSensor,
    SoundDirectionSensor,
    UltrasonicSensor,
)
from servo import HeadServo, LegsServo, TailServo


class FakeTouchReader:
    def read(self) -> str:
        return "L"


class FakeSoundReader:
    def __init__(self) -> None:
        self.detected = False

    def isdetected(self) -> bool:
        return self.detected

    def read(self) -> int:
        return 90


class FakeDog:
    def __init__(self) -> None:
        self.dual_touch = FakeTouchReader()
        self.ears = FakeSoundReader()
        self.accData = [1, 2, 3]
        self.gyroData = [4, 5, 6]
        self.calls = []

    def read_distance(self) -> float:
        return 25.5

    def head_move(self, target_yrps, immediately=True, speed=50) -> None:
        self.calls.append(("head_move", target_yrps, immediately, speed))

    def head_stop(self) -> None:
        self.calls.append(("head_stop",))

    def legs_move(self, target_angles, immediately=True, speed=50) -> None:
        self.calls.append(("legs_move", target_angles, immediately, speed))

    def legs_stop(self) -> None:
        self.calls.append(("legs_stop",))

    def tail_move(self, target_angles, immediately=True, speed=50) -> None:
        self.calls.append(("tail_move", target_angles, immediately, speed))

    def tail_stop(self) -> None:
        self.calls.append(("tail_stop",))


class HardwareInterfaceTests(unittest.TestCase):
    def test_sensor_adapters_read_from_device(self) -> None:
        dog = FakeDog()

        self.assertEqual(UltrasonicSensor(dog).read(), 25.5)
        self.assertEqual(DualTouchSensor(dog).read(), "L")
        self.assertEqual(
            ImuSensor(dog).read(),
            ImuReading((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)),
        )

        sound = SoundDirectionSensor(dog)
        self.assertEqual(sound.read(), -1)
        dog.ears.detected = True
        self.assertEqual(sound.read(), 90)

    def test_servo_adapters_translate_commands(self) -> None:
        dog = FakeDog()

        HeadServo(dog).move(1, 2, 3, speed=60, immediately=False)
        LegsServo(dog).move([[0] * 8], speed=70)
        TailServo(dog).move([10, 20], speed=80)

        self.assertEqual(
            dog.calls,
            [
                ("head_move", [[1, 2, 3]], False, 60),
                ("legs_move", [[0] * 8], True, 70),
                ("tail_move", [[10], [20]], True, 80),
            ],
        )

    def test_legs_servo_rejects_frames_with_wrong_width(self) -> None:
        dog = FakeDog()

        with self.assertRaises(ValueError):
            LegsServo(dog).move([[0] * 7])

        self.assertEqual(dog.calls, [])


if __name__ == "__main__":
    unittest.main()
