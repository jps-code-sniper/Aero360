{{ config(materialized='table') }}

/*
    Modelo Staging: Limpieza de datos crudos de vuelos
    
    Este modelo toma los datos raw de BigQuery y aplica:
    1. Conversión de tipos de datos
    2. Normalización de valores nulos
    3. Deduplicación por flight_id
*/

with datos_origen as (
    -- Traemos todos los datos de la tabla externa en BigQuery
    select * from {{ source('gcp_raw', 'stg_vuelos_raw') }}
),

datos_limpios as (
    select
        -- Convertimos strings vacíos a NULL para manejo consistente
        nullif(cast(flight_id as STRING), '') as flight_id,
        
        -- Renombramos columnas con nombres más descriptivos
        cast(origin as STRING) as origin_airport,
        cast(destination as STRING) as destination_airport,
        
        -- Aseguramos tipos numéricos correctos
        cast(passengers as INT64) as passenger_count,
        cast(fuel_level as FLOAT64) as fuel_percentage,
        
        -- Convertimos el timestamp a tipo TIMESTAMP de BigQuery
        timestamp(timestamp) as event_at
        
    from datos_origen
),

datos_deduplicados as (
    select
        *,
        -- Numeramos los registros por flight_id, el más reciente es 1
        row_number() over (
            partition by flight_id 
            order by event_at desc
        ) as numero_fila
    from datos_limpios
    -- Excluimos registros sin flight_id válido
    where flight_id is not null 
)

-- Seleccionamos únicamente el registro más reciente de cada vuelo
select
    flight_id,
    origin_airport,
    destination_airport,
    passenger_count,
    fuel_percentage,
    event_at
from datos_deduplicados
where numero_fila = 1