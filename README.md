# V2G
 A V2G simulator and reward calculater

## Environment
python >= 3.9
numpy

## Files
models.py: Base models of cars and chargers, with a calculator of drivers' satisfaction and probability of V2G.

price.py: Price model of charge, discharge, parking, etc.

objectGenerator.py: Generate EVFlow (list of cars coming, waiting and leaved), ParkingArea (cars charging).

simulator.py: main file of simulation and display.

## Params:
In simulator.py, run(evFlow, parkingArea, time). 

**Param: time** is the time length of simulation i.e. 24*60 for a day.

**Param: evFlow** is the EVFlow model in objectGenerator.py. 
evFlow(num_of_EV, V2G_rate, capacity, type_distribution, params_daily, params_short, params_long)

type_distribution: rate of daily, short and long term cars.

params_daily: array(\[[arr_loc, dep_loc], [arr_scale, dep_scale]])
*loc represents mean and scale represents std.*

params_short: array(\[[arr1_loc, arr2_loc], [arr1_scale, arr2_scale], [parking_loc, parking_scale]])
*arrive1 is the peak time at moon and arrive2 at night, parking_loc is the mean of parking time.*

params_long: array(\[[arr1_loc, arr2_loc], [arr1_scale, arr2_scale], [parking_loc, parking_scale]])

**Param: parkingArea** is the Parking_area model in objectGenerator.py.
Parking_area(num_of_charger, V2G_rate, charger_params)

V2G_rate: rate of chargers that support V2G

charger_params: array(\[discharge power, charger power])

## Problems
1. Parking fee is pre-calculated and add to reward before the car's departure.
2. Missing part of init_SOC model.
3. Missing part of dispatch of discharged cars.
4. Missing part of waiting penalty on satisfaction.
5. Missing part of active_price model.
6. Missing part of common car charging model.