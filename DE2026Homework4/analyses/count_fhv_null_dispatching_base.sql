-- Conteo de registros en stg_fhv_tripdata con dispatching_base_num IS NULL
-- Pregunta: Count of records in stg_fhv_tripdata (filter dispatching_base_num IS NULL)?
-- Respuesta: 3 registros

SELECT 
    COUNT(*) as null_count
FROM {{ ref('stg_fhv_tripdata') }}
WHERE dispatching_base_num IS NULL
