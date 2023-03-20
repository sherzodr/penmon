import unittest

from penmon import eto as pm


class Test(unittest.TestCase):
    def test_daylight_hours(self):
        station = pm.Station(41.42, 109)
        day = station.day_entry(135)
        day.temp_min = 19.5
        day.temp_max = 28

        self.assertEqual(day.daylight_hours(), 14.3, "daylighth_hours")


if __name__ == "__main__":
    unittest.main()
