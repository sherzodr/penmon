"""


Problem dataset #1

date               1/11/1979
latitude             37.3113
altitude                 263
temp_max                 3.1
temp_min               1.247
wind_speed           2.13654
humidity_mean       0.853413
solar_radiation      3.21356

"""
from penmon import eto as pm
import unittest


class Test(unittest.TestCase):
    def test_bug(self):
        station = pm.Station(37.31, 263)
        day = station.day_entry("1979-01-11")
        day.temp_min = 1.247
        day.temp_max = 3.10
        day.humidity_mean = 85.34
        day.wind_speed = 2.13654
        day.radiation_s = 3.21356
        self.assertTrue(day.net_radiation(), day.net_radiation())
        self.assertTrue(day.eto(), day.eto())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
