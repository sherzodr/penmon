'''
Created on Sep 30, 2020

@author: sherzodr
'''
import unittest
import penmon.eto as pm


class Test(unittest.TestCase):

    def test_date_parse(self):
        station = pm.Station(41.42, 109)
        day = station.get_day(228)
        self.assertEqual(day.day_number, 228)
        
        day=station.get_day("2020-01-01")
        self.assertEqual(day.day_number, 1)
        
        day=station.get_day("2020-08-16")
        self.assertEqual(day.day_number, 229)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()