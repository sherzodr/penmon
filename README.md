# NAME

penmon - Implementation of weather station class in Python that supports 
Penman-Monteith ETo Equation.

# INSTALL

	$ pip install penmon

# USAGE

    import penmon as pm
    
    ### create a station class with known location and elevation
    station = pm.Station(latitude=41.42, altitude=109)
    station.anemometer_height = 10

	### getting a day instance for August 16th
    day = station.day_entry(238, 
    		temp_min = 19.5, 
    		temp_max = 25.6, 
    		wind_speed = 2.5,
    		humidity_mean = 65,
    		radiation_s =2 5.6
    		)
    print("ETo for this day is", day.eto() )

# DESCRIPTION

Full implementation of *Penman-Monteith* *ETo* equation based on 
[UAN-FAO Irrigation and Drainage Paper 56][1].

*Penman-Monteith* equation is used to calculate reference crop evapotranspiration *ETo* 
for a given location using available climate data. This method provides many ways of estimating
missing climate data.

Following are the least data required to estimate ETo (But the more data you provide
the better the accuracy gets):

    * latitude
    * elevation
    * date
    * daily minimum temperature
    * daily maximum temperature

It can do this by making certain assumptions about the climate. These assumptions
can be fine-tuned. *Climate*-class is responsible for setting these assumptions.
We'll talk more about it later (see Climate class below)

# OVERVIEW

To calculate *ETo*, including intermediate atmospheric data you first need to 
define an instance of a **Station** with a known *latitude* and *altitude*. Then
you request the station to create an instance of a **DayEntry**, which represents
a single day with a known date. We then set whatever data we know about that particular 
day, and ask the **day** to calculate information that we do not know, including *ETo*.

# BEWARE

This is pre-release version of the library and intended for review only. API of 
the class may change in future releases. Do not assume backwards compatability 
in future releases. Consults **CHANGES** file before upgrading!

# Station CLASS

## CREATE A STATION instance

	import penmon as pm

	station = pm.Station(latitude=41.42, altitude=109)

*latitude* must be a float between -90 and 90. *altitudu* must be a positive 
integer. These arguments values are of utmost importance. Please make sure these 
data are as accurate as you can get them be. *latitude* is used to calculate 
**sunset hour angle** (Eq. 25) and **Extraterrestrial radiation** (Eq. 21), 
which in turn, along with date, is used to calculate solar radiation!

*altitude* is used to calculate **atmospheric pressure**, which in turn is used to 
calculate **psychrometric constant**, which in turn is used to calculate **vapour pressure**,
which is used to calculate **net longwave radiation**. As you can see, these 
very innocent looking numbers are pretty much backbone of the whole equation.
Show them respect!

## ANEMOMETER HEIGHT

Above *station* assumes its anemometer height is 2m above ground surface.
If it's not, you can set the height as:

	station.anemometer_height = 10
	
Now all the wind_speed information is assumed to be wind speed at 10m
height. This is important information, since ETo is calculated with speed
close the crop surface, which is 2m. Library uses logarithmic algorithm
to convert the data accordingly. Again, important setting! Shoud you wish to 
access calculated wind speed at 2m use *wind_speed_2m()* method:

    day.wind_speed=2.0;
    u2m = day.wind_speed_2m();
    
In the above example *u2m* returns *2.0* if the anemometer was set to 2 meters.
If it was set to 10m, it returns 1.5. If it was set to 50 meters, it reads 1.2 m/s.
	
## STATION CLIMATE

Station also makes certain assumptions about its climate. You can set this
by creating a new climate instance (see **Climate** class) and set is as:

    humid_climate = pm.Climate().humid().coastal().strong_winds()
    arid_climate = pm.Climate().arid().interior().moderare_winds()
    station.climate = humid_climate

By default it assumes we are in *arid, interior location, with moderate winds*.
If it's in arid climate, it makes certain assumption about the dew point temperature. 
This temperature will be used to calculate relative humidity if humidity data
is missing. It deduces dew_point temperature by looking at the temp_min of the record. 
In particulare, for arid location it substracts 2.0 degrees from temp_min. In
humid location it treats temp_min as temp_dew. In the following example
we set dew_point temperature 4.0 below temp_min

    climate=pm.Climate() 
    # above is the same as saying:
    climate=pm.Climate().arid().interior().moderate_winds()
    
    climate.dew_point_difference=4.0
    
    station.climate=climate;

    # from now on if humidity data is missing it substtracts 4.0 degrees
    from temp_min to take a guess at temp_dew
    
## REFERENCE CROP

It assumes it will be calculating ETo for a refernce crop. According
to the original paper reference crop is assumed to be grass of 0.12m height, 
aerodynamic resistance of 70 and albedo of 0.23. It you wish to calculate ETo 
for a different reference crop you may do so as:

	different_crop = pm.Crop(resistance_a=208, albedo=0.23, height=0.12)
	station.ref_crop = different_crop
	
## ITERATE THROUGH INDIVIDUAL ENTRIES
	
Based on the above example this station has no climate data available at this 
moment. But if it were you would've been able to iterate through these records 
like following:

	for a_day in station.days:
		# do stuff with a_day

# DayEntry class

Once we have station data available we work with a day at a time. We first
need to get a single day, identified by a day number:

	day = station.day_entry(238)
	
*day* is an instance of **DayEntry** class. *238* above represents
*August 26th* - it is 238th day of the year. Day number can only be an integer
in 1-366 range. It also supports a date string:

	day = station.day_entry("2020-08-26")
	day.day_number # returns 238
	
