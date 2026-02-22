/* @bruin

# Docs:
# - SQL assets: https://getbruin.com/docs/bruin/assets/sql
# - Materialization: https://getbruin.com/docs/bruin/assets/materialization
# - Quality checks: https://getbruin.com/docs/bruin/quality/available_checks

name: reports.trips_report

type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: report_date
  time_granularity: date

columns:
  - name: report_date
    type: DATE
    description: Date of the trip (derived from pickup_datetime)
    primary_key: true
    nullable: false
    checks:
      - name: not_null
  - name: taxi_type
    type: VARCHAR
    description: Type of taxi (yellow or green)
    primary_key: true
    nullable: false
    checks:
      - name: not_null
  - name: payment_type_name
    type: VARCHAR
    description: Payment type name
    primary_key: true
    nullable: false
    checks:
      - name: not_null
  - name: trip_count
    type: BIGINT
    description: Number of trips
    checks:
      - name: non_negative
      - name: positive
  - name: total_revenue
    type: DOUBLE
    description: Total revenue from trips
    checks:
      - name: non_negative
  - name: avg_trip_distance
    type: DOUBLE
    description: Average trip distance in miles
    checks:
      - name: non_negative

@bruin */

-- Purpose of reports:
-- - Aggregate staging data for dashboards and analytics
-- Required Bruin concepts:
-- - Filter using `{{ start_datetime }}` / `{{ end_datetime }}` for incremental runs
-- - GROUP BY your dimension + date columns

SELECT 
  DATE(pickup_datetime) AS report_date,
  taxi_type,
  payment_type_name,
  COUNT(*) AS trip_count,
  SUM(total_amount) AS total_revenue,
  AVG(trip_distance) AS avg_trip_distance
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY 
  DATE(pickup_datetime),
  taxi_type,
  payment_type_name
ORDER BY 
  report_date DESC,
  taxi_type,
  payment_type_name
