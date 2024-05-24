import numpy as np

# time unit is hours
def price_vehicle_charge(time=23*60, mall=False):
    time /= 60
    if mall == True:
        return 1.45
    elif time >= 6 and time <= 22:
        return 0.641
    else:
        return 0.331
    
def price_vehicle_discharge(price=0.6):
    return price

def price_mall(time, month=8, transformer=1e4):
    time /= 60
    is_peek_day = time >= 6 and time <= 22
    is_peek_year = month >= 7 and month <= 9
    if transformer <= 1e3:
        if is_peek_year:
            if is_peek_day:
                return 0.853
            else:
                return 0.423
        else:
            if is_peek_day:
                return 0.825
            else:
                return 0.396
    elif transformer > 1e3 and transformer <= 1e4:
        if is_peek_year:
            if is_peek_day:
                return 0.828
            else:
                return 0.399
        else:
            if is_peek_day:
                return 0.801
            else:
                return 0.371
    else:
        if is_peek_year:
            if is_peek_day:
                return 0.804
            else:
                return 0.375
        else:
            if is_peek_day:
                return 0.776
            else:
                return 0.347
            
def price_parking(parking_time, free_time=2, price_per_hour=5, MAX=35):
    parking_time /= 60
    if parking_time <= free_time:
        return 0
    fee = price_per_hour * (parking_time - free_time)
    if fee < MAX:
        return fee
    else:
        return MAX
    
def price_active(time, price=None):
    if price:
        return price
    time /= 60
    return price_active_FM(time) + price_active_PS(time)

def price_active_FM(time):
    time = np.floor(time).astype(int)
    if time < 6 or time > 22:
        return 0
    p_6to22 = [0.063, 0.05, 0.07, 0.084, 0.105, 0.14, 0.161, 0.168, 0.19, 0.2, 0.22, 0.24, 0.21, 0.168, 0.126, 0.122, 0.105]
    return p_6to22[time-6]

def price_active_PS(time):
    return 0.5

if __name__ == '__main__':
    print(price_active(600))