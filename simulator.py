import numpy as np
import matplotlib.pyplot as plt

import objectGenerator as Gen
import price as P
import models as M


def update(evFlow, parkingArea, time, discharge_price, active_price, month=8, dep_after_discharged=False):
    car_wait = evFlow.get_waiting_list()
    car_list = evFlow.get_EVFlow()
    car_leave = evFlow.get_leaved_list()
    car_pairs = parkingArea.get_charger_car_pairs()

    # park the waiting car
    # parking time is decreasing when waiting
    # if time >= departure time, car leaves instead
    if car_wait:
        del_idx = []
        for idx, car in enumerate(car_wait):
            if car.time_info()[1] <= time:
                car_leave.append(car)
                del_idx.append(idx)
                continue
            sac = M.Satisfaction(car=car, 
                price=np.array([P.price_vehicle_discharge(discharge_price), P.price_vehicle_charge(), P.price_parking(car.time_info()[1]-time), P.price_active((time+car.time_info()[1])/2, active_price)]))
            v2g = sac.intend_discharge()
            if parkingArea.park_a_car(car, v2g):
                car.change_park_time(time)
                #car.gain_reward(-P.price_parking(time-car.time_info()[1]))
                del_idx.append(idx)
        del_idx.sort(reverse=True)
        if del_idx:
            for idx in del_idx:
                car_wait.pop(idx)

    # park the coming car
    if car_list:
        while car_list[0].time_info()[0] <= time:
            car = car_list[0]
            sac = M.Satisfaction(car=car, 
                price=np.array([P.price_vehicle_discharge(discharge_price), P.price_vehicle_charge(), P.price_parking(car.time_info()[2]), P.price_active((car.time_info()[0]+car.time_info()[1])/2, active_price)]))
            v2g = sac.intend_discharge()
            if parkingArea.park_a_car(car, v2g):
                #car.gain_reward(-P.price_parking(car.time_info()[2]))
                pass
            else:
                car_wait.append(car)
            car_list.pop(0)
            if not car_list:
                break
    
    # depart the leaving car
    leaving_list = parkingArea.car_leave(time, dep_after_discharged)
    car_leave += leaving_list

    # charge the parking car
    for idx, pair in car_pairs.items():
        charger, car = pair
        if car:
            if charger.is_V2G() and not car.battery_condition()[1]:
                in_power = charger.get_power()[0]
                car.charge_discharge(power=-in_power, reward=(P.price_vehicle_discharge() - P.price_vehicle_charge() + P.price_active(time)))
                charger.gain_reward((P.price_mall(time, month) - P.price_vehicle_discharge())*in_power)
                charger.work(time)



def run(evFlow, parkingArea, time=24*60, discharge_price=0.6, active_price=None, display_time=[24*60-1], dep_after_discharged=False, log_file='log/log.txt'):
    with open(f'{log_file}', 'w') as f:
        evFlow_reward = 0
        park_reward = 0
        occupy_rate_list = []
        parking_num_list = []
        for t in range(time):
            update(evFlow, parkingArea, t, discharge_price, active_price, dep_after_discharged)
            if t in display_time:
                f.write(f'##################time is {t}####################\n')
                f.write(repr(evFlow))
                f.write(repr(parkingArea))
                evFlow_reward = evFlow.get_reward()
                park_reward = parkingArea.get_reward()
                occupy_rate = parkingArea.get_occupy_rate_v2g()
                parking_num = parkingArea.get_parking_num()
                occupy_rate_list.append(occupy_rate)
                parking_num_list.append(parking_num)
                f.write(f'EV reward:{evFlow_reward:.3f}, parking area reward:{park_reward:.3f}, v2g charger occupy rate:{occupy_rate:.3f}\n')
                f.write('##################################################\n')
        evFlow_reward = evFlow.get_reward()
        park_reward = parkingArea.get_reward()

        arr_times = []
        arr_nums = [0 for _ in range(24)]
        time_intervals = [i*60 for i in range(25)]
        for car in evFlow.get_leaved_list():
            arr_time = car.time_info()[0]
            arr_times.append(arr_time)
            for i in range(len(time_intervals)-1):
                if arr_time  <= time_intervals[i+1] and arr_time > time_intervals[i]:
                    arr_nums[i] += 1



        print(f'done! EV reward:{evFlow_reward:.3f}, parking area reward:{park_reward:.3f}')
        f.write(f'done! EV reward:{evFlow_reward:.3f}, parking area reward:{park_reward:.3f}\n')
        f.write(f'output: EV reward:{evFlow_reward:.3f}, parking area reward:{park_reward:.3f}, occupy_rate:{occupy_rate_list}, arrive_nums:{arr_nums}')
    return parking_num_list




if __name__ == '__main__':
    num_of_charger = 800
    num_of_EV = 1000
    discharge_price = 0.6
    active_price = None
    log_file = f'log/log_{num_of_charger}_{num_of_EV}_{discharge_price}_{active_price}.txt'


    display_time = [i for i in range(24*60)]
    #display_time=[8*60, 12*60, 18*60]
    for i in range(1):
        flow = Gen.EVFlow(num_of_EV=num_of_EV, V2G_rate=0.8)
        lot = Gen.Parking_area(num_of_charger=num_of_charger, V2G_rate=0.5)
        out = run(flow, lot, time=24*60, display_time=display_time, dep_after_discharged=False, log_file=log_file)


        plt.plot(out)
        plt.show()
    # print(update(flow, lot, time))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    # print('car_list:')
    # print(flow.get_EVFlow())
    # print('car_waiting:')
    # print(flow.get_waiting_list())
    # print('car_leaved:')
    # print(flow.get_leaved_list())
    # print('chargers:')
    # print(lot.get_charger_car_pairs())
