# Data Engineering Zoomcamp 2026 - Homework 1

## Descripción del Proyecto

Pipeline de ingesta de datos de taxis verdes de NYC (noviembre 2025) a una base de datos PostgreSQL usando Python, Docker y herramientas modernas de gestión de dependencias.

## 🎯 Objetivos

- Ingestar datos de viajes de taxi en formato Parquet a PostgreSQL
- Dockerizar el proceso de ingesta para facilitar la reproducibilidad
- Realizar análisis SQL sobre los datos cargados

## 🛠️ Tecnologías Utilizadas

- **Python 3.12+** - Lenguaje de programación principal
- **pandas** - Manipulación y análisis de datos
- **SQLAlchemy** - ORM para interacción con PostgreSQL
- **psycopg2** - Driver de PostgreSQL
- **Click** - Interfaz de línea de comandos
- **Docker** - Containerización
- **PostgreSQL** - Base de datos relacional
- **uv** - Gestor moderno de dependencias Python

## 📁 Estructura del Proyecto

```
DE2026-Homework1/
├── ingest_data.py              # Script principal de ingesta
├── notebook.ipynb              # Jupyter notebook con análisis exploratorio
├── Dockerfile                  # Imagen Docker para ingesta
├── docker-compose.yaml         # Orquestación de servicios
├── pyproject.toml              # Dependencias del proyecto
├── green_tripdata_2025-11.parquet  # Datos de viajes
├── taxi_zone_lookup.csv        # Lookup de zonas de NYC
└── CopilotHelpsHW1.md         # Historial detallado de desarrollo
```

## 🚀 Cómo Usar

### 1. Levantar la base de datos PostgreSQL

```bash
docker-compose up -d
```

### 2. Construir la imagen Docker de ingesta

```bash
docker build -t taxi_ingest:HW01 .
```

### 3. Ejecutar el proceso de ingesta

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

## 📊 Consultas SQL Implementadas

El proyecto incluye respuestas a las siguientes preguntas del homework:

1. **¿Cuántos viajes tuvieron una distancia ≤ 1 milla en noviembre 2025?**
2. **¿Qué día tuvo la mayor distancia total de viaje?**
3. **¿Qué zona de recogida tuvo el mayor monto total el 18 de noviembre?**
4. **¿Qué zona de descenso tuvo la mayor propina desde East Harlem North?**

Ver consultas completas en [CopilotHelpsHW1.md](CopilotHelpsHW1.md)

## ⚙️ Características Técnicas

### Ingesta Optimizada
- Lectura de archivos Parquet
- Inserción por chunks (100,000 registros por lote)
- Barra de progreso con tqdm
- Carga automática de tabla de lookup de zonas

### Configuración Flexible
- Parámetros configurables vía CLI con Click
- Valores por defecto razonables
- Documentación de ayuda integrada (`--help`)

### Containerización
- Imagen Docker ligera basada en Python slim
- Uso de uv para gestión rápida de dependencias
- Archivos de datos incluidos en la imagen

## 📝 Notas Importantes

- **pandas.read_parquet** no soporta `iterator=True` ni `chunksize` como `read_csv`
- Solución: Leer el DataFrame completo y dividirlo manualmente con `df.iloc[start:end]`
- La tabla `taxi_zone_lookup` se carga automáticamente antes de los datos de viajes

## 📚 Documentación Adicional

Para ver el proceso completo de desarrollo, incluyendo todos los problemas encontrados y sus soluciones, consulta [CopilotHelpsHW1.md](CopilotHelpsHW1.md)

## 👤 Autor

**Homework 1 - Data Engineering Zoomcamp 2026**  
Repositorio: [ayoquiroga/data-engineering-zoomcamp-2026](https://github.com/ayoquiroga/data-engineering-zoomcamp-2026)

---

*Desarrollado con la asistencia de GitHub Copilot*
