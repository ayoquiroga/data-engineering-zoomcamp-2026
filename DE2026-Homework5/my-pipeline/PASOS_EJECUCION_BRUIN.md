# Ejecución del pipeline Bruin — Paso a paso

## 1. Explicación: `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`

### ¿Qué hace esa línea?

```sql
ROW_NUMBER() OVER (
  PARTITION BY pickup_datetime, dropoff_datetime, taxi_type
  ORDER BY pickup_datetime
) AS rn
```

- **ROW_NUMBER()** es una función de ventana: asigna un número entero (1, 2, 3, …) a cada fila.
- **PARTITION BY** divide el resultado en **grupos**. Aquí cada grupo son filas con el mismo `(pickup_datetime, dropoff_datetime, taxi_type)`.
- **ORDER BY pickup_datetime** define el orden dentro de cada grupo. La primera fila del grupo recibe 1, la segunda 2, etc.
- **rn** es el alias de esa columna (row number).

### ¿Para qué sirve aquí?

En **ingestion** usamos estrategia **append**: cada ejecución solo agrega filas. Si el mismo viaje se descargó dos veces (o hubo reintentos), habrá **duplicados** con el mismo `(pickup_datetime, dropoff_datetime, taxi_type)`.

Con esta expresión:
- Todas las filas que comparten ese triple se agrupan.
- Dentro de cada grupo se numeran (1, 2, 3, …).
- Luego, con **WHERE rn = 1** nos quedamos solo con **una fila por grupo** → **deduplicación**.

Resumen: **detecta duplicados por (pickup, dropoff, taxi_type) y deja solo uno por grupo** (el “primero” según `ORDER BY pickup_datetime`).

---

## 2. Pasos para ejecutar el pipeline con Bruin

### Paso 1 — Validar (ya hecho)

```bash
bruin validate pipeline/pipeline.yml
```

- Bruin lee todos los assets, comprueba sintaxis, dependencias y tipos.
- No toca la base de datos ni descarga datos.
- Si hay errores, los muestra y no debes seguir hasta corregirlos.

**Estado:** ✓ Hecho.

---

### Paso 2 — Definir ventana de fechas y variables

Antes de ejecutar, decides:

- **Ventana de tiempo:** `--start-date` y `--end-date` (formato YYYY-MM-DD).
- **Variables del pipeline:** por ejemplo `--var 'taxi_types=["yellow"]'` para procesar solo yellow (más rápido en pruebas).

Bruin usará esas fechas en `BRUIN_START_DATE` / `BRUIN_END_DATE` y en `{{ start_datetime }}` / `{{ end_datetime }}` en los SQL.

---

### Paso 3 — Ejecutar el pipeline

```bash
bruin run pipeline/pipeline.yml --start-date 2022-01-01 --end-date 2022-01-02 --var 'taxi_types=["yellow"]'
```

Bruin entonces:

1. **Resuelve el grafo de dependencias** (DAG):
   - `ingestion.payment_lookup` (sin dependencias)
   - `ingestion.trips` (sin dependencias)
   - `staging.trips` (depende de `ingestion.trips` y `ingestion.payment_lookup`)
   - `reports.trips_report` (depende de `staging.trips`)

2. **Orden de ejecución:**
   - Primero: **ingestion.payment_lookup** (carga el CSV a DuckDB).
   - Segundo: **ingestion.trips** (Python: descarga Parquets, normaliza, escribe en `ingestion.trips`).
   - Tercero: **staging.trips** (SQL: deduplica con ROW_NUMBER, filtra ventana, JOIN con payment_lookup).
   - Cuarto: **reports.trips_report** (SQL: agrega por fecha, taxi_type, payment_type_name).

3. **Para cada asset:**
   - Conecta a DuckDB usando la conexión definida (p. ej. `duckdb-default`).
   - Ejecuta el asset (seed / Python / SQL).
   - Si el asset tiene **time_interval**, Bruin borra las filas de la ventana y inserta el resultado del query.
   - Ejecuta los **quality checks** definidos (not_null, non_negative, custom_checks, etc.).

4. **Salida en consola:** verás por cada asset “Running: …”, “Finished: …” y al final el resumen (PASS/FAIL y checks).

---

### Paso 4 — Revisar resultados (opcional)

- Consultar tablas en DuckDB:
  - `ingestion.trips`, `ingestion.payment_lookup`
  - `staging.trips`
  - `reports.trips_report`
- O usar: `bruin query --connection duckdb-default --query "SELECT * FROM reports.trips_report LIMIT 10"`

---

## 3. Resumen del flujo Bruin

| Paso | Comando / acción        | Qué hace Bruin |
|------|-------------------------|----------------|
| 1    | `bruin validate ...`    | Valida sintaxis, dependencias y tipos; no ejecuta nada. |
| 2    | Definir fechas/vars    | Tú eliges ventana y, por ejemplo, `taxi_types`. |
| 3    | `bruin run ...`        | Ordena assets por DAG, ejecuta cada uno, aplica materialización y checks. |
| 4    | Consultar tablas       | Verificar datos en DuckDB (opcional). |

El **ROW_NUMBER() … PARTITION BY …** entra en juego dentro del **Paso 3**, en el asset **staging.trips**, para deduplicar antes de escribir en `staging.trips`.
