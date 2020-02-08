"""
mta_schedule.py
Elliot G Mitchell
Aug 2019

First attempt to parse MTA realtime API data feed

Borrowed code to parse GTFS realtime from Chris Griffin
https://github.com/chris-griffin/real-time

List of Subway Feeds: http://datamine.mta.info/list-of-feeds

MTA Status API (XML): http://web.mta.info/status/ServiceStatusSubway.xml

MTA GTFS Realtime refernence PDF: http://datamine.mta.info/sites/all/files/pdfs/GTFS-Realtime-NYC-Subway%20version%201%20dated%207%20Sep.pdf

GTFS reference (static): https://developers.google.com/transit/gtfs/
                         https://developers.google.com/transit/gtfs/reference/
GTFS reference (realtime): https://developers.google.com/transit/gtfs-realtime/
                           https://developers.google.com/transit/gtfs-realtime/reference/
"""

import os
import math
import requests

import pandas as pd

from datetime import datetime
from google.transit import gtfs_realtime_pb2

from mta_gtfs_helpers import get_stop_name, match_full_trip_id

# get API key fron env vars
MTA_KEY = os.getenv("MTA_API_KEY")

# TODO: FEED_ID
FEED_ID = "26" #ACE
# FEED_ID = "21" #BDFM

stop_id = "A17N"
# stop_id = "A17S"
# stop_id = "A12N" # 145th st on the AC line
# stop_id = "D13N" # 145th st on the BD line
# Interesting note: transfers.txt incorporates this time distance

### Load static stops data
# stops_df = pd.read_csv("google_transit/stops.txt")
# print(stops_df)

### Call the API
mtafeed = gtfs_realtime_pb2.FeedMessage()
url = 'http://datamine.mta.info/mta_esi.php?key=' + MTA_KEY + '&feed_id=' + FEED_ID
# print(url)
response = requests.get(url)
# response = requests.get('http://datamine.mta.info/mta_esi.php?key=' + MTA_KEY)
# print(response.content)
mtafeed.ParseFromString(response.content)

def human_time(timestamp):
    pass


current_time = datetime.now()

"""
There seem to be two kinds of entities:
1. trip_update ; includes real time stop_time_update info for each stop left on the trip
    id: "000001A"
    trip_update {
      trip {
        trip_id: "063500_A..N"
        start_time: "10:35:00"
        start_date: "20190914"
        route_id: "A"
      }
      stop_time_update {
        arrival {
          time: 1568477533
        }
        departure {
          time: 1568477533
        }
        stop_id: "A03N"
      }
      stop_time_update {
        arrival {
          time: 1568477634
        }
        departure {
          time: 1568477634
        }
        stop_id: "A02N"
      }
    }
2. vehicle ; shows the current location of the train for this trip_id
    id: "000012A"
    vehicle {
      trip {
        trip_id: "066941_A..S"
        start_time: "11:09:25"
        start_date: "20190914"
        route_id: "A"
      }
      current_stop_sequence: 23
      timestamp: 1568477533
      stop_id: "A48"
    }
"""


for entity in mtafeed.entity:
    # print()
    # print(entity)
    # input()

    if not entity.trip_update:
        # print(entity.keys())
        continue

    for update in entity.trip_update.stop_time_update:
        if update.stop_id == stop_id:
            # print(entity)
            # input()
            # print(entity.id)
            # print(update)
            # print(entity.trip_update.trip.trip_id)
            # print(update.arrival.time)
            arrival_time = update.arrival.time
            if arrival_time <= 0:
                arrival_time = update.departure.time
            arrival_time = datetime.fromtimestamp(arrival_time)
            # arrival_minutes = math.trunc(((time - current_time).total_seconds()) / 60)
            arrival_minutes = math.trunc(((arrival_time - current_time).total_seconds()) / 60)
            arrival_minutes_seconds = math.trunc(((arrival_time - current_time).total_seconds()) % 60)
            # print(time)
            # print(arrival_minutes)
            # print(arrival_minutes_seconds)

            stop_name = get_stop_name(stop_id)
            if update.arrival.time % 60 == 0:
                realtime_guess = False
            else: realtime_guess = True

            trip_id = entity.trip_update.trip.trip_id
            try:
                full_trip_id = match_full_trip_id(trip_id)
            except Exception as e:
                full_trip_id = "UNABLE_TO_MATCH"


            # print("Trip {trip_id} will arrive at stop {stop_id} in {arrival_minutes} min and {arrival_minutes_seconds} seconds".format(
            print("Trip {trip_id} will arrive at {stop_name} at {eta} ({arrival_minutes} min and {arrival_minutes_seconds} seconds) - realtime:{realtime_guess}".format(
                trip_id=trip_id,
                stop_name=stop_name,
                arrival_minutes=arrival_minutes,
                arrival_minutes_seconds=arrival_minutes_seconds,
                eta=arrival_time.strftime("%Y-%m-%d %H:%M:%S %p"),
                raw_time=update.arrival.time,
                realtime_guess=realtime_guess
            ))
            print("\tI think this is a part of trip {full_trip_id}".format(full_trip_id=full_trip_id))



# import pdb; pdb.set_trace()
