"""
Penman-Monteith Equation implementation in Python.

Full implementation of Penman-Monteith ETo equation based on UAN-FAO
[Irrigation and Drainage Paper 56](http://www.fao.org/3/X0490E/x0490e00.htm)

Penman-Monteith equation is used to calculate reference crop evapotranspiration (ETo)
for a given location using available climate data. This method provides many ways of estimating
missing climate data using minimal data.

Homepage of the project: https://github.com/sherzodr/penmon

"""

import datetime as dt
from numpy import nan
import math

CHECK_RADIATION_RANGE = True
CHECK_SUNSHINE_HOURS_RANGE = True


class Station:
    """Class that implements a weather station at a known latitude and elevation."""

    def __init__(self, latitude, altitude, anemometer_height=2):
        """
        Instantiate Station object from latitude, altitude, and anemometer height.

        Required parameters:

        :param latitude: latitude of the location in decimal format. For southern
            hemisphere negative number must be used
        :type latitude: float

        :param altitude: altitude (elevation) of the location in meters
        :type altitude: int

        :param anemometer_height=2: height of the anemometer (wind-speed)
            measuring device
        :type anemometer_height: int

        Following are additional attributes that you can get/set on this station
        after instantiation:

         * latitude_rad - latitude in radian, alculated based on latitude
         * days - dictionary of days recorded (or calculated) by this station
         * climate - set to default **Climate()** instance
         * ref_crop - instance of **Crop** class, which sets default chracteristics
                      of the reference crop according to the paper.

        Should you wish to change assumes Climate and Crop characteristics
        you can do so after the object is innitialized, like so:

            station=Station(41.42, 109)
            station.ref_crop = Crop(albedo=0.25, height=0.35)
        """
        if type(latitude) is not float:
            raise TypeError("'latitude' must be a float")

        if latitude < -90.0 or latitude > 90.0:
            raise ValueError("'latitude' must be between -90.0 and 90.0")

        if type(altitude) is not int:
            raise TypeError("'altitude' must be an integer")

        if altitude < 0:
            raise ValueError("'altitude' must be above 0")

        self.latitude = latitude
        self.altitude = altitude
        self.latitude_rad = round((math.pi / 180 * self.latitude), 3)
        self.days = {}

        # setting default parameters for the station
        self.anemometer_height = anemometer_height
        self.climate = Climate()
        self.ref_crop = Crop()

    def day_entry(
        self,
        day_number,
        date_template="%Y-%m-%d",
        temp_min=None,
        temp_max=None,
        temp_mean=None,
        wind_speed=None,
        humidity_mean=None,
        humidity_min=None,
        humidity_max=None,
        radiation_s=None,
        sunshine_hours=None,
    ):
        """
        Calculate the evapotranspiration for a given day or day of year.

        Given a day number (integer type from 1-366) returns a **StationDay*** instance for
        that day. Logs the day in *days* attribute of the **Station()** class.

        If it receives a string it expects it to be in "yyyy-mm-dd" format, in which case
        it parses the string into **datetime** and calculates day number

        If your date format is different than assumed, you can adjust *date_template*
        as the second parameter. For example, following all three lines are identical

            day = station.day_entry(229)
            day = station.day_entry("2020-08-16")
            day = station.day_entry('08/16/2020', '%m/%d/%Y')

        You can pass the following named-parameters to the method:

         - temp_min
         - temp_max
         - wind_speed
         - radiation_s
         - sunshine_hours

         If *radiation_s* and *sunshine_hours* is out of range for this location
         for this date (based on solar declination, sun-distance and daylight hours)
         raises ValueError exception.
        """
        if type(day_number) is str:
            try:
                dt1 = dt.datetime.strptime(day_number, date_template)
            except ValueError as e:
                raise ValueError("Date must be in YYYY-MM-DD format (ex: 2020-09-28)") from e

            dt0 = dt.datetime(dt1.year, 1, 1)
            dates_delta = dt1 - dt0
            day_number = dates_delta.days + 1

        if type(day_number) is not int:
            raise TypeError("'day_number' must be an integer")

        if day_number < 1 or day_number > 366:
            raise ValueError("'day_number' must be between in the range 1-366")

        day = DayEntry(day_number, self)

        self.days[day_number] = day
        day.temp_min = temp_min
        day.temp_max = temp_max
        day.temp_mean = temp_mean
        day.humidity_min = humidity_min
        day.humidity_max = humidity_max
        day.humidity_mean = humidity_mean
        day.wind_speed = wind_speed

        if radiation_s:
            if (
                CHECK_RADIATION_RANGE
                and radiation_s <= day.clear_sky_rad()
                or not CHECK_RADIATION_RANGE
            ):
                day.radiation_s = radiation_s
            elif radiation_s is nan:
                pass
            else:
                raise ValueError("Radiation out of range")
        if sunshine_hours:
            if (
                CHECK_SUNSHINE_HOURS_RANGE
                and sunshine_hours <= day.daylight_hours()
                or not CHECK_SUNSHINE_HOURS_RANGE
            ):
                day.sunshine_hours = sunshine_hours
            else:
                raise ValueError("Sunshine hours out of range")
        return day

    get_day = day_entry

    def atmospheric_pressure(self):
        """Calculate atmospheric pressure *in kPa* based on station's altitude (Eq. 7)."""
        return round(101.3 * ((293 - 0.0065 * self.altitude) / 293) ** 5.26, 2)

    def describe(self):
        """Describe the station and all its assumptions in human-friendly text."""
        return self


