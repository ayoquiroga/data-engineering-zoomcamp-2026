SELECT
  COUNT(unique_row_id)
FROM
  `kestra-sandbox-2026`.`zoomcamp`.`green_tripdata`
WHERE
  TIMESTAMP_TRUNC(lpep_pickup_datetime, YEAR) = TIMESTAMP '2020-01-01 00:00:00';