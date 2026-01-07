{{ config(materialized='ephemeral') }}

/*
    Modelo Intermedio: Métricas de vuelos por ruta
    
    Agrega métricas clave para cada par origen-destino,
    permitiendo analizar el rendimiento de cada ruta.
*/

with vuelos as (
    -- Tomamos los datos limpios del modelo staging
    select * from {{ ref('stg_flights') }}
),

metricas_por_ruta as (
    select
        origin_airport,
        destination_airport,
        
        -- Identificador legible de la ruta
        concat(origin_airport, ' → ', destination_airport) as nombre_ruta,
        
        -- Métricas de volumen
        count(*) as total_vuelos,
        sum(passenger_count) as total_pasajeros,
        
        -- Promedios por vuelo
        round(avg(passenger_count), 1) as promedio_pasajeros,
        round(avg(fuel_percentage), 2) as promedio_combustible,
        
        -- Utilización de capacidad (asumiendo máximo 250 pasajeros por vuelo)
        round(avg(passenger_count) / 250.0 * 100, 1) as porcentaje_capacidad,
        
        -- Rango temporal de operación
        min(event_at) as primer_vuelo,
        max(event_at) as ultimo_vuelo
        
    from vuelos
    group by origin_airport, destination_airport
)

select * from metricas_por_ruta
