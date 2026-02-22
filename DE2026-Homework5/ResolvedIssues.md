# 🎯 Resumen de Problemas Resueltos - Pipeline Bruin NYC Taxi

## 1. **Error: "failed to install ingestr: exit status 2"**

**🔴 Problema:**
```
error: failed to remove file `ingestr.exe`: El proceso no tiene acceso al archivo porque está siendo utilizado por otro proceso. (os error 32)
```

**🔍 Causa Raíz:**
- El proceso `ingestr.exe` estaba ejecutándose en segundo plano
- Windows bloqueaba el archivo (error 32) porque otro proceso lo tenía abierto
- UV (el gestor de paquetes de Python) intentaba actualizar/reinstalar ingestr pero no podía eliminar el ejecutable

**✅ Solución:**
```powershell
Remove-Item -Recurse -Force "$env:APPDATA\uv\tools\ingestr" -ErrorAction SilentlyContinue
```
- Limpiar completamente la caché de UV para ingestr
- Permitir que se reinstale desde cero en la siguiente ejecución

**📚 Aprendizaje:**
- UV mantiene herramientas en entornos aislados en `%APPDATA%\uv\tools`
- Windows bloquea archivos ejecutables en uso
- A veces es necesario limpiar cachés para resolver conflictos de instalación

---

## 2. **Error: Acceso Concurrente a Base de Datos DuckDB**

**🔴 Problema:**
```
IO Error: Cannot open file "duckdb.db": El proceso no tiene acceso al archivo porque está siendo utilizado por otro proceso.
File is already open in python.exe (PID 5500)
```

**🔍 Causa Raíz:**
- Los assets `ingestion.payment_lookup` e `ingestion.trips` se ejecutaban en **paralelo**
- Ambos intentaban escribir simultáneamente en el mismo archivo `duckdb.db`
- DuckDB en Windows **no soporta múltiples escritores concurrentes** en un solo archivo

**✅ Solución:**
Agregar dependencia en `my-pipeline/pipeline/assets/ingestion/trips.py`:
```python
depends:
  - ingestion.payment_lookup
```

**📚 Aprendizaje:**
- Bruin ejecuta assets en paralelo por defecto para optimizar rendimiento
- DuckDB es una base de datos embebida que bloquea el archivo durante escrituras
- Las dependencias (`depends`) fuerzan ejecución secuencial
- En producción con bases de datos cliente-servidor (PostgreSQL, BigQuery) esto no sería un problema

---

## 3. **Error: PyArrow Timezone Database - "Cannot locate timezone 'UTC'"**

**🔴 Problema:**
```
pyarrow.lib.ArrowInvalid: Cannot locate timezone 'UTC': Timezone database not found at "C:\Users\aYo\Downloads\tzdata"
```

**🔍 Causa Raíz:**
- Los archivos parquet de NYC Taxi contienen timestamps con zona horaria (timezone-aware)
- DLT/ingestr usa PyArrow para procesar DataFrames
- PyArrow necesita la base de datos IANA de zonas horarias para procesar timestamps con timezone
- La base de datos no estaba instalada en la ubicación esperada

**❌ Intentos Fallidos:**
1. Instalar `tzdata` en requirements.txt → No funcionó porque ingestr corre en su propio entorno aislado
2. Crear manualmente el directorio tzdata → PyArrow esperaba formato IANA, no el paquete Python
3. Convertir timestamps a timezone-naive en pandas → DLT/PyArrow los procesaba antes

**✅ Solución Final:**
Convertir timestamps a **strings** en `my-pipeline/pipeline/assets/ingestion/trips.py`:
```python
for col in final_dataframe.columns:
    if pd.api.types.is_datetime64_any_dtype(final_dataframe[col]):
        # Convert to string format to avoid any timezone processing
        final_dataframe[col] = final_dataframe[col].astype(str)
```

Luego convertir de vuelta a TIMESTAMP en `my-pipeline/pipeline/assets/staging/trips.sql`:
```sql
TRY_CAST(pickup_datetime AS TIMESTAMP) AS pickup_dt,
TRY_CAST(dropoff_datetime AS TIMESTAMP) AS dropoff_dt,
```

**📚 Aprendizaje:**
- PyArrow tiene requisitos estrictos para procesar timestamps con timezone
- A veces la solución más simple es convertir tipos de datos temporalmente
- La capa de staging es ideal para transformaciones de tipos de datos
- DLT/ingestr ejecuta código en entornos aislados, complicando la instalación de dependencias

---

## 4. **Error: "Table with name trips does not exist" en Primera Ejecución**

**🔴 Problema:**
```
Catalog Error: Table with name trips does not exist!
Did you mean "ingestion.trips"?
LINE 2: DELETE FROM staging.trips WHERE pickup_datetime BETWEEN...
```

**🔍 Causa Raíz:**
- La estrategia `delete+insert` intenta hacer DELETE antes de INSERT
- En la primera ejecución, la tabla `staging.trips` no existe
- DuckDB falla al intentar ejecutar DELETE en una tabla inexistente

