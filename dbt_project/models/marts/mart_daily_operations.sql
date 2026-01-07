{{ config(materialized='table') }}

/*
    Modelo Mart: Panel de Operaciones Diarias
    
    KPIs listos para consumo ejecutivo, agregados por día.
    Este modelo alimenta dashboards de monitoreo operativo.
*/

with vuelos as (
    -- Datos limpios del staging
    select * from {{ ref('stg_flights') }}
),

estadisticas_diarias as (
    select
        -- Dimensión temporal
        date(event_at) as fecha_operacion,
        extract(dayofweek from event_at) as dia_semana,
        
        -- KPIs de volumen
        count(*) as total_vuelos,
        sum(passenger_count) as total_pasajeros,
        
        -- KPIs de eficiencia
        round(avg(passenger_count), 1) as promedio_pasajeros,
        round(avg(fuel_percentage), 2) as eficiencia_combustible,
        
        -- Métricas de capacidad
        round(sum(passenger_count) / (count(*) * 250.0) * 100, 1) as utilizacion_flota_pct,
        
        -- Diversidad de rutas operadas
        count(distinct origin_airport) as origenes_unicos,
        count(distinct destination_airport) as destinos_unicos,
        count(distinct concat(origin_airport, '-', destination_airport)) as rutas_unicas
        
    from vuelos
    group by date(event_at), extract(dayofweek from event_at)
)

select
    fecha_operacion,
    dia_semana,
    total_vuelos,
    total_pasajeros,
    promedio_pasajeros,
    eficiencia_combustible,
    utilizacion_flota_pct,
    origenes_unicos,
    destinos_unicos,
    rutas_unicas,
    
    -- Clasificación del día
    case 
        when dia_semana in (1, 7) then 'Fin de semana'
        else 'Día hábil'
    end as tipo_dia,
    
    -- Indicador de rendimiento según utilización
    case
        when utilizacion_flota_pct >= 80 then 'Alta'
        when utilizacion_flota_pct >= 50 then 'Media'
        else 'Baja'
    end as nivel_utilizacion

from estadisticas_diarias
order by fecha_operacion desc
