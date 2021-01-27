'''
Created on Jan 26, 2021

@author: sherzodr
'''
import unittest
import penmon


class Test(unittest.TestCase):


    def testName(self):
        station = penmon.Station(41.42, 109)

        qarmish = station.day_entry("2020-07-04", temp_min=15, temp_max=30)
        rh_mean = qarmish.RH_mean()
        self.assertEqual(rh_mean, 62, "RH_mean()")

        humidity_min = qarmish.RH(15)
        humidity_max = qarmish.RH(30)
        humidity_mean = int(round(( humidity_max + humidity_min ) / 2, 0))

        self.assertEqual(humidity_mean, 62, "Humidity is 62")



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()