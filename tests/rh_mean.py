"""
Created on Jan 26, 2021

@author: sherzodr
"""
from penmon import eto as pm
import unittest


class Test(unittest.TestCase):
    def testName(self):
        station = pm.Station(41.42, 109)

        qarmish = station.day_entry("2020-07-04", temp_min=15, temp_max=30)
        rh_mean = qarmish.relative_humidity_mean()
        self.assertEqual(rh_mean, 62, "relative_humidity_mean() wrong calc.")

        humidity_min = qarmish.relative_humidity(15)
        humidity_max = qarmish.relative_humidity(30)
        humidity_mean = int(round((humidity_max + humidity_min) / 2, 0))

        self.assertEqual(humidity_mean, 62, "Humidity is 62")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