class DayEntry:
    """
    Represents a single day retrieved from the Station.

    This class is usually not instantiated directly. It's instantniated by the
    **Station()**'s day_entry() method, passing all reuqired state data.

    Since bulk of Penman-Moneith is concerned with a daily ETo **StationDay** is
    heart of the module. Penman-Monteith equatoin is implemented within the
    methods of **StationDay**.

    All meteorological data are stored within this class instance.
    """

    def __init__(self, day_number, station):
        """
        Instantiate a DayEntry-object.

        *day_number* and *station* are two required arguments passed to
        instantiate the class. Day number must be between 1-366. It represents a
        single day in a year, *1* meaning January 1st, and 365 (or 366) being
        Decement 31st. *station* must be instance of **Station** class. It reads
        such important information from the station as its location, altitude,
        climate conditions. Without this information it's impossible to
        calculate solar radiation and humidity data.

        Following attributes of the class are available. They can be both set
        and get.

        - day_number
        - station   - references **Station** class.
        - temp_min
        - temp_max
        - temp_mean
        - temp_dew
        - temp_dry
        - temp_wet
        - humidity_mean
        - humidity_min
        - humidity_max
        - vapour_pressure
        - wind_speed
        - radiation_s
        - stephan_boltzman_constant
        - climate  - convenient reference to station.climate
        - sunshine_hours
        -
        """
        self.day_number = day_number
        self.station = station
        self.temp_min = None
        self.temp_max = None
        self.temp_mean = None
        self.humidity_mean = None
        self.humidity_min = None
        self.humidity_max = None
        self.wind_speed = None
        self.radiation_s = None
        self.temp_dew = None
        self.temp_dry = None
        self.temp_wet = None
        self.climate = station.climate
        self.stephan_boltzmann_constant = 4.903 * (10**-9)
        self.vapour_pressure = None
        self.sunshine_hours = None
        self.specific_heat = 1.013 * 10 ** (-3)
        self.latent_heat_of_vaporization = 2.45

    def wind_speed_2m(self):
        """
        Calculate the wind speed at 2m height.

        If this information is already logged, returns as is. If anemometer of
        the Station is located higher and wind speed information is available it
        converts this information to wind speed as 2ms based on  logarithimc
        conversion (Eq. 47)

        If wind speed was not logged for this date, and if climate is known
        tries to rely on Climate data to estimate average wind speed

        if wind speed at 2m height is given, return it
        if wind speed at height different than 2m is given, calculate wind
        speed at 2m
        """
        if self.wind_speed:
            if self.station.anemometer_height == 2:
                return self.wind_speed

            return round(
                self.wind_speed * (4.87 / math.log(67.8 * self.station.anemometer_height - 5.42)), 1
            )

        # if we reach this far no wind information is available to work with. we
        # consult if station has any climatic data, in which case we try to
        # deduce information off of that:
        if self.station.climate:
            return self.station.climate.average_wind_speed

        return None

    def dew_point(self):
        """
        Calculate dew point temperature.

        If *temp_dew* attribute is logged returns as is.
        If this data was not logged, but *temp_min* data is available tries to estimate *temp_dew*
        based on Station's Climate. If either is not possible returns *None*.
        """
        if self.temp_dew:
            return self.temp_dew

        if self.temp_min and self.climate:
            return self.temp_min - self.climate.dew_point_difference
        return False

    def atmospheric_pressure(self):
        """Calculate atmospheric pressure *in kPa* based on station's altitude (Eq. 7)."""
        return self.station.atmospheric_pressure()

    def psychrometric_constant(self):
        """
        Calculate psychrometric constant.

        The computation is based on Station's altitude (and atmospheric pressure, Eq. 8).
        """
        return round(0.665 * 10 ** (-3) * self.atmospheric_pressure(), 6)

    def interpolate_temp_mean(self):
        """
        Interpolate the mean temperature from max and min.

        If *temp_mean* is logged returns is as is. If *temp_min* and *temp_max*
        are available computes *temp_mean* based on these data. If none are
        available returns *None*. (Eq. 9)
        """
        if self.temp_mean:
            return self.temp_mean

        if self.temp_max and self.temp_min:
            return (self.temp_max + self.temp_min) / 2

        return None

    def saturation_vapour_pressure(self, temp):
        """Calculate saturation vapour pressure for a given temperature (Eq. 11)."""
        return round((0.6108 * (2.7183 ** (17.27 * temp / (temp + 237.3)))), 3)

    def mean_saturation_vapour_pressure(self):
        """
        Calculate mean saturation vapour pressure.

        Given *temp_max* and *temp_min* calculates mean saturation vapour pressure. (Eq. 12)
        """
        if self.temp_max and self.temp_min:
            vp_max = self.saturation_vapour_pressure(self.temp_max)
            vp_min = self.saturation_vapour_pressure(self.temp_min)
            return (vp_max + vp_min) / 2

        if self.temp_mean:
            return self.saturation_vapour_pressure(self.temp_mean)

    def slope_of_saturation_vapour_pressure(self, temp):
        """
        Calculate slope of the saturation vapour pressure curve for a given temperature.

        It's the required information to calculate ETo. (Eq. 13)
        """
        return round(
            (4098 * (0.6108 * 2.7183 ** (17.27 * temp / (temp + 237.3)))) / ((temp + 237.3) ** 2), 6
        )

    def actual_vapour_pressure(self):
        """
        Attempt to calculate vapour pressure based on several available weather data.

        If *temp_dry* and *temp_wet* data are logged (psychrometric data) uses
        (Eq. 15) to calculate actual vapour pressure. If only *temp_dew*
        information is logged uses (Eq. 14) to calculate actual vapour pressure.
        If *humidity_max* and *humidity_min* are logged uses (Eq. 17) to
        calculate vapour pressure. If only *humidity_max* is known uses (Eq. 18)
        to estimate actual vapour pressure. If only *humidity_mean* is known
        uses (Eq. 19) to estimate actual vapour pressure.
        """
        if self.vapour_pressure:
            return self.vapour_pressure

        if self.temp_dry and self.temp_wet:
            vp_wet = self.saturation_vapour_pressure(self.temp_wet)
            psychrometric_constant = self.psychrometric_constant()
            return round(vp_wet - psychrometric_constant * (self.temp_dry - self.temp_wet), 3)

        if self.humidity_max and self.humidity_min and self.temp_max and self.temp_min:
            vp_min = self.saturation_vapour_pressure(self.temp_min)
            vp_max = self.saturation_vapour_pressure(self.temp_max)
            return round(
                (vp_min * (self.humidity_max / 100) + vp_max * (self.humidity_min / 100)) / 2, 3
            )

        if self.humidity_max and self.temp_min:
            vp_min = self.saturation_vapour_pressure(self.temp_min)
            return round(vp_min * (self.humidity_max / 100), 3)

        if self.humidity_mean and self.temp_max and self.temp_min:
            vp_min = self.saturation_vapour_pressure(self.temp_min)
            vp_max = self.saturation_vapour_pressure(self.temp_max)
            return round((self.humidity_mean / 100) * ((vp_max + vp_min) / 2), 3)

        if self.dew_point():
            return round(self.saturation_vapour_pressure(self.dew_point()), 3)

    def vapour_pressure_deficit(self):
        """Calculate vapour pressure deficit."""
        if self.temp_min and self.temp_max:
            vp_min = self.saturation_vapour_pressure(self.temp_min)
            vp_max = self.saturation_vapour_pressure(self.temp_max)
            actual_vp = self.actual_vapour_pressure()
            return round(((vp_min + vp_max) / 2) - actual_vp, 3)

    def relative_sun_distance(self):
        """Eq. 23."""
        return round(1 + 0.033 * math.cos((2 * math.pi / 365) * self.day_number), 3)

    def solar_declination(self):
        """Eq. 24."""
        return round(0.409 * math.sin((2 * math.pi / 365) * self.day_number - 1.39), 3)

    def x_distance_from_sun(self):
        """Eq. 27."""
        x = 1 - math.tan(self.station.latitude_rad) * math.tan(self.solar_declination())
        if x <= 0:
            x = 0.00001
        return x

    def sunset_hour_angle(self):
        """Eq. 25."""
        return round(
            math.acos(
                -1 * math.tan(self.station.latitude_rad) * math.tan(self.solar_declination())
            ),
            3,
        )

    def r_a(self):
        """Extraterrestrial radiation for daily periods ( Eq. 21 )."""
        return round(
            24
            * 60
            / math.pi
            * 0.0820
            * self.relative_sun_distance()
            * (
                (
                    self.sunset_hour_angle()
                    * math.sin(self.station.latitude_rad)
                    * math.sin(self.solar_declination())
                )
                + (
                    math.cos(self.station.latitude_rad)
                    * math.cos(self.solar_declination())
                    * math.sin(self.sunset_hour_angle())
                )
            ),
            1,
        )

    def ra_to_mm(self):
        """Transform as r_a to mm-equivalents."""
        return round(self.r_a() * 0.408, 1)

    def daylight_hours(self):
        """Calculate daylight hours from Eq. 34."""
        return round((24 / math.pi) * self.sunset_hour_angle(), 1)

    # Rs
    def solar_radiation(self):
        """
        Calculate solar radiation.

        If *radiation_s* is logged, returns the value as is. If *sunshine_hours*
        attribute of the day class is set returns solar radiation amount in mJ/m2/day.
        To convert this number to W/m2 multiply multiply it by 11.57 or divide by
        0.0864. Uses Angstrom equation (Eq. 35).

        If climate data is available, and climate is *island* location and
        station elevation is between 0-100m it uses simplified (Eq. 51). This
        equation does not use temperature data, but just solar radiation and a
        coefficient.

        If station elevation is higher than 100m and/or location is not island
        it uses (Eq. 50) that calculates solar radiation by using temperature
        data along with a *krs* constant.

        If climate is not known it assumes **n=N**, meaning daily sunshine hours
        is the same as daylight hours for the given day and location.
        """
        if self.radiation_s:
            # We need to make sure that solar radiation if set, is not
            # larger than clear-sky solar radiation
            if CHECK_RADIATION_RANGE and (self.radiation_s > self.clear_sky_rad()):
                raise ValueError(f"Solar radiation out ot range. Rso={str(self.clear_sky_rad())}")
            return self.radiation_s

        n = self.sunshine_hours
        if n is None:
            # if we are in island location we refer to equation 51 in UAN-FAO
            # paper 56
            if (
                self.station.climate
                and self.station.climate.island_location
                and self.station.altitude < 100
            ):
                ra = self.r_a()
                return round((0.7 * ra) - 4, 1)

            if self.station.climate and self.temp_min and self.temp_max:
                # We assume caller has only temperature informaiton, and no
                # information on overcast conditions. So we resort to Hargreaves
                # and Samani's radiation formula:
                climate = self.station.climate
                ra = self.r_a()
                krs = 0.16
                if climate.coastal_location:
                    krs = 0.19
                elif climate.interior_location:
                    krs = 0.16

                return round(krs * math.sqrt(self.temp_max - self.temp_min) * ra, 1)

            else:
                n = self.daylight_hours()

        if n and not isinstance(n, (int, float)):
            raise TypeError("'n' must be a number")

        if n < 0:
            raise ValueError("Observed daylight hours cannot be less than 0")

        # n cannot be more than N, which is available daylight hours
        if (n > self.daylight_hours()) and CHECK_SUNSHINE_HOURS_RANGE:
            raise ValueError("Daylight hours out of range")

        a_s = 0.25
        b_s = 0.50
        max_daylight_hours = self.daylight_hours()  # this is the maximum possible sunshine duration
        ra = self.r_a()

        return round((a_s + b_s * n / max_daylight_hours) * ra, 1)

    def solar_radiation_in_mm(self):
        """
        Convert solar radiation to mm.

        Alias to *solar_radiation(n)* but converts the output to mm equivalent,
        rounded to 1 decimal.
        """
        rs = self.solar_radiation()
        return round(rs * 0.408, 1)

    # clear-skype solar radiation
    def clear_sky_rad(self):
        """
        Calculate clear sky radiation when n=N.

        Uses (Eq. 36) for elevations below 100m. Above 100m uses (Eq. 37).
        """
        if self.station.altitude < 100:
            return round((0.25 + 0.50) * self.r_a(), 1)

        return round((0.75 + (2 * 10 ** (-5)) * self.station.altitude) * self.r_a(), 1)

    def net_solar_rad(self):
        """
        Calculate net solar or net shortwave radiation.

        Uses Crop's albedo in calculations. (Eq. 38).
        Return radiation in MJ/m2/day
        """
        ref_crop = self.station.ref_crop
        return round((1 - ref_crop.albedo) * self.solar_radiation(), 1)

    def net_longwave_rad(self):
        """Calculate net longwave radiation (Eq. 39)."""
        if not (self.temp_max and self.temp_min):
            raise AttributeError(
                "Net longwave radiation cannot be calculated without min/max temperature"
            )

        temp_max_k = self.temp_max + 273.16
        temp_min_k = self.temp_min + 273.16
        ea = self.actual_vapour_pressure()
        rs = self.solar_radiation()
        rso = self.clear_sky_rad()

        sb_constant = self.stephan_boltzmann_constant
        return round(
            sb_constant
            * ((temp_max_k**4 + temp_min_k**4) / 2)
            * (0.34 - 0.14 * math.sqrt(ea))
            * (1.35 * (rs / rso) - 0.35),
            1,
        )

    def net_radiation(self):
        """Calculate net radiation (Eq. 40)."""
        ns = self.net_solar_rad()

        try:
            nl = self.net_longwave_rad()
        except BaseException as e:
            raise (str(e)) from e

        if (ns is not None) and (nl is not None):
            return round(ns - nl, 1)

    def net_radiation_to_mm(self):
        """Convert *net_radiation()* to mm."""
        if net_radiation := self.net_radiation():
            return round(net_radiation * 0.408, 1)

    def relative_humidity(self, T):
        """Calculate relative humidity of air given temperature using vapour pressure."""
        if not isinstance(T, (int, float)):
            raise TypeError("Number is expected")
        return round(100 * (self.actual_vapour_pressure() / self.saturation_vapour_pressure(T)), 3)

    def relative_humidity_mean(self):
        """
        Calculate the mean of relative humidity.

        If possible returns mean relative humidity for the day.
        If humidity_mean was logged in the station returns it as is.
        If min/max humidity values were logged at the station, computes the mean of the two values
        If none was logged, but min/max temperature values were logged it attempts to calculate
        relative humidity through saturation vapour pressure:
        """
        if self.humidity_mean is not None:
            return self.humidity_mean

        if (self.humidity_min is not None) and (self.humidity_max is not None):
            return round((self.humidity_max + self.humidity_min) / 2, 0)

        if (self.temp_min is not None) and (self.temp_max is not None):
            return int(
                round(
                    (self.relative_humidity(self.temp_min) + self.relative_humidity(self.temp_max))
                    / 2,
                    0,
                )
            )

        return None

    def soil_heat_flux(self):
        """Calculate soil heat flux.

        Returns 0.00 (daily coefficient)
        """
        return 0.00

    def eto_hargreaves(self):
        """
        Eto estimating using Hargreaves equation.

        If wind and humidty information is available, or can be estimated by this equation
        is not recommended. ( Eq. 52 )
        """
        temp_mean = self.interpolate_temp_mean()
        return round(
            0.0023
            * (temp_mean + 17.8)
            * (self.temp_max - self.temp_min) ** 0.5
            * self.r_a(),
            2,
        )

    def eto(self):
        """Calculate evapotranspiration from Eq. 6."""
        # if we cannot get wind speed data we revert to Hargreaves formula.
        # Which is not ideal! This can happen only if user removed default 'climate'
        # reference
        if not self.wind_speed_2m():
            return self.eto_hargreaves()

        if self.interpolate_temp_mean() is None:
            raise AttributeError("Cannot calculate eto(): temp_mean (mean temperature) is missing")

        try:
            net_radiation = self.net_radiation()
        except Exception as e:
            raise (str(e)) from e

        temp_mean = self.interpolate_temp_mean()
        slope_of_vp = self.slope_of_saturation_vapour_pressure(temp_mean)
        ground_heat_flux = self.soil_heat_flux()
        u2m = self.wind_speed_2m()
        eto_nominator = (
            0.408 * slope_of_vp * (net_radiation - ground_heat_flux)
        ) + self.psychrometric_constant() * (
            900 / (temp_mean + 273)
        ) * u2m * self.vapour_pressure_deficit()

        eto_denominator = slope_of_vp + self.psychrometric_constant() * (1 + 0.34 * u2m)
        return round(eto_nominator / eto_denominator, 2)


