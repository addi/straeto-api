import datetime
import time

current_bus_day_time = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

print current_bus_day_time

cache_end_time = current_bus_day_time.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(hours=24)

print cache_end_time

print (cache_end_time - current_bus_day_time).seconds