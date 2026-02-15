-- Total de viajes Green en octubre 2019
-- Pregunta: Which is the Total trips for Green taxis in October 2019?
-- Opciones: 500,234 / 350,891 / 384,624 / 421,509
-- Respuesta: 385,656 (más cercana a 384,624)

SELECT 
    SUM(total_monthly_trips) as total_trips
FROM {{ ref('dim_monthly_zone_revenue') }}
WHERE service_type = 'Green'
    AND EXTRACT(YEAR FROM revenue_month) = 2019
    AND EXTRACT(MONTH FROM revenue_month) = 10
