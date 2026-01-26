# Historial de Conversación - Data Engineering Zoomcamp 2026 - Homework 1

**Fecha:** Enero 22-26, 2026  
**Proyecto:** Data Engineering Zoomcamp 2026 - Homework 1  
**Repositorio:** ayoquiroga/data-engineering-zoomcamp-2026

---

## Problema 1: Configuración del Intérprete de Python

**Usuario:** ver la opcion Python: Select Interpreter

**Solución:**
- Se instaló la extensión de Python (`ms-python.python`)
- Se explicó cómo acceder al selector de intérpretes:
  - `Ctrl+Shift+P` → "Python: Select Interpreter"
  - O desde la barra de estado en la parte inferior de VS Code

---

## Problema 2: Error StopIteration en Notebook con Pandas

**Usuario:** Error al intentar insertar datos desde CSV a PostgreSQL usando Python

**Error:** `"StopIteration"` en `pandas._libs.parsers.TextReader.read_low_memory()`

**Diagnóstico:**
- El iterador `df_iter` fue consumido completamente en una celda anterior
- Al intentar usar `next(df_iter)` en una celda posterior, el iterador ya estaba agotado

**Solución aplicada en notebook.ipynb:**
```python
df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000,
)
```

---

## Problema 3: Warning de Permisos en Git

**Usuario:** Warning `"could not open directory 'pipeline/ny_taxi_postgres_data/18/docker/': Permission denied"`

**Diagnóstico:**
- El directorio `ny_taxi_postgres_data` contiene archivos de PostgreSQL con permisos de root
- Git no puede acceder a algunos subdirectorios

**Solución:**
1. Agregado al `.gitignore`:
   ```
   # PostgreSQL data directory
   ny_taxi_postgres_data/
   ```
2. Ejecutado: `git rm -r --cached pipeline/ny_taxi_postgres_data/`

---

## Problema 4: Usar Click para Parsear Argumentos

**Usuario:** Usar click para parsear argumentos, instalar con uv

**Implementación en ingest_data.py:**
1. Instalado click: `uv add click`
2. Agregado import: `import click`
3. Decorada función main con `@click.command()` y opciones:

```python
@click.command()
@click.option('--user', default='root', help='PostgreSQL username')
@click.option('--password', default='root', help='PostgreSQL password')
@click.option('--host', default='localhost', help='PostgreSQL host')
@click.option('--port', default='5432', help='PostgreSQL port')
@click.option('--db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--table', default='yellow_taxi_data', help='Target table name')
@click.option('--url', required=True, help='URL of the CSV file to ingest')
@click.option('--chunksize', default=100000, help='Number of rows per chunk')
```

---

## Problema 5: Agregar Opciones Year y Month

**Usuario:** Agregar year y month como opciones

**Modificación:**
- Agregadas opciones `--year` y `--month`
- URL se construye automáticamente si no se proporciona `--url`:

```python
if url is None:
    url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
    url = f'{url_prefix}/yellow_tripdata_{year:04d}-{month:02d}.csv.gz'
```

---

## Problema 6: Eliminar Opción URL

**Usuario:** Sacar la opción url

**Modificación:**
- Eliminada opción `--url`
- URL siempre se construye a partir de year y month

---

## Problema 7: Error al Copiar Archivo en Dockerfile

**Usuario:** Error al ejecutar `docker build` - no puede encontrar `ingest_data.py`

**Diagnóstico:**
- Los archivos están en el directorio `pipeline/` pero el Dockerfile los busca en la raíz

**Solución en Dockerfile:**
```dockerfile
COPY "pipeline/pyproject.toml" "pipeline/uv.lock" "pipeline/.python-version" ./
COPY pipeline/ingest_data.py ingest_data.py
```

---

## Problema 8: Módulo Click No Encontrado en Docker

**Usuario:** Error `"ModuleNotFoundError: No module named 'click'"`

**Diagnóstico:**
- Click no estaba en las dependencias del `pyproject.toml`

