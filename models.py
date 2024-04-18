import numpy as np
import pandas as pd
import random


#capacity: kWh, power:kW, time:minute
class Car:
    def __init__(self, type, arr_time, dep_time, init_SOC=1, capacity=100, V2G=False):
        self.capacity = capacity
        self.init_SOC = init_SOC
        self.SOC = init_SOC
        self.arr_time = arr_time
        self.dep_time = dep_time
        self.V2G = V2G
        self.reward = 0
        if self.SOC == 1:
            self.is_full = True
        else:
            self.is_full = False

        if self.SOC == 0:
            self.is_empty = True
        else:
            self.is_empty = False
        
        if type in ['daily', 'short', 'long']:
            self.type = type
        else:
            print('car type wrong!')

    def get_type(self):
        return self.type

    def get_SOC(self):
        return self.SOC
    
    def get_expect_SOC(self):
        if not self.V2G:
            return 1
        x = random.random()
        if x <= 0.57:
            return 0.7
        elif x <= 0.85:
            return 0.5
        elif x <= 0.95:
            return 0.3
        else:
            return 0.1
        
    def parking_time(self):
        return self.dep_time - self.arr_time
    
    def is_V2G(self):
        return self.V2G
    
    def is_fully_charged(self):
        return self.is_full
    
    def is_fully_discharged(self):
        return self.is_empty
    
    # Change the SOC
    def charge_discharge(self, power):
        self.SOC += power / self.capacity
        if self.SOC > 1:
            self.SOC = 1
            self.is_full = True
        if self.SOC <= 0:
            self.SOC = 0
            self.is_empty = True
        return self.is_full, self.is_empty



# action>0代表从车取电，<0代表给车充电，=0代表不充不放
# in_power为从车取电，out_power为给车充电
class Charger:
    def __init__(self, in_power=20, out_power=100, is_V2G=False):
        self.in_power = in_power
        self.out_power = out_power
        self.is_V2G = is_V2G

    def get_power(self):
        return self.in_power, self.out_power
    
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
        return 
        


class Satisfaction:
    '''
    price = array([price_discharge, price_charge, price_parking, price_active])
    '''
    def __init__(self, car, time_resolution=60, price=np.array([0.828, 0.331, 5, 0]), battery_loss=0.05):
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
        if soc > 0.9:
            return 1
        elif soc <= 0.3:
            return 0
        else:
            return 1/(1+np.exp(-5*(self.driver_satisfaction()-0.5)))




if __name__ == '__main__':
    mycar = Car(type='daily', arr_time=8*60, dep_time=18*60, init_SOC=0.7, V2G=True)
    sac = Satisfaction(mycar)
    print(sac.prob_discharge())