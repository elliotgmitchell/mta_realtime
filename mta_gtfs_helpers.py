import pandas as pd

TRIPS = pd.read_csv("gtfs_static/trips.txt")
STOPS = pd.read_csv("gtfs_static/stops.txt")

# print(TRIPS.head())
# print(TRIPS.columns)

def match_full_trip_id(partial_trip_id):
    slice = TRIPS[TRIPS.trip_id.str.contains(partial_trip_id)]
    return slice.trip_id.iloc[0]
    return slice

def get_stop_name(stop_id):
    stop_slice = STOPS[STOPS.stop_id==stop_id]
    if stop_slice.shape[0]>1:
        exit("something is wrong with STOPS")
    return  stop_slice.stop_name.iloc[0]

def get_static_schedule(route_id, date="today"):
    # Join trips with calendar
    # Filter based on line (route_id), and then the day of the week
    pass

if __name__ == '__main__':
    s = match_full_trip_id("099150_C..N")
    stop_id = "A17N"
    sn = get_stop_name(stop_id)
    print(sn)
