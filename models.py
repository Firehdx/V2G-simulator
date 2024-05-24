import numpy as np
import pandas as pd
import random



def expected_SOC(init_SOC=1, is_V2G=False):
    if not is_V2G:
        p = 1
    else:
        x = random.random()
        if x <= 0.57:
            p = 0.7
        elif x <= 0.85:
            p = 0.5
        elif x <= 0.95:
            p = 0.3
        else:
            p = 0.1
    return init_SOC * p


def generate_init_SOC(type, arr_time, C):
    if type == 'daily':
        L = np.random.normal(loc=10, scale=8/3)
        SOC = max(1 - L * 0.15 / C, 0)
    else:
        t = arr_time/60
        SOC = min(1 - 0.8 * (t - 7) / 16, 1)
    return SOC
        



#capacity: kWh, power:kW, time:minute
class Car:
    def __init__(self, type, arr_time, dep_time, capacity=100, V2G=False):
        self.capacity = capacity
        self.arr_time = np.clip(arr_time, a_max=24*60-1, a_min=0)
        self.dep_time = np.clip(dep_time, a_max=24*60-1, a_min=0)
        self.V2G = V2G
        self.reward = 0
        self.parking_fee = 0
        self.park_time = self.arr_time
        
        #init car type
        if type in ['daily', 'short', 'long']:
            self.type = type
        else:
            print('car type wrong!')

        # init SOC
        self.init_SOC = generate_init_SOC(self.type, self.arr_time, capacity)
        self.SOC = self.init_SOC

        # #init expected SOC
        self.exp_SOC = expected_SOC(self.init_SOC, self.V2G)

        #init battery condition
        if self.SOC == 1:
            self.is_full = True
        else:
            self.is_full = False
        if self.SOC == self.exp_SOC:
            self.is_empty = True
        else:
            self.is_empty = False

    def get_type(self):
        return self.type

    def get_SOC(self):
        return self.SOC

    def is_V2G(self):
        return self.V2G
    
    def get_expect_SOC(self):
        return self.exp_SOC
        
    def time_info(self):
        return self.arr_time, self.dep_time, self.dep_time - self.arr_time
    
    def battery_condition(self):
        return self.is_full, self.is_empty
    
    #when charging, reward is -
    def gain_reward(self, reward):
        self.reward += reward
        return self.reward
    
    def gain_parking_fee(self, fee):
        self.parking_fee += fee
        return self.parking_fee
    
    def change_park_time(self, time):
        self.park_time = time
        return self.park_time
    
    def get_park_time(self):
        return self.park_time
    
    def get_reward(self):
        return self.reward
    
    def get_parking_fee(self):
        return self.parking_fee
    
    # Change the SOC, power is + when charge and - when discharge
    # power已在charger中除了60
    def charge_discharge(self, power, reward):
        self.SOC += power / self.capacity
        if self.SOC > 1:
            self.SOC = 1
            self.is_full = True
        if self.SOC <= self.exp_SOC:
            self.SOC = self.exp_SOC
            self.is_empty = True
        self.reward -= reward * power
        return self.is_full, self.is_empty
    
    def __repr__(self) -> str:
        if self.V2G:
            s = 'is_V2G'
        else:
            s = 'common'
        return f"({self.type:5}-{s}, time:{self.arr_time}->{self.dep_time}, SOC:{self.SOC:.3f}->{self.exp_SOC:.3f}, reward:{self.reward:.2f}, parking fee:{self.parking_fee:.2f})"



# action>0代表从车取电，<0代表给车充电，=0代表不充不放
# in_power为从车取电，out_power为给车充电
#Unit: power:kW, time:minute, capacity:kWh, so power should /60
class Charger:
    def __init__(self, in_power=20, out_power=100, V2G=False):
        self.in_power = in_power/60
        self.out_power = out_power/60
        self.V2G = V2G
        self.reward = 0
        self.start_working = False
        self.start_time = 0
        self.working_time = 0
        

    def is_V2G(self):
        return self.V2G

    def get_power(self):
        return self.in_power, self.out_power
    
    def gain_reward(self, reward):
        self.reward += reward
        return self.reward
    
    def work(self, time):
        self.working_time += 1
        if self.start_working == False:
            self.start_working = True
            self.start_time = time
        return 

    def get_working_time(self):
        return self.working_time

    def duty_ratio(self, peak_period=[8*60, 18*60]):
        return self.working_time / (peak_period[1] - peak_period[0])
    
    # not used
    # 需要矩阵化加速
    # action需要考虑car的电池容量等限制
    def eletric_charged(self, action):
        Q_in = 0
        Q_out = 0
        for i, act in enumerate(action):
            if act > 0:
                Q_in += self.in_power
            elif act < 0:
                Q_out += self.out_power
            else:
                pass
        return Q_in, Q_out

    def __repr__(self) -> str:
        if self.V2G:
            s = 'is_V2G'
        else:
            s = 'common'
        return f'({s}, charge:{self.out_power:.3f}, discharge:{self.in_power:.3f}, reward:{self.reward:.2f})'
    

        


class Satisfaction:
    '''
    price = array([price_discharge, price_charge, price_parking, price_active])
    '''
    def __init__(self, car, time_resolution=60, price=np.array([0.828, 0.331, 5, 0]), battery_loss=0.0):
        self.car = car
        self.pm, self.pv, self.pp, self.pa = price/time_resolution
        self.bt_loss = battery_loss/time_resolution

    def battery_loss(self):
        return self.bt_loss
    
    def parking_loss(self):
        return self.pp
    
    def price_active(self):
        return self.pa
    
    def reward_satisfaction(self):
        return self.pm - self.pv - self.battery_loss() - self.parking_loss()/20 + self.price_active()

    def battery_loss_intention(self):
        return np.exp(self.battery_loss()) - 1

    def SOC_intention(self):
        return 5 * self.car.get_SOC() / 3 - 0.5

    def intention_satisfaction(self, params=np.array([-1, 1])):
        intention = np.array([self.battery_loss_intention(), self.SOC_intention()])
        return np.dot(intention, params)
    
    def driver_satisfaction(self, params=np.array([0.5, 1])):
        satisfaction = np.array([self.reward_satisfaction(), self.intention_satisfaction()])
        return np.dot(satisfaction, params)


    def prob_discharge(self):
        soc = self.car.get_SOC()
        if not self.car.is_V2G():
            return 0
        if self.car.get_type() == 'short':
            return 0
        if soc > 0.9:
            return 1
        elif soc <= 0.3:
            return 0
        else:
            return 1/(1+np.exp(-5*(self.driver_satisfaction()-0.5)))
        
    def intend_discharge(self):
        if self.prob_discharge() >= 0.5:
            return True
        else:
            return False




if __name__ == '__main__':
    mycar = Car(type='daily', arr_time=8*60, dep_time=18*60, V2G=True)
    sac = Satisfaction(mycar)
    print(sac.prob_discharge())