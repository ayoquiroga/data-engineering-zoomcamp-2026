import duckdb

conn = duckdb.connect('taxi_pipeline.duckdb')

# Consultar proporción de pagos con tarjeta de crédito
result = conn.execute('''
    SELECT 
        COUNT(*) FILTER (WHERE payment_type = 'Credit') as credit_card_trips,
        COUNT(*) as total_trips,
        ROUND(COUNT(*) FILTER (WHERE payment_type = 'Credit') * 100.0 / COUNT(*), 2) as credit_card_percentage
    FROM nyc_taxi_data.taxi_trips
''').fetchone()

# Guardar resultados en archivo
with open('credit_card_result.txt', 'w') as f:
    f.write(f'Credit card trips: {result[0]:,}\n')
    f.write(f'Total trips: {result[1]:,}\n')
    f.write(f'Proportion: {result[2]}%\n')

print("Results saved to credit_card_result.txt")

conn.close()
