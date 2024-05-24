import numpy as np
import random
import models as models
import price as P

#time:minute
class EVFlow:
    '''
    type_distribution = [daily, short, long]
    '''
    def __init__(self, num_of_EV, V2G_rate=0.8, capacity=100, type_distribution=np.array([0.1, 0.3, 0.6]),
                  params_daily=np.array([[8*60-30, 17*60+30], [30, 30]]),
                  params_short=np.array([[10*60, 18*60], [240, 240], [30, 10]]),
                  params_long=np.array([[10*60, 18*60], [240, 240], [240, 80]])):
        self.num_of_EV = num_of_EV
        self.num_of_V2G = self.num_of_EV * V2G_rate
        self.capacity = capacity
        self.type_distribution = type_distribution
        self.num_type = np.rint(self.num_of_EV * type_distribution).astype(int)
        self.num_type_V2G = np.rint(self.num_of_V2G * type_distribution).astype(int)
        self.car_list = []
        self.car_list += self.generate_daily_cars(num_of_EV=self.num_type[0], num_of_V2G=self.num_type_V2G[0],
                                locs=params_daily[0], scales=params_daily[1])
        self.car_list += self.generate_short_term_cars(num_of_EV=self.num_type[1], num_of_V2G=self.num_type_V2G[1],
                                arr_locs=params_short[0], arr_scales=params_short[1],
                                parking_loc=params_short[2, 0], parking_scale=params_short[2, 1])
        self.car_list += self.generate_long_term_cars(num_of_EV=self.num_type[2], num_of_V2G=self.num_type_V2G[2],
                                arr_locs=params_long[0], arr_scales=params_long[1],
                                parking_loc=params_long[2, 0], parking_scale=params_long[2, 1])
        self.car_list = sorted(self.car_list, key=lambda car: car.time_info()[0])
        self.car_leave = []
        self.car_wait = []

    def get_EVFlow(self):
        return self.car_list
    
    def car_waiting(self, car):
        self.car_wait.append(car)

    def get_waiting_list(self):
        return self.car_wait
    
    def car_leaving(self, car):
        self.car_leave.append(car)

    def get_leaved_list(self):
        return self.car_leave

    def display_EVFlow(self):
        for i, car in enumerate(self.car_list):
            print(car)

        
    def generate_daily_cars(self, num_of_EV, num_of_V2G, locs=[8*60-30, 17*60+30], scales=[10, 10]):
        '''
        arr locs and scales: [arrive_time, departure_time]
        '''
        arr_times = np.rint(np.random.normal(loc=locs[0], scale=scales[0], size=num_of_EV)).astype(int)
        dep_times = np.rint(np.random.normal(loc=locs[1], scale=scales[1], size=num_of_EV)).astype(int)

        car_list = []
        for i in range(num_of_EV):
            V2G = i < num_of_V2G
            car = models.Car(capacity=self.capacity, type='daily', arr_time=arr_times[i], dep_time=dep_times[i], V2G=V2G)
            car_list.append(car)
        return car_list

    #arr_scales=[60, 60]
    def generate_long_term_cars(self, num_of_EV, num_of_V2G, arr_locs=[12*60, 18*60], arr_scales=[60, 60], parking_loc=240, parking_scale=80):
        '''
        arr locs and scales: [arrive time peak at noon, arrive time peak at night]
        parking locs and scales: parking time
        '''
        arr_times1 = 0.5*np.random.normal(loc=arr_locs[0], scale=arr_scales[0], size=num_of_EV)
        arr_times2 = 0.5*np.random.normal(loc=arr_locs[1], scale=arr_scales[1], size=num_of_EV)
        arr_times = np.rint(arr_times1 + arr_times2).astype(int)
        parking_times = np.random.normal(loc=parking_loc, scale=parking_scale, size=num_of_EV)
        dep_times = np.rint(arr_times + parking_times).astype(int)
        car_list = []
        for i in range(num_of_EV):
            V2G = i < num_of_V2G
            car = models.Car(capacity=self.capacity, type='long', arr_time=arr_times[i], dep_time=dep_times[i], V2G=V2G)
            car_list.append(car)
        return car_list

    def generate_short_term_cars(self, num_of_EV, num_of_V2G, arr_locs=[12*60, 18*60], arr_scales=[60, 60], parking_loc=30, parking_scale=10):
        '''
        arr locs and scales: [arrive time peak at noon, arrive time peak at night]
        parking locs and scales: parking time
        '''
        arr_times1 = 0.5*np.random.normal(loc=arr_locs[0], scale=arr_scales[0], size=num_of_EV)
        arr_times2 = 0.5*np.random.normal(loc=arr_locs[1], scale=arr_scales[1], size=num_of_EV)
        arr_times = np.rint(arr_times1 + arr_times2).astype(int)
        parking_times = np.random.normal(loc=parking_loc, scale=parking_scale, size=num_of_EV)
        dep_times = np.rint(arr_times + parking_times).astype(int)
        car_list = []
        for i in range(num_of_EV):
            V2G = i < num_of_V2G
            car = models.Car(capacity=self.capacity, type='short', arr_time=arr_times[i], dep_time=dep_times[i], V2G=V2G)
            car_list.append(car)
        return car_list

    def get_reward(self):
        reward = 0
        if self.car_list:
            for car in self.car_list:
                reward += car.gain_reward(0)
        if self.car_leave:
            for car in self.car_leave:
                reward += car.gain_reward(0)
        if self.car_wait:
            for car in self.car_wait:
                reward += car.gain_reward(0)
        return reward
    
    def __repr__(self) -> str:
        str = f'cars coming: {len(self.car_list)}\n'
        for car in self.car_list:
            str += f'{car}\n'
        str += f'cars waiting: {len(self.car_wait)}\n'
        for car in self.car_wait:
            str += f'{car}\n'       
        str += f'cars leaved: {len(self.car_leave)}\n'
        for car in self.car_leave:
            str += f'{car}\n'    
        return str
    

