import numpy as np
import random
import V2G.models as models
import V2G.price as price

#time:minute
class EVFlow:
    '''
    type_distribution = [daily, short, long]
    '''
    def __init__(self, num_of_EV, V2G_rate=0.8, capacity=100, type_distribution=np.array([0.1, 0.3, 0.6])):
        self.num_of_EV = num_of_EV
        self.num_of_V2G = self.num_of_EV * V2G_rate
        self.capacity = capacity
        self.type_distribution = type_distribution

    #need to complete
    def generate_init_SOC(self, type):
        if type == 'daily':
            return random.uniform(0.7, 1)
        elif type == 'short':
            return random.uniform(0.2, 0.5)
        else:
            return random.uniform(0.5, 0.9)

    def generate_daily_cars(self, num_of_EV, num_of_V2G, locs=[8*60-30, 17*60+30], scales=[10, 10]):
        '''
        arr locs and scales: [arrive_time, departure_time]
        '''
        arr_times = np.random.normal(loc=locs[0], scale=scales[0], size=num_of_EV)
        dep_times = np.random.normal(loc=locs[1], scale=scales[1], size=num_of_EV)

        car_list = []
        for i in range(num_of_EV):
            V2G = i < num_of_V2G
            car = models.Car(capacity=self.capacity, type='daily', init_SOC=self.generate_init_SOC('daily'),
                                 arr_time=arr_times[i], dep_time=dep_times[i], V2G=V2G)
            car_list.append(car)
        return car_list

    def generate_long_term_cars(self, num_of_EV, num_of_V2G, arr_locs=[12*60, 18*60], arr_scales=[60, 60], parking_loc=240, parking_scale=80):
        '''
        arr locs and scales: [arrive time peak at noon, arrive time peak at night]
        parking locs and scales: parking time
        '''
        arr_times1 = 0.5*np.random.normal(loc=arr_locs[0], scale=arr_scales[0], size=num_of_EV)
        arr_times2 = 0.5*np.random.normal(loc=arr_locs[1], scale=arr_scales[1], size=num_of_EV)
        arr_times = arr_times1 + arr_times2
        parking_times = np.random.normal(loc=parking_loc, scale=parking_scale, size=num_of_EV)
        dep_times = arr_times + parking_times
        car_list = []
        for i in range(num_of_EV):
            V2G = i < num_of_V2G
            car = models.Car(capacity=self.capacity, type='long', init_SOC=self.generate_init_SOC('long'),
                                 arr_time=arr_times[i], dep_time=dep_times[i], V2G=V2G)
            car_list.append(car)
        return car_list

    def generate_short_term_cars(self, num_of_EV, num_of_V2G, arr_locs=[12*60, 18*60], arr_scales=[60, 60], parking_loc=30, parking_scale=10):
        '''
        arr locs and scales: [arrive time peak at noon, arrive time peak at night]
        parking locs and scales: parking time
        '''
        arr_times1 = 0.5*np.random.normal(loc=arr_locs[0], scale=arr_scales[0], size=num_of_EV)
        arr_times2 = 0.5*np.random.normal(loc=arr_locs[1], scale=arr_scales[1], size=num_of_EV)
        arr_times = arr_times1 + arr_times2
        parking_times = np.random.normal(loc=parking_loc, scale=parking_scale, size=num_of_EV)
        dep_times = arr_times + parking_times
        car_list = []
        for i in range(num_of_EV):
            V2G = i < num_of_V2G
            car = models.Car(capacity=self.capacity, type='short', init_SOC=self.generate_init_SOC('short'),
                                 arr_time=arr_times[i], dep_time=dep_times[i], V2G=V2G)
            car_list.append(car)
        return car_list
    