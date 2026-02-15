-- dbt model for yellow tripdata staging
SELECT 

--identifiers
cast(vendorid as int) as vendor_id,
cast(ratecodeid as int) as rate_code_id,
cast(pulocationid as int) as pickup_location_id,
cast(dolocationid as int) as dropoff_location_id,

--timestamps
cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,

--trips info
store_and_fwd_flag as store_and_fwd_flag,
cast(passenger_count as int) as passenger_count,
cast(trip_distance as float) as trip_distance,
cast(1 as int) as trip_type,
'Yellow' as service_type,

--payment info
cast(fare_amount as float) as fare_amount,
cast(extra as float) as extra,
cast(mta_tax as float) as mta_tax,
cast(tip_amount as float) as tip_amount,
cast(tolls_amount as float) as tolls_amount,
cast(improvement_surcharge as float) as improvement_surcharge,
cast(total_amount as float) as total_amount,
cast(payment_type as int) as payment_type


FROM {{ source('raw_data', 'yellow_tripdata') }}

WHERE vendorid is not null