**Solución:**
1. Ejecutado: `cd DE2026-Homework1 && uv add click`
2. Reconstruida imagen: `docker build -t taxi_ingest:HW01 .`

---

## Problema 9: Error con pd.read_parquet y Parámetros iterator/chunksize

**Usuario:** Error al ejecutar `ingest_data.py` con archivos Parquet

**Diagnóstico:**
- `pd.read_parquet` no soporta `iterator=True` ni `chunksize` (solo `pd.read_csv` lo soporta)

**Solución implementada en ingest_data.py:**
```python
def ingest_data(url: str, engine, target_table: str, chunksize: int = 100000):
    # Read the entire parquet file
    df = pd.read_parquet(url)
    
    # Create the table with empty data first
    df.head(0).to_sql(name=target_table, con=engine, if_exists="replace")
    print(f"Table {target_table} created")

    # Insert data in chunks manually
    total_rows = len(df)
    for start in tqdm(range(0, total_rows, chunksize)):
        end = min(start + chunksize, total_rows)
        df_chunk = df.iloc[start:end]
        
        df_chunk.to_sql(name=target_table, con=engine, if_exists="append")
        print(f"Inserted chunk: {len(df_chunk)} rows (from {start} to {end})")

    print(f'Done ingesting {total_rows} rows to {target_table}')
```

---

## Problema 10: Agregar Archivo taxi_zone_lookup.csv al Dockerfile

**Usuario:** Agregar `taxi_zone_lookup.csv` al contenedor y modificar `ingest_data.py` para cargarlo a PostgreSQL

**Modificaciones:**

### 1. Dockerfile:
```dockerfile
# Copy parquet data file
COPY green_tripdata_2025-11.parquet ./

# Copy taxi zone lookup CSV
COPY taxi_zone_lookup.csv ./
```

### 2. ingest_data.py - función main:
```python
def main(user, password, host, port, db, table, year, month, chunksize):
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    
    # First, ingest taxi zone lookup table
    print("Ingesting taxi zone lookup table...")
    taxi_zones = pd.read_csv('./taxi_zone_lookup.csv')
    taxi_zones.to_sql(
        name='taxi_zone_lookup',
        con=engine,
        if_exists='replace',
        index=False
    )
    print(f"Inserted {len(taxi_zones)} rows into taxi_zone_lookup table")
    
    # Then, ingest green taxi trip data
    print("\nIngesting green taxi trip data...")
    url = f'./green_tripdata_{year:04d}-{month:02d}.parquet'
    ingest_data(url=url, engine=engine, target_table=table, chunksize=chunksize)
```

### 3. Reconstruida imagen:
```bash
docker build -t taxi_ingest:HW01 .
```

---

## Problema 11: Corregir Notebook con Lógica de Parquet

**Usuario:** Corregir `notebook.ipynb` para archivos Parquet sin iterator/chunksize

**Correcciones aplicadas en DE2026-Homework1/notebook.ipynb:**

### Celda 18:
```python
# Read the entire parquet file (parquet doesn't support iterator/chunksize like CSV)
df = pd.read_parquet("green_tripdata_2025-11.parquet")
```

### Celda 19:
```python
# Check the dataframe info
df.info()
```

### Celda 20:
```python
# Total number of rows
print(f"Total rows: {len(df)}")
```

### Celda 23:
```python
# Read the entire parquet file
df = pd.read_parquet("green_tripdata_2025-11.parquet")
```

### Celda 24:
```python
# Create the table with empty data first
df.head(0).to_sql(
    name="green_taxi_trips_2025_11",
    con=engine,
    if_exists="replace"
)

print("Table created")

# Insert data in chunks
chunksize = 100000
total_rows = len(df)

for start in tqdm(range(0, total_rows, chunksize)):
    end = min(start + chunksize, total_rows)
    df_chunk = df.iloc[start:end]
    
    df_chunk.to_sql(
        name="green_taxi_trips_2025_11",
        con=engine,
        if_exists="append"
    )
    print(f"Inserted chunk: {len(df_chunk)} rows (from {start} to {end})")

print(f"Done ingesting {total_rows} rows")
```

