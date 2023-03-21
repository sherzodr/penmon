"""
Created on Sep 29, 2020

@author: sherzodr

This test case uses examples in the UN-FAO's "Irrigation and Drainage paper 56"
as test cases, to verify we are in sync with oroginal paper's methodology.

Examples in the original paper does not use floating points as consistently.
I had to standardadize floating point arithmetic for the purposes of consistency.

"""
from penmon.eto import Climate, DayEntry, Station
import unittest


class Test(unittest.TestCase):

    station = Station(41.42, 109)
    station.climate = Climate()
    day_130 = station.day_entry(130)

    def test_station_class(self):
        """Testing Station instance attributes"""
        self.assertIsInstance(self.station, Station, "station is instance of Station")
        self.assertEqual(self.station.latitude, 41.42, "station.latitude")
        self.assertEqual(self.station.altitude, 109, "station.altitude")
        self.assertEqual(self.station.anemometer_height, 2, "station.anemometer_height")
        self.assertIsInstance(self.station.climate, Climate, "station.climate")

    def test_station_day(self):
        """Testing station's 'day()' method"""
        day = self.station.day_entry(130)
        self.assertEqual(day.day_number, 130, "Station.day.day_number")
        # print(type(day))
        self.assertIsInstance(day, DayEntry, "staion.day is instance of ")

    def test_atmospheric_pressure(self):
        station = Station(41.42, 1800)
        station.climate = Climate()
        day = station.day_entry(130)
        self.assertEqual(round(day.atmospheric_pressure(), 1), 81.8, "Atmosphertic pressure")

    def test_station_atmospheric_pressure(self):
        station = Station(41.42, 1800)
        self.assertEqual(round(station.atmospheric_pressure(), 1), 81.8, "Atmosphertic pressure")

    def test_psychrometric_constant(self):
        station = Station(41.42, 1800)
        station.climate = Climate()
        day = station.day_entry(130)
        self.assertEqual(day.psychrometric_constant(), 0.05437, "psychrometric constant")

    def test_specific_heat(self):
        day = self.station.day_entry(130)
        self.assertEqual(day.specific_heat, 1.013 * 10 ** (-3))

    def test_latent_heat_of_vaporization(self):
        day = self.station.day_entry(130)
        self.assertEqual(day.latent_heat_of_vaporization, 2.45)

    def test_mean_saturation_vp(self):
        day_130 = self.day_130
        day_130.temp_max = 24.5
        day_130.temp_min = 15
        self.assertEqual(
            day_130.mean_saturation_vapour_pressure(),
            2.39,
            "mean_saturation_vapour_pressure()",
        )

    def test_RH(self):
        day = self.station.day_entry(130)
        day.temp_dew = 19.5
        self.assertEqual(
            round(day.relative_humidity(35), 2),
            40.32,
            "We can calculate relative humidity for a given T if dew point is known",
        )

    def test_mean_saturation_vp2(self):
        day = self.station.day_entry(130)
        day.temp_mean = 19.75
        self.assertEqual(
            day.mean_saturation_vapour_pressure(),
            2.302,
            "mean_saturation_vapour_pressure using just Tmean",
        )

    def test_slope_of_saturation_vp(self):
        day = self.station.day_entry(130)
        slope = day.slope_of_saturation_vapour_pressure(24.5)
        self.assertEqual(slope, 0.183837, "slope of vapour pressure curve")

    def test_actual_vapour_pressure_psychrometric(self):
        station = Station(41.42, 1200)
        station.climate = Climate()
        day = station.day_entry(130)
        day.temp_wet = 19.5
        day.temp_dry = 25.6
        self.assertEqual(day.atmospheric_pressure(), 87.9, 87.9)
        self.assertEqual(day.saturation_vapour_pressure(19.5), 2.267)
        self.assertEqual(day.temp_dew, None, "No dew point temperature known")
        self.assertEqual(
            day.actual_vapour_pressure(),
            1.91,
            "Actual vapour pressure from psychrometric data",
        )

    def test_actual_vapour_pressure_dew(self):
        station = Station(41.42, 1200)
        station.climate = Climate()
        day = station.day_entry(130)

        self.assertEqual(day.temp_dew, None, "Dew temp is not known")
        day.temp_dew = 17.0
        self.assertEqual(day.temp_dew, 17.0, "Dew temp is set")
        self.assertEqual(
            day.actual_vapour_pressure(),
            1.938,
            "Actual vapour pressure with no psychrometric data",
        )

    def test_actual_vapour_pressure_humidity(self):

        station = Station(41.42, 1200)
        station.climate = Climate()

        day = station.day_entry(130)
        day.temp_min = 18
        day.temp_max = 25
        day.humidity_max = 82
        day.humidity_min = 54

        sat_vap_pres_min = day.saturation_vapour_pressure(day.temp_min)
        self.assertEqual(sat_vap_pres_min, 2.064)

        sat_vap_pres_max = day.saturation_vapour_pressure(day.temp_max)
        self.assertEqual(sat_vap_pres_max, 3.168)

        actual_vp = day.actual_vapour_pressure()
        self.assertEqual(actual_vp, 1.702)

    def test_actual_vapour_pressure_humidity_max_temp_min(self):
        station = Station(41.42, 1200)

        day = station.day_entry(130)
        day.temp_min = 18
        day.humidity_max = 82

        actual_vp = day.actual_vapour_pressure()
        self.assertEqual(
            actual_vp,
            1.692,
            "Actual vapour pressure with only humidity_max and temp_min",
        )

    def test_actual_vapour_pressure_humidity_mean(self):
        station = Station(41.42, 1200)

        day = station.day_entry(130)
        day.temp_min = 18
        day.temp_max = 25
        day.humidity_mean = 68

        actual_vp = day.actual_vapour_pressure()
        self.assertEqual(
            actual_vp,
            1.779,
            "Actual vapour pressure with only humidity_mean, temp_min and temp_max",
        )

    def test_vapour_pressure_deficit(self):
        station = Station(41.42, 1200)

        day = station.day_entry(130)
        day.temp_min = 18
        day.temp_max = 25
        day.humidity_max = 82
        day.humidity_min = 54

        vp_deficit = day.vapour_pressure_deficit()
        self.assertEqual(vp_deficit, 0.914, "Dtermining vapour pressure deficit")

    def test_latitude_rad(self):
        station_bangkok = Station(13.73, 1200)
        self.assertEqual(station_bangkok.latitude_rad, 0.240)
        station_rio = Station(22.90, 1200)
        self.assertEqual(station_rio.latitude_rad, 0.400)

    def test_relative_sun_distance(self):
        dr = self.station.day_entry(246).relative_sun_distance()
        self.assertEqual(dr, 0.985)

    def test_solar_declination(self):
        declination = self.station.day_entry(246).solar_declination()
        self.assertEqual(declination, 0.120)

    def test_sunset_hour_angle(self):
        station = Station(-20.0, 1200)
        sunset_angle = station.day_entry(246).sunset_hour_angle()
        self.assertEqual(sunset_angle, 1.527)

    def test_r_a(self):
        r_a = Station(-20.0, 1200).day_entry(246).r_a()
        self.assertEqual(r_a, 32.2)

    def test_r_a_in_mm(self):
        r_a = Station(-20.0, 1200).day_entry(246).ra_to_mm()
        self.assertEqual(r_a, 13.10)

    def test_daylight_hours(self):
        hours = Station(-20.0, 1200).day_entry(246).daylight_hours()
        self.assertEqual(hours, 11.7)

    def test_solar_radiation(self):
        day = Station(-22.90, 1200).day_entry(135)
        day.sunshine_hours = 7.10
        radiation = day.solar_radiation()
        self.assertEqual(radiation, 14.4)

    def test_clear_sky_solar_radiation(self):
        day = Station(-22.90, 0).day_entry(135)
        day.sunshine_hours = 7.1
        solar_radiation = day.solar_radiation()
        self.assertEqual(solar_radiation, 14.4)

        clear_sky_radiation = day.clear_sky_rad()
        self.assertEqual(clear_sky_radiation, 18.8)

    def test_net_shortwave_radiation(self):
        day = Station(-22.90, 1200).day_entry(135)
        day.sunshine_hours = 7.1
        r_ns = day.net_solar_rad()
        self.assertEqual(r_ns, 11.1)

    def test_net_longwave_radiation(self):
        day = Station(-22.90, 1200).day_entry(135)

        day.temp_max = 25.1
        day.temp_min = 19.1
        day.vapour_pressure = 2.1

        vp = day.actual_vapour_pressure()
        self.assertEqual(vp, 2.1)

        day.sunshine_hours = 7.1

        r_nl = day.net_longwave_rad()
        self.assertEqual(r_nl, 3.3)

    def test_net_radiation(self):
        day = Station(-22.90, 1200).day_entry(135)
        day.temp_max = 25.1
        day.temp_min = 19.1
        day.vapour_pressure = 2.1
        day.sunshine_hours = 7.1

        net_radiation = day.net_radiation()
        self.assertEqual(net_radiation, 7.8)

    def test_wind_speed2m(self):
        day = Station(-22.90, 1200).day_entry(135)
        day.wind_speed = 5

        self.assertEqual(day.wind_speed_2m(), 5)

        day.station.anemometer_height = 10
        day.wind_speed = 3.2
        self.assertEqual(day.wind_speed_2m(), 2.4)

    def test_solar_radiation_from_temp(self):
        day = Station(45.72, 200).day_entry(196)
        day.temp_max = 26.6
        day.temp_min = 14.8

        ra = day.r_a()
        self.assertEqual(ra, 40.6)

        solar_radiation = day.solar_radiation()
        self.assertEqual(solar_radiation, 22.3)
        self.assertEqual(day.solar_radiation_in_mm(), 9.1)

    def test_net_radiation_without_radiation_data(self):
        day = Station(13.73, 2).day_entry(105)

        climate = day.station.climate
        climate.coastal()

        day.temp_min = 25.6
        day.temp_max = 34.8

        self.assertEqual(Station(13.73, 2).latitude_rad, 0.24)

        ra = day.r_a()
        self.assertEqual(ra, 38.0)
        net_radiation = day.net_radiation()

        self.assertEqual(net_radiation, 14.0)

    def test_solar_radiation_in_island(self):
        day = Station(41.42, 10).day_entry(105)
        day.station.climate.island()

        rs = day.solar_radiation()
        self.assertEqual(rs, 20.0)

        day.station.climate.coastal()

        rs = day.solar_radiation()
        self.assertEqual(rs, 25.7)

        day.station.climate.interior()

        rs = day.solar_radiation()
        self.assertEqual(rs, 25.7)

    def test_eto_hargreaves(self):
        day = Station(41.42, 109).day_entry(295)
        day.temp_min = 19.5
        day.temp_max = 26.5

        eto = day.eto_hargreaves()
        self.assertEqual(eto, 4.97)

    def test_eto(self):
        day = Station(41.42, 109).day_entry(150)
        day.temp_min = 19.5
        day.temp_max = 36.5
        day.wind_speed = 2
        # day.humidity_mean = 60

        self.assertEqual(day.slope_of_saturation_vapour_pressure(23), 0.169921)
        self.assertEqual(day.net_radiation(), 16.1)
        self.assertEqual(day.soil_heat_flux(), 0)
        self.assertEqual(round(day.psychrometric_constant(), 4), 0.0665)
        self.assertEqual(day.wind_speed_2m(), 2)
        self.assertEqual(day.vapour_pressure_deficit(), 2.186)

        eto = day.eto()

        self.assertEqual(eto, 6.98)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
