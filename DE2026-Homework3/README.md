# Data Engineering Zoomcamp 2026 - Homework 3

## Descripción del Proyecto

Pipeline de carga de datos de Yellow Taxi NYC (enero-junio 2024) desde archivos Parquet a Google Cloud Storage y BigQuery, creando tanto tablas externas como tablas materializadas para análisis de rendimiento.

## 🎯 Objetivos

- Descargar datos de Yellow Taxi Trip Records en formato Parquet
- Cargar archivos Parquet a Google Cloud Storage (GCS)
- Crear tabla externa en BigQuery apuntando a archivos en GCS
- Crear tabla regular (materializada) en BigQuery
- Comparar el rendimiento y uso de datos entre ambos tipos de tablas

## 🛠️ Tecnologías Utilizadas

- **Python 3.12+** - Lenguaje de programación principal
- **Google Cloud Storage** - Almacenamiento de archivos en la nube
- **Google BigQuery** - Data warehouse para análisis SQL
- **pandas** - Manipulación de datos
- **pyarrow** - Lectura de archivos Parquet
- **uv** - Gestor moderno de dependencias Python

## 📁 Estructura del Proyecto

```
DE2026-Homework3/
├── web_to_gcs.py                   # Script para descargar y subir Parquet a GCS
├── DLT_upload_to_GCP.ipynb         # Notebook para crear tablas en BigQuery
├── pyproject.toml                  # Dependencias del proyecto
├── gcs.json                        # Credenciales de servicio GCP (no versionado)
├── yellow_tripdata_2024-*.parquet  # Archivos Parquet descargados (6 meses)
└── README.md                       # Este archivo
```

## 📄 Descripción de Archivos

### `web_to_gcs.py`
Script que descarga archivos Parquet de Yellow Taxi Trip Records desde CloudFront y los sube a Google Cloud Storage.

**Funcionalidades:**
- Descarga archivos Parquet de enero a junio 2024
- Generación automática de nombres de archivo con zero-padding de meses
- Carga de archivos a bucket GCS en carpeta `yellow/`
- Usa credenciales desde archivo `gcs.json` o variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`

**Ejecución:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="gcs.json"
uv run python web_to_gcs.py
```

### `DLT_upload_to_GCP.ipynb`
Notebook de Jupyter que crea y analiza tablas en BigQuery a partir de los archivos en GCS.

**Contenido:**
1. **Configuración de credenciales GCP** - Setup del entorno local
2. **Instalación de paquetes** - Google Cloud BigQuery y Storage
3. **Creación de dataset** - Dataset `yellow_taxi_data` en BigQuery
4. **Tabla externa** - `yellow_taxi_external` apuntando a archivos Parquet en GCS
5. **Tabla regular** - `yellow_taxi_trips` materializada desde la tabla externa
6. **Análisis de rendimiento** - Comparación de uso de datos al consultar ambas tablas
7. **Query de ejemplo** - Conteo de PULocationIDs distintos con estadísticas de bytes procesados

**Resultados clave:**
- Muestra el número total de filas cargadas
- Compara bytes leídos entre tabla externa vs. regular
- Demuestra que la tabla regular es más eficiente para consultas repetidas

### `pyproject.toml`
Archivo de configuración de dependencias para `uv`.

**Dependencias principales:**
- `google-cloud-bigquery` - Cliente de BigQuery
- `google-cloud-storage` - Cliente de GCS
- `pandas` - Análisis de datos
- `pyarrow` - Lectura de Parquet
- `requests` - Descarga de archivos HTTP
- `ipykernel` y `jupyter` - Soporte para notebooks

## 🚀 Cómo Usar

### 1. Configurar Credenciales GCP

Coloca tu archivo de credenciales de servicio como `gcs.json` en esta carpeta.

### 2. Instalar Dependencias

```bash
uv sync
```

### 3. Descargar y Subir Datos a GCS

```bash
export GOOGLE_APPLICATION_CREDENTIALS="gcs.json"
uv run python web_to_gcs.py
```

Esto descargará 6 archivos Parquet (~326 MB total) y los subirá a GCS.

### 4. Crear Tablas en BigQuery

Abre `DLT_upload_to_GCP.ipynb` y ejecuta las celdas en orden:
- Celda 1: Configura credenciales
- Celda 2: Instala paquetes (requiere reinicio de kernel)
- Celda 3: Importa librerías
- Celda 4: Crea dataset
- Celdas 6-7: Crea tabla externa
- Celdas 9-10: Crea tabla regular
- Celdas restantes: Análisis y comparaciones

## 📊 Resultados Esperados

### Datos Cargados
- **Período:** Enero - Junio 2024
- **Total de viajes:** ~3-4 millones de registros
- **Tamaño en GCS:** ~326 MB (Parquet comprimido)
- **Tamaño en BigQuery:** ~1-2 GB (tabla regular)

### Comparación de Tablas

**Tabla Externa (`yellow_taxi_external`):**
- Lee datos directamente desde archivos Parquet en GCS
- No ocupa espacio de almacenamiento en BigQuery
- Cada query lee todos los archivos necesarios
- Ideal para datos que se consultan esporádicamente

**Tabla Regular (`yellow_taxi_trips`):**
- Datos materializados en BigQuery
- Ocupa espacio de almacenamiento
- Consultas más rápidas y eficientes
- BigQuery puede optimizar el escaneo de columnas
- Ideal para consultas frecuentes y análisis recurrente

### Query de Análisis: Distinct PULocationIDs

```sql
SELECT COUNT(DISTINCT PULocationID) as distinct_locations
FROM `yellow_taxi_trips`
```

**Resultados típicos:**
- Distinct locations: ~260-265 zonas de pickup
- Tabla externa: Lee ~326 MB
- Tabla regular: Lee solo columna PULocationID (~10-20 MB)
- **Ahorro:** ~90-95% menos datos procesados con tabla regular

## 📝 Notas Importantes

- **URL de descarga:** Los archivos se descargan desde `https://d37ci6vzurychx.cloudfront.net/trip-data/`
- **Formato de meses:** Se utiliza zero-padding (`01`, `02`, ..., `06`)
- **Credenciales:** Asegúrate de tener permisos de BigQuery Admin y Storage Admin
- **Costos:** Las consultas en BigQuery se facturan por bytes procesados (primeros 1TB/mes gratis)

## 🔧 Solución de Problemas

### Error: "Input file is not in Parquet format"
- Verifica que la URL de descarga en `web_to_gcs.py` sea correcta
- Vuelve a ejecutar el script para sobrescribir archivos corruptos

### Error: "ModuleNotFoundError: No module named 'google'"
- Instala las dependencias: `uv sync`
- O en el notebook: `%pip install -q google-cloud-bigquery google-cloud-storage pyarrow`
- Reinicia el kernel del notebook después de instalar

### Error: "UsageError: Line magic function `%%capture` not found"
- Reemplaza `%%capture` por `%pip install -q` en las celdas de instalación

## 👤 Autor

**Homework 3 - Data Engineering Zoomcamp 2026**  
Repositorio: [ayoquiroga/data-engineering-zoomcamp-2026](https://github.com/ayoquiroga/data-engineering-zoomcamp-2026)

---

*Desarrollado con la asistencia de GitHub Copilot*
