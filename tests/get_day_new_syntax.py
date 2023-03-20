"""
Created on Oct 5, 2020

@author: sherzodr
"""
from penmon import eto as pm
import unittest


class Test(unittest.TestCase):

    station = pm.Station(41.42, 109)

    def test_name(self):
        # day_228 = self.station.day_entry(228, temp_min=19.5, temp_max=25.6, humidity_mean=60, wind_speed=2.35)

        day_228 = self.station.day_entry(228)
        day_228.temp_min = 19.5
        day_228.temp_max = 25.6
        day_228.humidity_mean = 60
        day_228.wind_speed = 2.35

        self.assertEqual(day_228.eto(), 3.94)

    def test_new_day_entry(self):
        day_228_2 = self.station.day_entry(
            228, temp_min=19.5, temp_max=25.6, humidity_mean=60, wind_speed=2.35
        )
        self.assertEqual(day_228_2.eto(), 3.94)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