**✅ Solución:**
Primera ejecución con flag `--full-refresh`:
```bash
bruin run pipeline/pipeline.yml --full-refresh --start-date 2022-01-01 --end-date 2022-01-02
```

**📚 Aprendizaje:**
- `--full-refresh` crea tablas desde cero (CREATE TABLE AS)
- Estrategias incrementales (`delete+insert`, `append`) asumen que las tablas ya existen
- Siempre ejecutar pipelines nuevos con `--full-refresh` la primera vez
- Ejecuciones subsecuentes pueden ser incrementales

---

## 5. **Error: "trip_id has 55 non-unique values" en Ejecución Incremental**

**🔴 Problema:**
```
trip_id.unique - column 'trip_id' has 55 non-unique values
```

**🔍 Causa Raíz:**
- `trip_id` se generaba con `ROW_NUMBER()` que produce secuencias 1, 2, 3...
- En ejecución incremental:
  - 1ª ejecución: trip_id = 1, 2, 3... (para enero)
  - 2ª ejecución: trip_id = 1, 2, 3... (para febrero)
  - Resultado: IDs duplicados entre meses

**❌ Solución Incorrecta:**
```sql
ROW_NUMBER() OVER (ORDER BY pickup_datetime) AS trip_id
```

**✅ Solución Correcta:**
Usar hash de columnas en `my-pipeline/pipeline/assets/staging/trips.sql`:
```sql
hash(pickup_dt, dropoff_dt, taxi_type, payment_type, trip_distance, fare_amount) AS trip_id
```

**📚 Aprendizaje:**
- `ROW_NUMBER()` no es apropiado para claves primarias en pipelines incrementales
- Los IDs deben ser **determinísticos** y **únicos globalmente**
- Hash de columnas clave genera IDs consistentes entre ejecuciones
- Alternativas: UUIDs, secuencias distribuidas, o claves naturales compuestas

---

## 🎓 Conceptos Clave Aprendidos

### **Gestión de Dependencias**
- Entornos aislados de Python (UV, virtualenv)
- Diferencia entre dependencias de desarrollo y runtime
- Limitaciones de instalar paquetes en entornos aislados de herramientas

### **Bases de Datos Embebidas**
- DuckDB: ventajas (simplicidad, rendimiento) vs limitaciones (concurrencia)
- Diferencias entre bases de datos embebidas y cliente-servidor
- Estrategias de bloqueo y acceso concurrente

### **Procesamiento de Datos con PyArrow**
- Serialización eficiente con Parquet
- Manejo de timezone-aware vs timezone-naive timestamps
- Conversiones de tipos de datos en pipelines

### **Pipelines Incrementales**
- Estrategias de materialización: `append`, `delete+insert`, `replace`, `merge`
- Importancia de `--full-refresh` en primera ejecución
- Generación de claves primarias en contextos incrementales

### **Data Quality**
- Checks automáticos: `not_null`, `unique`, `positive`, `non_negative`
- Custom checks con SQL
- Importancia de validar constraints en cada ejecución

### **Debugging en Windows**
- Errores de bloqueo de archivos (error 32)
- Gestión de procesos en segundo plano
- Limpieza de cachés y estados inconsistentes

---

## 📊 Resumen de Cambios en el Código

### Archivos Modificados:

1. **`my-pipeline/pipeline/assets/ingestion/trips.py`**
   - ✅ Agregada dependencia `ingestion.payment_lookup`
   - ✅ Conversión de timestamps a strings para evitar PyArrow timezone issues
   - ✅ Timestamp `extracted_at` como timezone-naive

2. **`my-pipeline/pipeline/assets/staging/trips.sql`**
   - ✅ Conversión de strings a TIMESTAMP con `TRY_CAST()`
   - ✅ Cambio de `ROW_NUMBER()` a `hash()` para trip_id
   - ✅ Estrategia `delete+insert` en lugar de `time_interval`

3. **`my-pipeline/pipeline/assets/ingestion/requirements.txt`**
   - ✅ Agregado `tzdata>=2024.1` (aunque finalmente no se usó)

---

## 🚀 Comandos Útiles

### Primera Ejecución (Full Refresh)
```bash
bruin run pipeline/pipeline.yml --start-date 2022-01-01 --end-date 2022-01-31 --var 'taxi_types=["yellow"]' --full-refresh
```

### Ejecución Incremental
```bash
bruin run pipeline/pipeline.yml --start-date 2022-02-01 --end-date 2022-02-28 --var 'taxi_types=["yellow"]'
```

### Múltiples Tipos de Taxi
```bash
bruin run pipeline/pipeline.yml --start-date 2022-01-01 --end-date 2022-12-31 --var 'taxi_types=["yellow","green"]'
```

### Limpiar Caché de UV (En caso de problemas)
```powershell
Remove-Item -Recurse -Force "$env:APPDATA\uv\tools\ingestr" -ErrorAction SilentlyContinue
```

---

**Fecha:** 22 de febrero de 2026  
**Pipeline:** ny_taxi_pipeline  
**Framework:** Bruin  
**Database:** DuckDB  

¡Excelente trabajo debugeando todos estos problemas! 🎉 Cada error te enseñó algo valioso sobre ingeniería de datos en el mundo real.
