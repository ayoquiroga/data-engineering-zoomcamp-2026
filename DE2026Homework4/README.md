# Data Engineering Zoomcamp 2026 - Homework 4
## dbt Project - NYC Taxi Data

### Descripción del Proyecto
Este proyecto utiliza dbt (data build tool) con DuckDB para transformar y analizar datos de taxis de NYC (Yellow, Green y FHV).

### Estructura del Proyecto
```
taxirides_zoomcamp_local/
├── analyses/           # Consultas de análisis SQL
├── models/
│   ├── staging/       # Modelos de staging (stg_*)
│   │   ├── stg_yellow_tripdata.sql
│   │   ├── stg_green_tripdata.sql
│   │   └── stg_fhv_tripdata.sql
│   ├── intermediate/  # Modelos intermedios (int_*)
│   │   └── int_trips_unioned.sql
│   └── marts/         # Modelos finales (fact_*, dim_*)
│       ├── fact_trips.sql
│       ├── dim_vendors.sql
│       ├── dim_zones.sql
│       └── dim_monthly_zone_revenue.sql
├── macros/            # Macros reutilizables
├── seeds/             # Archivos CSV de referencia
│   └── taxi_zone_lookup.csv
└── tests/             # Tests de datos

```

### Requisitos
- Python 3.12+
- dbt-core 1.11.4
- dbt-duckdb 1.10.0

### Instalación
```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source .venv/bin/activate    # Linux/Mac

# Instalar dependencias
pip install dbt-core dbt-duckdb requests

# Configurar profiles.yml en C:\Users\<user>\.dbt\profiles.yml
```

### Configuración de profiles.yml
```yaml
taxirides_zoomcamp_local:
  outputs:
    dev:
      type: duckdb
      path: taxi_rides_ny.duckdb
      schema: dev
      threads: 4
      extensions:
        - parquet
      settings:
        memory_limit: 4GB
    prod:
      type: duckdb
      path: taxi_rides_ny.duckdb
      schema: prod
      threads: 4
      extensions:
        - parquet
      settings:
        memory_limit: 4GB
  target: dev
```

### Uso

#### 1. Ingestar Datos
```bash
# Descargar datos de Yellow y Green taxis (2019-2020)
python ingest.py

# Descargar datos de FHV (2019)
python ingest_fhv.py
```

#### 2. Cargar Seeds
```bash
dbt seed
```

#### 3. Ejecutar Modelos
```bash
# Ejecutar todos los modelos
dbt run

# Ejecutar modelo específico con dependencias
dbt run --select +dim_monthly_zone_revenue

# Ejecutar solo staging
dbt run --select staging.*
```

#### 4. Ejecutar Tests
```bash
dbt test
```

#### 5. Generar Documentación
```bash
dbt docs generate
dbt docs serve
```

### Modelos Principales

#### Staging
- **stg_yellow_tripdata**: Staging de viajes de taxis Yellow
- **stg_green_tripdata**: Staging de viajes de taxis Green
- **stg_fhv_tripdata**: Staging de viajes FHV (For-Hire Vehicles)

#### Intermediate
- **int_trips_unioned**: Unión de Yellow y Green trips

#### Marts
- **fact_trips**: Tabla de hechos con 114.44M viajes únicos
  - Deduplicación con DISTINCT ON
  - Trip ID único (MD5)
  - Enriquecimiento de payment_type
  
- **dim_monthly_zone_revenue**: Agregación mensual por zona y tipo de servicio
  - Revenue metrics por mes/zona/service_type
  - Trips count, avg passenger count, avg distance

- **dim_vendors**: Dimensión de vendors
- **dim_zones**: Dimensión de zonas

### Respuestas del Homework

#### Q1: Count of records in fct_monthly_zone_revenue
**Respuesta: 12,184 registros**

#### Q2: Pickup zone with highest revenue (Green, 2020)
**Opciones:** East Harlem North, Morningside Heights, East Harlem South, Washington Heights South  
**Respuesta: East Harlem South** ($5,623,086.29)

#### Q3: Total Green trips in October 2019
**Respuesta: 385,656** (opción más cercana: 384,624)

#### Q4: Count of records in stg_fhv_tripdata (filtered NULL dispatching_base_num)
**Respuesta: 43,244,693 registros**

### Consultas Guardadas
Todas las consultas de análisis están en la carpeta `analyses/`:
- `count_monthly_zone_revenue.sql`
- `highest_revenue_green_zone_2020.sql`
- `total_green_trips_oct_2019.sql`
- `count_stg_fhv_tripdata.sql`
- `count_fhv_null_dispatching_base.sql`

### Características Técnicas
- **Materialización**: Vistas para staging, Tablas para marts
- **Deduplicación**: DISTINCT ON para optimizar memoria
- **Memory Management**: 4GB limit para DuckDB
- **Service Type Tracking**: Columna service_type ('Green'/'Yellow') para distinguir tipos de taxi

### Notas
- Los datos FHV incluyen solo el año 2019 (43M+ registros)
- La base de datos DuckDB (`taxi_rides_ny.duckdb`) no se sube al repositorio
- Los archivos Parquet en `data/` tampoco se suben (ver `.gitignore`)
