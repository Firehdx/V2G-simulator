import numpy as np

import objectGenerator as Gen
import price as P
import models as M


def update(evFlow, parkingArea, time):
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
                price=np.array([P.price_vehicle_discharge(), P.price_vehicle_charge(), P.price_parking(car.time_info()[1]-time), P.price_active()]))
            v2g = sac.intend_discharge()
            if parkingArea.park_a_car(car, v2g):
                car.gain_reward(-P.price_parking(time-car.time_info()[1]))
                del_idx.append(idx)
                if v2g:
                    car.gain_reward(P.price_active())
        del_idx.sort(reverse=True)
        if del_idx:
            for idx in del_idx:
                car_wait.pop(idx)

    # park the coming car
    if car_list:
        while car_list[0].time_info()[0] <= time:
            car = car_list[0]
            sac = M.Satisfaction(car=car, 
                price=np.array([P.price_vehicle_discharge(), P.price_vehicle_charge(), P.price_parking(car.time_info()[2]), P.price_active()]))
            v2g = sac.intend_discharge()
            if parkingArea.park_a_car(car, v2g):
                car.gain_reward(-P.price_parking(car.time_info()[2]))
                if v2g:
                    car.gain_reward(P.price_active())
            else:
                car_wait.append(car)
            car_list.pop(0)
            if not car_list:
                break
    
    # depart the leaving car
    leaving_list = parkingArea.car_leave(time)
    car_leave += leaving_list

    # charge the parking car
    for idx, pair in car_pairs.items():
        charger, car = pair
        if car:
            if charger.is_V2G() and not car.battery_condition()[1]:
                in_power = charger.get_power()[0]
                car.charge_discharge(power=-in_power, reward=(P.price_vehicle_discharge() - P.price_vehicle_charge()))
                charger.gain_reward((P.price_mall(time) - P.price_vehicle_discharge())*in_power)



def run(evFlow, parkingArea, time=24*60, display_time=[24*60-1]):
    evFlow_reward = 0
    park_reward = 0
    for t in range(time):
        update(evFlow, parkingArea, t)
        if t in display_time:
            print(f'###############time is {t}#################')
            print(evFlow)
            print(parkingArea)
            print('############################################')
    for car in evFlow.get_leaved_list():
        evFlow_reward += car.gain_reward(0)
    park_reward = parkingArea.get_reward()
    print(f'done! EV reward:{evFlow_reward:.3f}, parking area reward:{park_reward:.3f}')

if __name__ == '__main__':
    flow = Gen.EVFlow(num_of_EV=10)
    lot = Gen.Parking_area(5, 0.5)
    
    # print(update(flow, lot, time))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    # print('car_list:')
    # print(flow.get_EVFlow())
    # print('car_waiting:')
    # print(flow.get_waiting_list())
    # print('car_leaved:')
    # print(flow.get_leaved_list())
    # print('chargers:')
    # print(lot.get_charger_car_pairs())

    run(flow, lot, time=24*60, display_time=[8*60, 17*60, 24*60-1])