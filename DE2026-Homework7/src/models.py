import json
import math
import dataclasses

from dataclasses import dataclass
from typing import Optional


@dataclass
class Ride:
    PULocationID: int
    DOLocationID: int
    trip_distance: float
    total_amount: float
    lpep_pickup_datetime: int  # epoch milliseconds
    lpep_dropoff_datetime: int  # epoch milliseconds
    passenger_count: Optional[int]
    tip_amount: float

def ride_from_row(row):
    return Ride(
        PULocationID=int(row['PULocationID']),
        DOLocationID=int(row['DOLocationID']),
        trip_distance=float(row['trip_distance']),
        total_amount=float(row['total_amount']),
        lpep_pickup_datetime=int(row['lpep_pickup_datetime'].timestamp() * 1000),
        lpep_dropoff_datetime=int(row['lpep_dropoff_datetime'].timestamp() * 1000),
        passenger_count=None if math.isnan(row['passenger_count']) else int(row['passenger_count']),
        tip_amount=float(row['tip_amount']),
    )


def ride_serializer(ride):
    ride_dict = dataclasses.asdict(ride)
    json_str = json.dumps(ride_dict)
    return json_str.encode('utf-8')


def ride_deserializer(data):
    json_str = data.decode('utf-8')
    ride_dict = json.loads(json_str)
    return Ride(**ride_dict)


#test_bytes = json.dumps({
#    'PULocationID': 186,
#    'DOLocationID': 79,
#    'trip_distance': 1.72,
#    'total_amount': 17.31,
#    'lpep_pickup_datetime': 1730429702000,
#    'lpep_dropoff_datetime': 1730430302000,
#    'passenger_count': 2,
#    'tip_amount': 3.5
#}).encode('utf-8')

#ride_deserializer(test_bytes)
# Ride(PULocationID=186, DOLocationID=79, trip_distance=1.72,
#      total_amount=17.31, lpep_pickup_datetime=1730429702000)