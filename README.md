# NAME

penmon.eto - Implementation of Penman-Monteith ETo Equation in Python.

# SYNOPSIS

    import penmon.eto as pm
    
    station = pm.Station(latitude=41.42, altitude=109)
    day = station.get_day(238) # August 16th
    day.temp_min = 19.5
    day.temp_max = 25.6
    
    print("ETo for this day is", day.eto)

# DESCRIPTION

Full implementation of *Penman-Monteith* *ETo* equation based on 
[UAN-FAO Irrigation and Drainage Paper 56][1].

*Penman-Monteith* equation is used to calculate reference crop evapotranspiration *ETo* 
for a given location using available climate data. This method provides many ways of estimating
missing climate data using minimal data.

Following are the least data required to estimate ETo:

    * latitude
    * elevation
    * date
    * daily minimum temperature
    * daily maximum temperature

It can do this by making certain assumptions about the climate conditions. These assumptions
can be fine-tuned. *Climate* is responsible for setting these assumptions.

By default it assumes we are in *arid, interior location, with moderate winds*. 
To adjust these assumptions you can define your own *Climate* class and assign 
this instance to the station:

    humid_climate = pm.Climate().humid().coastal().strong_winds()

    station = pm.Station(41.42, 109)
    station.climate = climate
    
If you do not want it to make any assumptions about its climate you may set *climate* attribute
of the Station to *None*:

    station = pm.Station(41.42, 109)
    station.climate = None

In this case, if humidity and wind information are missing, instead of trying to guess missing data
it relies on Haargresves' *ETo* equation (Eq 52). 

Whenever appropriate reference to Equations used in [UN-FAO Paper 56][1] are made.

# TODO

 * *import_data()* must be supported by *penmon.eto.Station* class to import
   bulk data into the station.
 
 * *export_data()* must be supported by *penmon.eto.Station* class to export
   all the data (including intermediate results) into a .csv file. 
   Options for exporting data into **AquaCrop** and **CropWat** systems must be
   supported
 
 * Module only implements daily calculations. It does not support hourly or monthly
observations at this time.

# AUTHOR

 Sherzod Ruzmetov <sherzodr@gmail.com>
 
 
 [1]: http://www.fao.org/3/X0490E/x0490e00.htm
