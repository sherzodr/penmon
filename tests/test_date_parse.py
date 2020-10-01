'''
Created on Sep 30, 2020

@author: sherzodr
'''
import unittest
import penmon.eto as pm


class Test(unittest.TestCase):

    station = pm.Station(41.42, 109)

    def test_date_parse(self):
        day = self.station.get_day(229)
        self.assertEqual(day.day_number, 229)

    def test_first_date(self):
        day=self.station.get_day("2020-01-01")
        self.assertEqual(day.day_number, 1)

    def test_isodate_parse(self):

        day=self.station.get_day("2020-08-16")
        self.assertEqual(day.day_number, 229)

    def test_parse_us_date(self):

        day=self.station.get_day("08/16/2020", "%m/%d/%Y")
        self.assertEqual(day.day_number, 229)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()