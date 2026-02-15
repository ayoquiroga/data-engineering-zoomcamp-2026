-- Conteo de registros en dim_monthly_zone_revenue
-- Pregunta: What is the count of records in the fct_monthly_zone_revenue model?
-- Respuesta: 12,184 registros

SELECT 
    COUNT(*) as record_count 
FROM {{ ref('dim_monthly_zone_revenue') }}