If you have to pass a date string that has a different template than "%Y-%m-%d", 
you can pass your template string to the method as follows. Above example assumes
following default *date_template* value:

    day = station.day_entry("2020-08-26", date_template="%Y-%m-%d")
    
To learn more about date template placeholders refer to *strptime()* manual either
from *datetime* module, or by refering to your system's *strptime* manual 
(available in all linux/unix machines).

Based on this day number alone library is able to calculate inverse
of the relative Sun-Earth distance (Eq. 23), solar declination (Eq. 24), 
which is used to calculate possible daylight hours for that particular day for 
that particular latitude. It's amazing how much information we can deduce based 
on this single number!

Once you have *day* instance now all the fun begins! 

Everyday has following attributes:

	- day_number (whatever we passed to the constructor)
	- station (set automatically by station)
	
	# following are required to be set:
	- temp_min
	- temp_max
	
	# following are better to be set:
	- temp_dew
	- wind_speed
	- humidity_min
	- humidity_max
	- radiation_s	- Solar Radiation
	
	# following are optional, if above attributes are known
	- radiation_a
	- temp_mean
	- temp_dry     - dry bulb temperature
	- temp_wet     - wet bulb temperature
	
## INTERMEDIATE CALCULATIONS
	
Before setting any of the above attributes following information is available for
us. These information do not use any recorded data, but only uses
mostly astronomical calculations.

### day.atmospheric_pressure()

Returns atmostpheric pressure in kPa for station elevation. For the above example
altitude (109m) returns 100.0kpa. Atmospheric pressure is also available through
*station.atmospheric_pressure()* call. In fact, *DayEntry.atmospheric_pressure()*
is just an alias to it.

Value returned is a pressure in *kPa*. If you wish to convert it to mercury
scale multiply it by *7.50* to get *mm Hg*, or *0.295* to get *in Hg*.

### day.latent_heat_of_vaporization()

Returns 2.45

### day.specific_heat()

Returns 0.001013

### day.psychrometric_constant()

For the elevation in this example returns 0.0665.

### day.saturation_vapour_pressure(T)

Given *T* - temperature returns saturation vapour pressure. For example for T=25.0
returns 3.168 

### day.slope_of_saturation_vapour_pressure(T)

Given *T* - temperature returns slope of saturation vapour pressure curve. For example
for T=25.0 returns 0.188684

### day.relative_sun_distance()

Returns inverse of relative Earth-Sun distance. For this example returns 0.981

### day.solar_declination()

For this example returns 0.172. This is angle in radians. To convert this to 
degrees multiply by 180 and devide to *math.pi()*. For example, 0.172 rad is the
same as 9.8 degrees. So Sun's declination was 9.8 degrees north relative to equatorial
plane. If the value were negative it would've meant the Sun is declined to the 
south of the equatorial plane.

### day.sunset_hour_angle()

For this example, returns 1.725. See *day.solar_declination* to convert this
to degrees.

### day.R_a()

Returns extraterrestrial radiation in MJ/m2/day. For this given example returns 40.3.

### day.R_a_in_mm()

The same as above but in mm. 16.4 for this example.

### day.daylight_hours()

Possible daylight hours for this day. 

### day.solar_radiation()

Depends on the value of *day.sunshine_hours* attribute. Returns solar radiation
in MJ/m2/day

### day.solar_radiation_in_mm()

Same as above, but returns in mm.

### day.R_so()

Calculates Clear-Sky solar radiation.

### day.R_ns()

Given hours of direct sunlight (in *day.sunshine_hours* attribute) calculates 
net solar radiation (or shortwave radiation) Takes into account albedo of the crop. 

### day.soil_heat_flux()

Returns 0.00 for daily calculations.

## RECORDED DATA MANIPULATIONS

At this point we still cannot calculate *ETo*. some vital information are still
missing. Let's record some data for this day:

	day.temp_min = 19.5
	day.tmep_max = 25.6

Now we can calculate *ETo* for the first time:

	day.eto() # returns 3.2mm
	
To calculate ETo with the current recorded data the library did lots of assumptions
and calculations based on empirical data. Let's help it further by recording 
other important information:

	day.temp_dew = 15.0
	day.eto() # returns 3.58mm

	day.wind_speed=2.50
	day.eto()# returns 3.82mm
	
Recording solar radiation gets us the most accurate ETo:

	day.radiation_s = 25.0
	day.eto() # returns 5.04m	
	
# TODO

 * rounding consistency. Currently rounding of decimal points for floating point numbers
   follow the [original paper][1]'s usage examples. I did so in order to be able
   to test examples used in the paper. However this is far from ideal. This
   issue of significant digits must be revisited in future revisions!

 * *import_data()* must be supported by *penmon.eto.Station* class to import
   bulk data into the station.
 
 * *export_data()* must be supported by *penmon.eto.Station* class to export
   all the data (including intermediate results) into a .csv file. 
   Options for exporting data into **AquaCrop** and **CropWat** systems must be
   supported
 
 * Module only implements daily calculations. It does not support hourly or monthly
observations at this time.

# SEE ALSO


*libpenmon* - port of the current module into C++. See [github.com/sherzodr/libpenmon][2]


# AUTHOR

 Sherzod Ruzmetov <sherzodr@gmail.com>
 
 [1]: http://www.fao.org/3/X0490E/x0490e00.htm
 [2]: https://github.com/sherzodr/libpenmon
