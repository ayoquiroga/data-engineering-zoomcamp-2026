-- Zona con mayor ingreso para Green taxis en 2020
-- Pregunta: Using the dim_monthly_zone_revenue table, find the pickup zone with the highest 
--           total revenue (revenue_monthly_total_amount) for Green taxi trips in 2020.
--           Which zone had the highest revenue?
-- Opciones: East Harlem North, Morningside Heights, East Harlem South, Washington Heights South
-- Respuesta: East Harlem South ($5,623,086.29)

SELECT 
    revenue_zone, 
    SUM(revenue_monthly_total_amount) as total_revenue 
FROM {{ ref('dim_monthly_zone_revenue') }}
WHERE service_type = 'Green'
    AND EXTRACT(YEAR FROM revenue_month) = 2020
    AND revenue_zone IN (
        'East Harlem North', 
        'Morningside Heights', 
        'East Harlem South', 
        'Washington Heights South'
    )
GROUP BY revenue_zone 
ORDER BY total_revenue DESC