class Climate:
    """
    Represents a default climate according to *UN-FAO Paper 56*.

    If module has to make any assumptions regarding the climate it consults
    this class for any clues. If you wish to not use any assumptions and
    rely soleley on logged station data (if such is available) you may set
    Station's *climate* attribute to *None*.

        station = Station(latitude=-20.5, altitude=200)
        station.climate = None

    If you want to set a new climate:

        humid_climate = Climate().humid().coastal().moderate_winds()

        station = Station(latitude=-20.5, altitude=200)
        station.climate = humid_climate
    """

    def __init__(self):
        """
        Instantiate Climate-class object.

        Accepts no arguments. Default initialization is as follows:

            - interior_location
            - arid_climate
            - dew_point_difference = 2
            - average_wind_speed = 2.0 m/s
            - k_rs = 0.16


        To affect these values use respected methods documented below.
        """
        self.interior_location = True
        self.coastal_location = False
        self.island_location = False

        self.arid_climate = True
        self.humid_climate = False

        # Assining default values for the climatic condition to be able to
        # calculate missing data accurately
        self.dew_point_difference = 2
        self.average_wind_speed = 2.0
        self.k_rs = 0.16

    def light_winds(self):
        """Set *average_wind_speed* to 0.5m/s."""
        self.average_wind_speed = 0.5
        return self

    def moderate_winds(self):
        """Set *average_wind_speed* to 2.0m/s."""
        self.average_wind_speed = 2
        return self

    def strong_winds(self):
        """Set average_wind_speed to 4m/s."""
        self.average_wind_speed = 4
        return self

    def arid(self):
        """Set *arid_climate* and *dew_point_difference* to 2."""
        self.arid_climate = True
        self.humid_climate = False
        self.dew_point_difference = 2
        return self

    def humid(self):
        """Set *humid_climate* and *dew_point_difference* to 0."""
        self.arid_climate = False
        self.humid_climate = True
        self.dew_point_difference = 0
        return self

    def interior(self):
        """Set *interior_location*, *k_rs* coefficient to *0.16*."""
        self.interior_location = True
        self.coastal_location = False
        self.island_location = False
        self.k_rs = 0.16
        return self

    def coastal(self):
        """Set *coastal_location*, *k_rs* to *0.19*."""
        self.interior_location = False
        self.coastal_location = True
        self.island_location = False
        self.k_rs = 0.19
        return self

    def island(self):
        """Set *island_location* and *k_rs* to 0.19."""
        self.interior_location = False
        self.coastal_location = False
        self.island_location = True
        self.k_rs = 0.19
        return self

    """
    def set_location(self, location):
        if location == "coastal":
            return self.coastal()

        if location == "interior":
            return self.interior()

        if location == "island":
            return self.island()

        return self
    """

    def __str__(self):
        """Get string representation of object."""
        location = "interior" if self.interior_location else "coastal"
        if self.arid_climate:
            humidity = "arid, or semi-arid region"
        else:
            humidity = "humid, or sub-humid region"

        return f"""
            Climate can be described as located in {location} area, {humidity}.
            Average wind speeds are estimated at {self.average_wind_speed}.
            Dew point temperature is usually runs {self.dew_point_difference}C lower than
            day's minimal observed temperature
        """


class Crop:
    """Represents reference crop as assumed by Penman-Monteith equation."""

    def __init__(self, resistance_a=208, albedo=0.23, height=0.12):
        """
        Instantiate crop class.

        Contains the following assumptions (default values):
        - resistance_a = 208 (aerodynamic resistance)
        - albedo = 0.23
        - height - 0.12
        """
        self.resistance_a = resistance_a
        self.albedo = albedo
        self.height = height


class StationDay(DayEntry):
    """Left here for backwards-compatability with earlier versions of the library."""

    pass


class MonthEntry:
    def __init__(self):
        pass


class WeekEntry:
    def __init__(self):
        pass


class HourEntry:
    def __init__(self):
        pass
