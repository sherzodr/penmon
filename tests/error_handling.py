'''
Created on Sep 30, 2020

@author: sherzodr
'''
import unittest
import penmon as pm

class Test(unittest.TestCase):

    def test_smoke(self):
        station = pm.Station(latitude=41.42, altitude=109)
        self.assertIsInstance(station, pm.Station, "Smoke test passed")

    def test_type_error(self):
        try:
            pm.Station(latitude=10, altitude=109)
        except TypeError:
            self.assertTrue(True, "Exception was expected and raised")
        else:
            self.assertTrue(False, "Exception was expected but was NOT raised")

    def test_latitude_range_error(self):
        try:
            pm.Station(latitude=100.0, altitude=100)
        except:
            self.assertTrue(True, "Exception was expected and raised")
        else:
            self.assertTrue(False, "Exception was expected but was NOT raised")

    def test_altitude_range_error(self):
        try:
            pm.Station(latitude=41.42, altitude=-1)
        except:
            self.assertTrue(True, "Exception was expected and raised")
        else:
            self.assertTrue(False, "Exception was expected but NOT raised")

    def test_day_number_type(self):
        station = pm.Station(latitude=41.42, altitude=109)
        try:
            station.get_day(365.0)
        except TypeError:
            self.assertTrue(True, "Exception was expected and raised")
        else:
            self.assertTrue(False, "Exception was expected but was NOT raised")

    def test_day_number_range(self):
        station = pm.Station(latitude=41.42, altitude=109)

        try:
            station.get_day(367)
        except:
            self.assertTrue(True, "Exception was expected and raised")
        else:
            self.assertTrue(False, "Exception was expected but was NOT raised")

    def test_immature_eto(self):
        station = pm.Station(41.42, 109)
        day = station.get_day(238, temp_mean=25.00)
        self.assertTrue(day.temp_mean != None, "temp_mean was set")
        self.assertEqual(day.temp_mean, day.Tmean())
        
        # following code should raise an exception:
        try:
            day.eto()
        except Exception as e:
            self.assertTrue(True, str(e))
        else:
            self.assertTrue(False, "Exception was expected")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
