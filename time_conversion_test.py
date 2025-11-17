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




if __name__ == '__main__':
    unittest.main()