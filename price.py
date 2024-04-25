
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
            
def price_parking(parking_time):
    parking_time /= 60
    if parking_time <= 2:
        return 0
    elif parking_time <= 9:
        return 5*(parking_time-2)
    else:
        return 35
    
def price_active():
    return 0