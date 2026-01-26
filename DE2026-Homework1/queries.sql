--Question 3. Counting short trips
SELECT COUNT(*) 
FROM green_taxi_trips_2025_11 
WHERE lpep_pickup_datetime >= '2025-11-01' 
AND lpep_pickup_datetime < '2025-12-01' AND trip_distance <= 1;

--Question 4. Longest trip for each day
SELECT 
    DATE(lpep_pickup_datetime) as pickup_date,
    SUM(trip_distance) as total_distance
FROM green_taxi_trips_2025_11
WHERE trip_distance < 160
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY total_distance DESC
LIMIT 1;

--Question 5. Biggest pickup zone
SELECT 
    tz."Zone" as pickup_zone,
    SUM(gt.total_amount) as total_amount
FROM green_taxi_trips_2025_11 gt
JOIN taxi_zone_lookup tz ON gt."PULocationID" = tz."LocationID"
WHERE DATE(gt.lpep_pickup_datetime) = '2025-11-18'
GROUP BY tz."Zone"
ORDER BY total_amount DESC
LIMIT 1;

--Question 6. Largest tip
SELECT 
    tz_dropoff."Zone" as dropoff_zone,
    MAX(gt.tip_amount) as max_tip
FROM green_taxi_trips_2025_11 gt
JOIN taxi_zone_lookup tz_pickup ON gt."PULocationID" = tz_pickup."LocationID"
JOIN taxi_zone_lookup tz_dropoff ON gt."DOLocationID" = tz_dropoff."LocationID"
WHERE tz_pickup."Zone" = 'East Harlem North'
    AND DATE_PART('year', gt.lpep_pickup_datetime) = 2025
    AND DATE_PART('month', gt.lpep_pickup_datetime) = 11
GROUP BY tz_dropoff."Zone"
ORDER BY max_tip DESC
LIMIT 1;