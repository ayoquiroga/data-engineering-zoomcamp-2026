import dataclasses
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from kafka import KafkaProducer
from models import Ride, ride_from_row, ride_serializer

# Download NYC green taxi trip data (first 1000 rows)
url = str(Path(__file__).parent.parent / "../green_tripdata_2025-10.parquet")
columns = ['PULocationID', 'DOLocationID', 'trip_distance', 'total_amount', 'lpep_pickup_datetime', 'lpep_dropoff_datetime', 'passenger_count', 'tip_amount']
df = pd.read_parquet(url, columns=columns)
#df = pd.read_parquet(url, columns=columns).head(1000)

server = 'localhost:9092'

producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=ride_serializer
)

t0 = time.time()

topic_name = 'green-trips'

for _, row in df.iterrows():
    ride = ride_from_row(row)
    producer.send(topic_name, value=ride)
    print(f"Sent: {ride}")
    time.sleep(0.01)

producer.flush()

t1 = time.time()
print(f'took {(t1 - t0):.2f} seconds')
