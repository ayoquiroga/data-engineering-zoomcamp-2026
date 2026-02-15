-- dbt model for FHV tripdata staging
SELECT 
    -- identifiers
    dispatching_base_num,
    Affiliated_base_number as affiliated_base_number,
    cast(PUlocationID as int) as pickup_location_id,
    cast(DOlocationID as int) as dropoff_location_id,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropOff_datetime as timestamp) as dropoff_datetime,
    
    -- flags
    SR_Flag as sr_flag

FROM {{ source('raw_data', 'fhv_tripdata') }}

WHERE dispatching_base_num IS NOT NULL
