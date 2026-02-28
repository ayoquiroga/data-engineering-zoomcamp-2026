import duckdb
import sys

# Redirigir warnings
import warnings
warnings.filterwarnings('ignore')

# Conectar a la base de datos
conn = duckdb.connect("taxi_pipeline.duckdb")

print("\n" + "="*60)
print("VERIFICACIÓN DE DATOS - NYC TAXI PIPELINE")
print("="*60)

# Listar todas las tablas
print("\n📊 Schemas y Tablas:")
schemas = conn.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')").fetchall()
for schema in schemas:
    schema_name = schema[0]
    print(f"\n  Schema: {schema_name}")
    tables = conn.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}'").fetchall()
    for table in tables:
        print(f"    └─ {table[0]}")

# Contar registros en la tabla taxi_trips
print("\n📈 Estadísticas de taxi_trips:")
try:
    count = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.taxi_trips").fetchone()[0]
    print(f"    Total de registros: {count:,}")
    
    # Estadísticas adicionales (usando nombres en snake_case que DuckDB usa)
    stats = conn.execute("""
        SELECT 
            MIN(trip_pickup_date_time) as fecha_inicio,
            MAX(trip_dropoff_date_time) as fecha_fin,
            ROUND(AVG(fare_amt), 2) as tarifa_promedio,
            ROUND(AVG(trip_distance), 2) as distancia_promedio
        FROM nyc_taxi_data.taxi_trips
    """).fetchone()
    
    print(f"    Fecha inicio: {stats[0]}")
    print(f"    Fecha fin: {stats[1]}")
    print(f"    Tarifa promedio: ${stats[2]}")  
    print(f"    Distancia promedio: {stats[3]} millas")
    
    # Columnas
    columns = conn.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'nyc_taxi_data' AND table_name = 'taxi_trips'").fetchone()[0]
    print(f"    Total de columnas: {columns}")
    
except Exception as e:
    print(f"    ❌ Error: {e}")

print("\n" + "="*60)
print("✅ Verificación completada exitosamente!")
print("="*60 + "\n")

conn.close()
