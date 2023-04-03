"""
Created on Mar 31, 2021

@author: sherzodr
"""
import math
from penmon import eto as pm
import unittest

# penmon.eto.CHECK_RADIATION_RANGE=False


class Test(unittest.TestCase):

    station = pm.Station(37.85, 100, anemometer_height=10)
    day180 = station.get_day(
        180,
        temp_min=15,
        temp_max=35,
        humidity_min=30,
        humidity_max=70,
        wind_speed=2,
        radiation_s=30,
    )

    def testDecl(self):
        day180 = self.day180
        self.assertEqual(day180.solar_declination(), 0.405, "solar declination is 0.405 rad")
        self.assertEqual(
            round(day180.solar_declination() * 180 / math.pi, 2),
            23.20,
            "solar declination is 23.23 degrees",
        )

    def testHourAngle(self):
        self.assertEqual(self.day180.sunset_hour_angle(), 1.911, "Sunset hour angle is 1.91")

    def testETo(self):
        self.assertEqual(self.day180.eto(), 6.79, "eto equals 6.79mm")

    def testSunDistance(self):
        self.assertEqual(
            self.day180.relative_sun_distance(),
            0.967,
            "inverse of relative sun distance",
        )

    def testRs(self):
        self.assertEqual(self.day180.r_a(), 41.7, "Ra is 41.7")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