class Parking_area:
    def __init__(self, num_of_charger=100, V2G_rate=0.5, charger_params=[20, 100]):
        self.num_of_charger = num_of_charger
        self.num_of_V2G = int(num_of_charger*V2G_rate)
        self.charger_car_pair = {}
        self.reward = 0
        self.parking_num = 0
        for i in range(self.num_of_charger):
            if i < self.num_of_V2G:
                self.charger_car_pair[i] = (models.Charger(in_power=charger_params[0], out_power=charger_params[1], V2G=True), None)
            else:
                self.charger_car_pair[i] = (models.Charger(in_power=charger_params[0], out_power=charger_params[1], V2G=False), None)

    def get_charger_car_pairs(self):
        return self.charger_car_pair
    
    def has_space(self):
        for pair in self.charger_car_pair.values():
            if pair[1] == None:
                return True
        return False

    def has_space_V2G(self):
        for pair in self.charger_car_pair.values():
            if pair[1] == None and pair[0].is_V2G():
                return True
        return False

    def has_space_common(self):
        for pair in self.charger_car_pair.values():
            if pair[1] == None and not pair[0].is_V2G():
                return True
        return False
    
    def get_parking_num(self):
        return self.parking_num

    # if driver is not intend to v2g, then param v2g = false, though the car may support v2g.
    def park_a_car(self, car, v2g):
        if v2g:
            space = self.has_space_V2G()
        else:
            space = self.has_space_common()
        if not space:
            return False
        for idx, pair in self.charger_car_pair.items():
            if pair[1] == None and pair[0].is_V2G() == v2g:
                self.charger_car_pair[idx] = (pair[0], car)
                self.parking_num += 1
                return True
            
    def car_leave(self, time, dep_after_discharged=False):
        leaving_list = []
        for idx, pair in self.charger_car_pair.items():
            if pair[1] != None:
                if pair[1].time_info()[1] <= time:
                    pair[1].gain_parking_fee(P.price_parking(time-pair[1].get_park_time()))
                    leaving_list.append(pair[1])
                    self.charger_car_pair[idx] = (pair[0], None)
                    self.parking_num -= 1
                elif dep_after_discharged and pair[1].get_SOC() <= pair[1].get_expect_SOC():
                    pair[1].gain_parking_fee(P.price_parking(time-pair[1].get_park_time()))
                    leaving_list.append(pair[1])
                    self.charger_car_pair[idx] = (pair[0], None)
                    self.parking_num -= 1
        return leaving_list
        
    def get_reward(self):
        reward = 0
        for pair in self.charger_car_pair.values():
            reward += pair[0].gain_reward(0)
        self.reward = reward
        return reward
    
    def get_avg_duty_ratio_v2g(self):
        avg_duty_ratio = 0
        for pair in self.charger_car_pair.values():
            if pair[0].is_V2G():
                avg_duty_ratio += pair[0].duty_ratio()
        avg_duty_ratio /= self.num_of_V2G
        return avg_duty_ratio
    
    def get_occupy_rate_v2g(self):
        occupy_rate = 0
        for pair in self.charger_car_pair.values():
            if pair[0].is_V2G() and pair[1] != None:
                occupy_rate += 1
        occupy_rate /= self.num_of_V2G
        return occupy_rate
    
    def __repr__(self) -> str:
        str = f'num of chargers:{len(self.charger_car_pair)}, {self.parking_num} cars parking\n'
        for idx, pair in self.charger_car_pair.items():
            charger, car = pair
            str += f'charger:{charger}-->car:{car}\n'
        return str
    
        

if __name__ == '__main__':
    flow = EVFlow(num_of_EV=100)
    #flow.display_EVFlow()
    car1 = models.Car('daily', 7*60, 18*60, V2G=True)
    car2 = models.Car('daily', 7*60, 18*60, V2G=False)
    lot = Parking_area(2, 0.5)
    print(lot.has_space())
    lot.park_a_car(car1)
    print(lot.has_space())
    print(lot.charger_car_pair)