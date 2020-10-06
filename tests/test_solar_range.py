'''
Created on Oct 6, 2020

@author: sherzodr
'''
import unittest
import penmon.eto as pm

class Test(unittest.TestCase):

    def test_solar_radiation_range(self):
        station = pm.Station(41.42, 109)

        try:
            day=station.get_day("2020-08-16", temp_min=19.8, temp_max=29.9, radiation_s=27.5)
            self.assertTrue(day.eto())
        except ValueError:
            self.assertTrue(True, "Out of range ValueError caught")
        else: 
            self.assertTrue(False, "Out of range ValueError NOT caught")

    def test_daylight_hours(self):
        station = pm.Station(41.42, 109)

        try:
            day = station.get_day("2020-08-16", temp_min=19.8, temp_max=29.9, radiation_s=35)
            self.assertTrue(day.eto())
        except ValueError:
            self.assertTrue(True, "out of range ValueError caught")
            
        else:
            self.assertTrue(False, "out of range ValueError NOT caught")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_solar_radiation_range']
    unittest.main()