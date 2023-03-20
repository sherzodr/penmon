"""
Created on Oct 6, 2020

@author: sherzodr
"""
import unittest

from penmon import eto as pm


class Test(unittest.TestCase):
    def test_solar_radiation_range(self):
        station = pm.Station(41.42, 109)

        self.assertTrue(pm.CHECK_RADIATION_RANGE is True)

        eto = False
        try:
            day = station.day_entry("2020-08-16", temp_min=19.8, temp_max=29.9, radiation_s=27.5)
            self.assertTrue(day.eto())
        except Exception as e:
            self.assertIsInstance(e, ValueError, f"Out of range ValueError caught: {str(e)}")
        else:
            self.assertTrue(False, "Out of range ValueError NOT caught")

    def test_daylight_hours(self):
        station = pm.Station(41.42, 109)

        try:
            day = station.day_entry("2020-08-16", temp_min=19.8, temp_max=29.9, radiation_s=35)
            self.assertTrue(day.eto())
        except ValueError:
            self.assertTrue(True, "out of range ValueError caught")
        else:
            self.assertTrue(False, "out of range ValueError NOT caught")
            day = station.day_entry("2020-08-16", temp_min=19.8, temp_max=29.9, radiation_s=27.5)

    def test_no_solar_range_test(self):

        self.assertTrue(pm.CHECK_RADIATION_RANGE, "CHECK_RADIATION_RANGE defaults to True")

        pm.CHECK_RADIATION_RANGE = False

        self.assertTrue(not pm.CHECK_RADIATION_RANGE, "CHECK_RADIATION_RANGE defaults to True")

        try:
            day = pm.Station(41.42, 109).day_entry(
                "2020-08-16", temp_min=19.8, temp_max=29.9, radiation_s=35
            )
            self.assertTrue(day.eto() > 0)
        except Exception:
            self.assertTrue(False, "out of range exception raised")
        else:
            self.assertTrue(True, "out of range exception was not raised, as planned")

        pm.CHECK_RADIATION_RANGE = True

    def test_check_sunshine_hours_range(self):
        try:
            day = pm.Station(41.42, 109).day_entry(
                "2019-12-21", sunshine_hours=15, temp_min=19.8, temp_max=29.9
            )
            self.assertTrue(day.eto())
        except Exception as e:
            self.assertTrue(True, str(e))
        else:
            self.assertTrue(False, "Out of range exception was supposed to be raised")

    def test_check_sunshine_hours_range_error_ignore(self):
        pm.CHECK_SUNSHINE_HOURS_RANGE = False

        try:
            day = pm.Station(41.42, 109).day_entry(
                "2019-12-21", temp_min=-5, temp_max=5.50, sunshine_hours=15
            )
            self.assertTrue(day.eto())
        except Exception as e:
            self.assertTrue(False, str(e))
        else:
            self.assertTrue(True, "Out of range exception was NOT supposed to be raised")
        pm.CHECK_SUNSHINE_HOURS_RANGE = True


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_solar_radiation_range']
    unittest.main()
