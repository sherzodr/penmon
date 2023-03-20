from penmon.eto import Station
import unittest


class Test(unittest.TestCase):
    def test_et0(self):
        station = Station(41.42, 109)

        data = {
            228: [19.8, 29.9, 4.49],
            229: [15.1, 29.9, 5.13],
            230: [13.4, 29.6, 5.24],
            231: [12.7, 31.1, 5.62],
            232: [16.2, 32.8, 5.66],
            233: [16.9, 33.6, 5.72],
            234: [16.0, 35.5, 6.27],
        }

        for day_number, wdata in data.items():
            day = station.day_entry(day_number)
            day.temp_min = wdata[0]
            day.temp_max = wdata[1]
            day.wind_speed = 2
            self.assertEqual(
                day.eto(),
                wdata[2],
                f"day {day_number}: Tmin={wdata[0]}, Tmax={wdata[1]}, ETo={wdata[2]}",
            )

    def test_with_no_assumptions(self):

        station = Station(41.42, 109)
        station.climate = None

        day = station.day_entry(228)  # august 16
        day.temp_min = 19.8
        day.temp_max = 29.9
        day.radiation_s = 264 * 0.0864
        day.humidity_min = 37
        day.humidity_max = 88
        day.wind_speed = 2

        self.assertEqual(day.eto(), 5.3)


if __name__ == "__main__":
    unittest.main()
