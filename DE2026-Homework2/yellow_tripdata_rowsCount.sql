SELECT
  COUNT(*) AS count_of_rows
FROM
  `kestra-sandbox-2026`.`zoomcamp`.`yellow_tripdata`
WHERE
  TIMESTAMP_TRUNC(tpep_pickup_datetime, YEAR) = TIMESTAMP '2020-01-01 00:00:00 UTC';