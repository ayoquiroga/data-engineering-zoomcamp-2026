/* @bruin

# Docs:
# - Materialization: https://getbruin.com/docs/bruin/assets/materialization
# - Quality checks (built-ins): https://getbruin.com/docs/bruin/quality/available_checks
# - Custom checks: https://getbruin.com/docs/bruin/quality/custom

name: staging.trips

type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: delete+insert
  incremental_key: pickup_datetime

columns:
  - name: trip_id
    type: BIGINT
    description: Unique trip identifier (generated using ROW_NUMBER)
    primary_key: true
    nullable: false
    checks:
      - name: not_null
      - name: unique
  - name: pickup_datetime
    type: TIMESTAMP
    description: When the meter was engaged
    nullable: false
    checks:
      - name: not_null
  - name: dropoff_datetime
    type: TIMESTAMP
    description: When the meter was disengaged
    nullable: false
    checks:
      - name: not_null
  - name: taxi_type
    type: VARCHAR
    description: Type of taxi (yellow or green)
    nullable: false
    checks:
      - name: not_null
  - name: payment_type_id
    type: INTEGER
    description: Payment type identifier
    checks:
      - name: not_null
  - name: payment_type_name
    type: VARCHAR
    description: Human-readable payment type name
  - name: trip_distance
    type: DOUBLE
    description: Trip distance in miles
    checks:
      - name: non_negative
  - name: fare_amount
    type: DOUBLE
    description: Base fare amount
    checks:
      - name: non_negative
  - name: total_amount
    type: DOUBLE
    description: Total amount charged
    checks:
      - name: non_negative

custom_checks:
  - name: dropoff_after_pickup
    description: Ensure dropoff datetime is after pickup datetime
    query: |
      SELECT COUNT(*) 
      FROM staging.trips 
      WHERE dropoff_datetime < pickup_datetime
    value: 0

@bruin */

-- Purpose of staging:
-- - Clean and normalize schema from ingestion
-- - Deduplicate records (important if ingestion uses append strategy)
-- - Enrich with lookup tables (JOINs)
-- - Filter invalid rows (null PKs, negative values, etc.)
--
-- Why filter by {{ start_datetime }} / {{ end_datetime }}?
-- When using `time_interval` strategy, Bruin:
--   1. DELETES rows where `incremental_key` falls within the run's time window
--   2. INSERTS the result of your query
-- Therefore, your query MUST filter to the same time window so only that subset is inserted.
-- If you don't filter, you'll insert ALL data but only delete the window's data = duplicates.

WITH deduplicated AS (
  SELECT 
    *,
    -- Convert string timestamps back to TIMESTAMP type
    TRY_CAST(pickup_datetime AS TIMESTAMP) AS pickup_dt,
    TRY_CAST(dropoff_datetime AS TIMESTAMP) AS dropoff_dt,
    ROW_NUMBER() OVER (
      PARTITION BY pickup_datetime, dropoff_datetime, taxi_type
      ORDER BY pickup_datetime
    ) AS rn
  FROM ingestion.trips
  WHERE TRY_CAST(pickup_datetime AS TIMESTAMP) >= CAST('{{ start_datetime }}' AS TIMESTAMP)
    AND TRY_CAST(pickup_datetime AS TIMESTAMP) < CAST('{{ end_datetime }}' AS TIMESTAMP)
    AND pickup_datetime IS NOT NULL
    AND dropoff_datetime IS NOT NULL
    AND TRY_CAST(dropoff_datetime AS TIMESTAMP) > TRY_CAST(pickup_datetime AS TIMESTAMP)
)
SELECT 
  -- Generate unique trip_id using hash to avoid duplicates in incremental runs
  hash(pickup_dt, dropoff_dt, taxi_type, payment_type, trip_distance, fare_amount) AS trip_id,
  pickup_dt AS pickup_datetime,
  dropoff_dt AS dropoff_datetime,
  taxi_type,
  COALESCE(CAST(payment_type AS INTEGER), 0) AS payment_type_id,
  pl.payment_type_name,
  COALESCE(trip_distance, 0) AS trip_distance,
  COALESCE(fare_amount, 0) AS fare_amount,
  COALESCE(total_amount, 0) AS total_amount
FROM deduplicated d
LEFT JOIN ingestion.payment_lookup pl 
  ON COALESCE(CAST(d.payment_type AS INTEGER), 0) = pl.payment_type_id
WHERE d.rn = 1
  AND COALESCE(trip_distance, 0) >= 0
  AND COALESCE(fare_amount, 0) >= 0
  AND COALESCE(total_amount, 0) >= 0
