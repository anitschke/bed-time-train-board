from time_conversion import TimeConversion
from datetime import datetime
import unittest

class Test_relative_time_from_now(unittest.TestCase):
    def run_test(self, time_seconds, exp_result):
        time_conv = TimeConversion()
        act_result = time_conv.format_relative_time_from_now(time_seconds)
        self.assertEqual(act_result, exp_result)

    def test_zero(self):
        self.run_test(time_seconds=0, exp_result="0sec")
    
    def test_seconds_only(self):
        self.run_test(time_seconds=10, exp_result="10sec")

    def test_minutes_and_seconds(self):
        self.run_test(time_seconds=70, exp_result="1min 10sec")

    def test_minutes_only(self):
        self.run_test(time_seconds=120, exp_result="2min")


class Test_format_clock_time(unittest.TestCase):
    def run_test(self, hour, minute, exp_result):
        time_conv = TimeConversion()
        act_result = time_conv.format_clock_time(hour, minute)
        self.assertEqual(act_result, exp_result)

    def test_midnight(self):
        # 0:00 should display as 12:00
        self.run_test(hour=0, minute=0, exp_result="12:00")

    def test_noon(self):
        # 12:00 should display as 12:00
        self.run_test(hour=12, minute=0, exp_result="12:00")

    def test_noon_with_minutes(self):
        # 12:05 should display as 12:05
        self.run_test(hour=12, minute=5, exp_result="12:05")

    def test_single_digit_hour(self):
        # Single digit hours should have a leading space for alignment
        self.run_test(hour=9, minute=15, exp_result=" 9:15")

    def test_double_digit_morning_hour(self):
        self.run_test(hour=10, minute=30, exp_result="10:30")

    def test_afternoon_single_digit_hour(self):
        # 13:05 (1:05 PM) should display as  1:05
        self.run_test(hour=13, minute=5, exp_result=" 1:05")

    def test_afternoon_double_digit_hour(self):
        # 23:45 (11:45 PM) should display as 11:45
        self.run_test(hour=23, minute=45, exp_result="11:45")


class Test_analog_clock_angles(unittest.TestCase):
    def setUp(self):
        self.time_conv = TimeConversion()

    def test_zero_angles(self):
        # 00:00:00 or 12:00:00 -> all hands point to 12 o'clock (0 degrees)
        hour_angle, minute_angle, second_angle = self.time_conv.analog_clock_angles(0, 0, 0)
        self.assertEqual(hour_angle, 0.0)
        self.assertEqual(minute_angle, 0.0)
        self.assertEqual(second_angle, 0.0)

        hour_angle_12, minute_angle_12, second_angle_12 = self.time_conv.analog_clock_angles(12, 0, 0)
        self.assertEqual(hour_angle_12, 0.0)
        self.assertEqual(minute_angle_12, 0.0)
        self.assertEqual(second_angle_12, 0.0)

    def test_quarter_past(self):
        # 15 minutes / 15 seconds -> 90 degrees (3 o'clock)
        self.assertEqual(self.time_conv.second_hand_angle(15), 90.0)
        self.assertEqual(self.time_conv.minute_hand_angle(15), 90.0)
        self.assertEqual(self.time_conv.hour_hand_angle(3), 90.0)
        self.assertEqual(self.time_conv.hour_hand_angle(15), 90.0)  # 3 PM

    def test_half_past(self):
        # 30 minutes / 30 seconds -> 180 degrees (6 o'clock)
        self.assertEqual(self.time_conv.second_hand_angle(30), 180.0)
        self.assertEqual(self.time_conv.minute_hand_angle(30), 180.0)
        self.assertEqual(self.time_conv.hour_hand_angle(6), 180.0)
        self.assertEqual(self.time_conv.hour_hand_angle(18), 180.0)  # 6 PM

    def test_quarter_to(self):
        # 45 minutes / 45 seconds -> 270 degrees (9 o'clock)
        self.assertEqual(self.time_conv.second_hand_angle(45), 270.0)
        self.assertEqual(self.time_conv.minute_hand_angle(45), 270.0)
        self.assertEqual(self.time_conv.hour_hand_angle(9), 270.0)
        self.assertEqual(self.time_conv.hour_hand_angle(21), 270.0)  # 9 PM


if __name__ == '__main__':
    unittest.main()