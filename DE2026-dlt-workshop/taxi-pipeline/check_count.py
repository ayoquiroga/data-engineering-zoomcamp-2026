import duckdb
import sys

try:
    conn = duckdb.connect("taxi_pipeline.duckdb")
    count = conn.execute("SELECT COUNT(*) FROM nyc_taxi_data.taxi_trips").fetchone()[0]
    print(f"\n✅ Pipeline ejecutado exitosamente!")
    print(f"📊 Total de registros cargados: {count:,}")
    conn.close()
except Exception as e:
    print(f"\n❌ Error al verificar datos: {e}")
    sys.exit(1)
