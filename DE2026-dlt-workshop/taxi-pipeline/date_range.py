import duckdb

conn = duckdb.connect('taxi_pipeline.duckdb')
result = conn.execute('''
    SELECT 
        MIN(trip_pickup_date_time) as start_date, 
        MAX(trip_dropoff_date_time) as end_date 
    FROM nyc_taxi_data.taxi_trips
''').fetchone()

print(f'Start date: {result[0]}')
print(f'End date: {result[1]}')

conn.close()
