import duckdb

conn = duckdb.connect('taxi_pipeline.duckdb')

# Consultar el monto total generado en viajes
result = conn.execute('''
    SELECT SUM(total_amt) as total_amount 
    FROM nyc_taxi_data.taxi_trips
''').fetchone()

print(f'Total amount generated: ${result[0]:,.2f}')

conn.close()
