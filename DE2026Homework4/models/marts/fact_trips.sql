{{ config(materialized='table') }}

with trips_deduped as (
    -- Usar DISTINCT ON para deduplicar (más eficiente que ROW_NUMBER en memoria)
    select distinct on (
        vendor_id,
        pickup_datetime,
        pickup_location_id,
        dropoff_location_id
    )
        *
    from {{ ref('int_trips_unioned') }}
    order by 
        vendor_id,
        pickup_datetime,
        pickup_location_id,
        dropoff_location_id,
        dropoff_datetime
),

fact_trips as (
    select
        -- Primary Key
        md5(
            cast(vendor_id as varchar) || '-' ||
            cast(pickup_datetime as varchar) || '-' ||
            cast(pickup_location_id as varchar) || '-' ||
            cast(dropoff_location_id as varchar)
        ) as trip_id,
        
        -- Identifiers
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
        
        -- Timestamps
        pickup_datetime,
        dropoff_datetime,
        
        -- Trip Info
        store_and_fwd_flag,
        passenger_count,
        trip_distance,
        trip_type,
        service_type,
        
        -- Payment Info
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        payment_type,
        case payment_type
            when 1 then 'Credit card'
            when 2 then 'Cash'
            when 3 then 'No charge'
            when 4 then 'Dispute'
            when 5 then 'Unknown'
            when 6 then 'Voided trip'
            else 'Unknown'
        end as payment_type_name
        
    from trips_deduped
)

select * from fact_trips