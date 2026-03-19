# streaming-redpanda-flink

Pipeline de procesamiento de datos en tiempo real utilizando **Redpanda** como broker de mensajería (compatible con Kafka), **Apache Flink** (PyFlink) para el procesamiento de streams y **PostgreSQL** como sink de resultados.

El dataset utilizado es el de viajes en taxi verde de NYC (`green_tripdata_2025-10.parquet`).

---

## Arquitectura

```
NYC Green Taxi Data (Parquet)
        │
        ▼
   producer.py  ──►  Redpanda (topic: green-trips)  ──►  PyFlink Jobs  ──►  PostgreSQL
```

| Servicio | Puerto | Descripción |
|---|---|---|
| Redpanda | `9092` / `29092` | Broker Kafka-compatible |
| Flink JobManager | `8081` | UI web de Flink |
| PostgreSQL | `5432` | Base de datos de resultados |

---

## Requisitos

- Docker y Docker Compose
- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)

---

## Instalación y puesta en marcha

### 1. Levantar los servicios

```bash
docker compose up --build --remove-orphans -d
# o con Make:
make up
```

### 2. Instalar dependencias Python (host)

```bash
uv sync
```

### 3. Publicar eventos en Redpanda

```bash
uv run python src/producers/producer.py
```

Lee el archivo `green_tripdata_2025-10.parquet` y publica cada viaje en el topic `green-trips` con un intervalo de 10 ms entre mensajes.

### 4. Enviar jobs a Flink

```bash
# Job pass-through (guarda eventos crudos en processed_events)
docker exec -it de2026-homework7-jobmanager-1 flink run \
    -py /opt/src/job/pass_through_job.py --pyFiles /opt/src -d

# Tumbling window de 5 minutos (trips por localización)
docker exec -it de2026-homework7-jobmanager-1 flink run \
    -py /opt/src/job/tumbling.py --pyFiles /opt/src -d

# Session window (sesiones por localización)
docker exec -it de2026-homework7-jobmanager-1 flink run \
    -py /opt/src/job/session_window.py --pyFiles /opt/src -d

# Tumbling window de 1 hora (propinas por hora)
docker exec -it de2026-homework7-jobmanager-1 flink run \
    -py /opt/src/job/tumbling_1h.py --pyFiles /opt/src -d
```

---

## Jobs de Flink

### `pass_through_job.py`
Lee eventos del topic `green-trips` y los escribe directamente en la tabla `processed_events` de PostgreSQL, convirtiendo los timestamps de epoch (ms) a `TIMESTAMP`.

### `tumbling.py`
Ventanas tumbling de **5 minutos**. Cuenta el número de viajes por `PULocationID` en cada ventana y persiste en `trips_per_location`.

### `session_window.py`
Ventanas de sesión con un **gap de 5 minutos**. Agrupa viajes del mismo `PULocationID` mientras no haya un silencio mayor a 5 minutos, persistiendo en `session_trips`.

### `tumbling_1h.py`
Ventanas tumbling de **1 hora**. Suma el `tip_amount` total por ventana y persiste en `tip_per_hour`.

---

## Esquema PostgreSQL

### Tabla 1 — `processed_events`

Almacena los eventos de viaje tal como llegan del stream (sin agregación).

```sql
CREATE TABLE processed_events (
    PULocationID     INTEGER,
    DOLocationID     INTEGER,
    trip_distance    DOUBLE PRECISION,
    total_amount     DOUBLE PRECISION,
    pickup_datetime  TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count  INTEGER,
    tip_amount       DOUBLE PRECISION
);
```

**Consultas de validación:**

```sql
-- Ver todos los eventos recibidos
SELECT * FROM processed_events;

-- Contar el total de viajes
SELECT count(*) FROM processed_events;

-- Pregunta 1: ¿Cuántos viajes tienen trip_distance > 5 km?
SELECT count(1) FROM processed_events WHERE trip_distance > 5;
```

---

### Tabla 2 — `trips_per_location`

Resultado de ventanas tumbling de 5 minutos: número de viajes por zona de recogida.

```sql
CREATE TABLE trips_per_location (
    window_start TIMESTAMP,
    PULocationID INTEGER,
    num_trips    BIGINT,
    PRIMARY KEY (window_start, PULocationID)
);
```

**Consultas de validación:**

```sql
SELECT * FROM trips_per_location;

-- Pregunta 2: Top 3 zonas con más viajes
SELECT PULocationID, num_trips
FROM trips_per_location
ORDER BY num_trips DESC
LIMIT 3;
```

---

### Tabla 3 — `session_trips`

Resultado de ventanas de sesión (gap 5 min): agrupa viajes consecutivos del mismo `PULocationID`.

```sql
CREATE TABLE session_trips (
    session_start TIMESTAMP,
    session_end   TIMESTAMP,
    PULocationID  INTEGER,
    num_trips     BIGINT,
    PRIMARY KEY (session_start, session_end, PULocationID)
);
```

**Consultas de validación:**

```sql
SELECT * FROM session_trips;

-- Pregunta 3: Sesión con más viajes
SELECT PULocationID, num_trips, session_start, session_end
FROM session_trips
ORDER BY num_trips DESC
LIMIT 1;
```

---

### Tabla 4 — `tip_per_hour`

Resultado de ventanas tumbling de 1 hora: suma total de propinas por hora.

```sql
CREATE TABLE tip_per_hour (
    window_start TIMESTAMP,
    window_end   TIMESTAMP,
    total_tip    DOUBLE PRECISION,
    PRIMARY KEY (window_start)
);
```

**Consultas de validación:**

```sql
SELECT * FROM tip_per_hour;

-- Pregunta 4: Hora con mayor total de propinas
SELECT window_start, window_end, total_tip
FROM tip_per_hour
ORDER BY total_tip DESC
LIMIT 1;
```

---

## Estructura del proyecto

```
.
├── docker-compose.yml        # Redpanda + Flink + PostgreSQL
├── Dockerfile.flink          # Imagen custom de PyFlink
├── flink-config.yaml         # Configuración de Flink
├── Makefile                  # Comandos frecuentes
├── pyproject.toml            # Dependencias del host (uv)
├── pyproject.flink.toml      # Dependencias dentro del contenedor Flink
└── src/
    ├── models.py             # Dataclass Ride + serializador Kafka
    ├── producers/
    │   ├── producer.py       # Produce desde el archivo parquet (batch)
    │   └── producer_realtime.py  # Produce con timestamps en tiempo real
    ├── consumers/
    │   ├── consumer.py       # Consumidor de consola
    │   └── consumer_postgres.py  # Consumidor directo a PostgreSQL
    └── job/
        ├── pass_through_job.py   # → processed_events
        ├── tumbling.py           # → trips_per_location (5 min)
        ├── session_window.py     # → session_trips (gap 5 min)
        ├── tumbling_1h.py        # → tip_per_hour (1 hora)
        └── aggregation_job.py    # Job de agregación general
```

---

## Apagar los servicios

```bash
docker compose down
# o:
make down
```