---

## Consultas SQL para Homework 1

### Consulta 1: Viajes con distancia <= 1 milla en noviembre 2025
```sql
SELECT COUNT(*) 
FROM green_taxi_trips_2025_11 
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01' 
  AND trip_distance <= 1;
```

### Consulta 2: Día con mayor distancia total de viaje (< 160 km)
```sql
SELECT 
    DATE(lpep_pickup_datetime) as pickup_date,
    SUM(trip_distance) as total_distance,
    COUNT(*) as num_trips
FROM green_taxi_trips_2025_11
WHERE trip_distance < 160
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY total_distance DESC
LIMIT 10;
```

### Consulta 3: Zona de recogida con mayor monto total el 18 de noviembre 2025
```sql
SELECT 
    tz.Zone as pickup_zone,
    SUM(gt.total_amount) as total_amount,
    COUNT(*) as num_trips
FROM green_taxi_trips_2025_11 gt
JOIN taxi_zone_lookup tz ON gt."PULocationID" = tz."LocationID"
WHERE DATE(gt.lpep_pickup_datetime) = '2025-11-18'
GROUP BY tz.Zone
ORDER BY total_amount DESC
LIMIT 10;
```

### Consulta 4: Zona de descenso con mayor propina desde East Harlem North
```sql
SELECT 
    tz_dropoff.Zone as dropoff_zone,
    MAX(gt.tip_amount) as max_tip,
    COUNT(*) as num_trips,
    AVG(gt.tip_amount) as avg_tip
FROM green_taxi_trips_2025_11 gt
JOIN taxi_zone_lookup tz_pickup ON gt."PULocationID" = tz_pickup."LocationID"
JOIN taxi_zone_lookup tz_dropoff ON gt."DOLocationID" = tz_dropoff."LocationID"
WHERE tz_pickup.Zone = 'East Harlem North'
    AND DATE_PART('year', gt.lpep_pickup_datetime) = 2025
    AND DATE_PART('month', gt.lpep_pickup_datetime) = 11
GROUP BY tz_dropoff.Zone
ORDER BY max_tip DESC
LIMIT 10;
```

---

## Comandos Docker Útiles

### Construir imagen:
```bash
docker build -t taxi_ingest:HW01 .
```

### Ejecutar contenedor:
```bash
docker run -it \
  --network=de2026-homework1_default \
  taxi_ingest:HW01 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --table=green_taxi_trips_2025_11 \
  --year=2025 \
  --month=11
```

### Crear red Docker:
```bash
docker network create pg-network
```

---

## Estructura Final de Archivos

```
DE2026-Homework1/
├── Dockerfile
├── docker-compose.yaml
├── ingest_data.py
├── notebook.ipynb
├── pyproject.toml
├── uv.lock
├── .python-version
├── green_tripdata_2025-11.parquet
├── taxi_zone_lookup.csv
└── README.md
```

---

## Lecciones Aprendidas

### 1. pandas.read_parquet NO soporta iterator=True ni chunksize
**Solución:** Leer el archivo completo y dividir manualmente con `df.iloc[start:end]`

### 2. Los iteradores en Python solo se pueden usar una vez
**Solución:** Recrear el iterador si necesitas usarlo nuevamente

### 3. Docker busca archivos relativos al contexto de construcción
**Solución:** Especificar rutas correctas con prefijos de directorio

### 4. Las dependencias deben estar en pyproject.toml para que uv sync las instale
**Solución:** Usar `uv add <paquete>` antes de reconstruir la imagen

### 5. Los directorios de datos de PostgreSQL no deben estar en Git
**Solución:** Agregar al `.gitignore` y usar `git rm -r --cached`

### 6. Click simplifica el manejo de argumentos de línea de comandos
**Beneficios:** Validación automática, ayuda integrada, valores por defecto

---

**FIN DEL HISTORIAL**
