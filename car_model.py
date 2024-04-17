import numpy as np
import pandas as pd
import random



class Car:
    def __init__(self, capacity, type, init_SOC, arr_time, dep_time, V2G=False, expect_SOC=1, min_max_SOC=(0,1)):
        self.capacity = capacity
        self.init_SOC = init_SOC
        self.SOC = init_SOC
        self.arr_time = arr_time
        self.dep_time = dep_time
        self.V2G = V2G
        self.expect_SOC = expect_SOC
        self.min_SOC, self.max_SOC = min_max_SOC
        self.reward = 0
        if self.SOC == self.max_SOC:
            self.is_full = True
        else:
            self.is_full = False

        if self.SOC == self.min_SOC:
            self.is_empty = True
        else:
            self.is_empty = False
        
        if type == 'work':
            self.type = 2
        elif type == 'long':
            self.type = 0
        elif type == 'short':
            self.type = 1
        else:
            print('car type error!')
            self.type = -1

    def get_SOC(self):
        return self.SOC
    
    def get_expect_SOC(self):
        return self.expect_SOC
    
    def get_min_max_SOC(self):
        return self.min_SOC, self.max_SOC
    
    def is_V2G(self):
        return self.V2G
    
    def is_fully_charged(self):
        return self.is_full
    
    def is_fully_discharged(self):
        return self.is_empty
    
    # Change the SOC
    def charge_discharge(self, power):
        self.SOC += power / self.capacity
        if self.SOC > self.max_SOC:
            self.SOC = self.max_SOC
            self.is_full = True
        if self.SOC <= self.min_SOC:
            self.SOC = self.min_SOC
            self.is_empty = True
        return self.is_full, self.is_empty



# action>0代表从车取电，<0代表给车充电，=0代表不充不放
# in_power为从车取电，out_power为给车充电
class Charger:
    def __init__(self, in_power, out_power, is_V2G):
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
        


# 假定car在每一个时间帧里只有充电和放电两种状态， 从Charger中读取
class Satisfaction:
    def __init__(self, car, time_resolution=60, price=np.array([0.828, 0.331, 5]), battery_loss=0.05):
        self.car = car
        self.pm, self.pv, self.pp = price/time_resolution
        self.bt_loss = battery_loss/time_resolution

    def battery_loss(self):
        return self.bt_loss
    
    def parking_loss(self):
        return self.pp
    
    def reward_satisfaction(self):
        return self.pm - self.pv - self.battery_loss() - self.parking_loss()/20



    def random_intention(self, n0=0.1):
        return 1 + random.uniform(-n0, n0)

    def battery_loss_intention(self):
        return np.exp(1+self.battery_loss()) - np.e

    def SOC_intention(self):
        SOC_exp = self.car.get_expect_SOC()
        _, SOC_full = self.car.get_min_max_SOC()
        return np.log(SOC_exp/SOC_full +1)
    


    def intention_satisfaction(self, params=np.array([1, -1, -0.5])):
        intention = np.array([self.random_intention(), self.battery_loss_intention(), self.SOC_intention()])
        return np.dot(intention, params)
    
    def driver_satisfaction(self, params=np.array([0.85, 0.18])):
        satisfaction = np.array([self.reward_satisfaction(), self.intention_satisfaction()])
        return np.dot(satisfaction, params)




if __name__ == '__main__':
    mycar = Car(100, 0, 0, 1, True, 1, (0,1))
    sac = Satisfaction(mycar)
    print(sac.reward_satisfaction()*60)