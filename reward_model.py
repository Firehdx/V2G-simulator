import numpy as np
import car_model

class EVFlow:
    def __init__(self, num_of_cars, EV_rate, V2G_rate, capacity, ):
        self.num_of_EV = num_of_cars * EV_rate
        self.num_of_V2G = self.num_of_EV * V2G_rate
        self.capacity = capacity

    def generate_work_cars(self, num, locs, scales):
        arr_times = np.random.normal(loc=locs[0], scale=scales[0], size=num)
        dep_times = np.random.normal(loc=locs[1], scale=scales[1], size=num)
        car_list = []
        for i in range(num):
            car = car_model.Car(capacity=self.capacity, type='work', init_SOC=0.8,
                                 arr_time=arr_times[i], dep_time=dep_times[i], )

    def generate_long_term_cars(self):
        pass

    def generate_short_term_cars(self):
        pass
    