-- Conteo total de registros en stg_fhv_tripdata
-- Pregunta: What is the count of records in stg_fhv_tripdata?
-- Respuesta: 43,244,693 registros
-- Nota: El modelo filtra dispatching_base_num IS NOT NULL (3 registros excluidos)

SELECT 
    COUNT(*) as total_count
FROM {{ ref('stg_fhv_tripdata') }}
