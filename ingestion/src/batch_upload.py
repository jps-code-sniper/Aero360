"""
Script para generar multiples vuelos de prueba y subirlos a GCS
"""

import json
import random
import os
from datetime import datetime, timedelta
from google.cloud import storage

# Configuracion
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "aero360-482417-vuelos-landing")
NUM_VUELOS = 20


def generar_vuelo(fecha_base):
    """Genera un vuelo aleatorio"""
    vuelos = ["AR1302", "LA456", "IB203", "AA901", "AV100", "CM501"]
    origenes = ["EZE", "SCL", "MAD", "MIA", "BOG", "LIM"]
    destinos = ["GRU", "CDG", "JFK", "MEX", "PTY", "CCS"]

    origen = random.choice(origenes)
    destino = random.choice([d for d in destinos if d != origen])

    return {
        "flight_id": random.choice(vuelos),
        "timestamp": fecha_base.isoformat(),
        "origin": origen,
        "destination": destino,
        "passengers": random.randint(80, 280),
        "fuel_level": round(random.uniform(40.0, 95.0), 2),
    }


def generar_multiples_vuelos(cantidad):
    """Genera una lista de vuelos con fechas variadas"""
    vuelos = []
    fecha_base = datetime.now()

    for i in range(cantidad):
        # Variar la fecha entre los ultimos 7 dias
        dias_atras = random.randint(0, 6)
        horas = random.randint(0, 23)
        fecha = fecha_base - timedelta(days=dias_atras, hours=horas)

        vuelo = generar_vuelo(fecha)
        vuelos.append(vuelo)
        print(
            f"Vuelo {i + 1}: {vuelo['flight_id']} {vuelo['origin']} -> {vuelo['destination']}"
        )

    return vuelos


def subir_a_gcs(datos, bucket_name, destino):
    """Sube datos JSON a GCS"""
    cliente = storage.Client()
    bucket = cliente.bucket(bucket_name)
    blob = bucket.blob(destino)

    # Convertir a NDJSON (newline-delimited JSON) para BigQuery
    contenido = "\n".join(json.dumps(v) for v in datos)
    blob.upload_from_string(contenido, content_type="application/json")

    print(f"\n[OK] {len(datos)} vuelos subidos a gs://{bucket_name}/{destino}")


if __name__ == "__main__":
    print(f"Generando {NUM_VUELOS} vuelos de prueba...\n")

    vuelos = generar_multiples_vuelos(NUM_VUELOS)

    # Guardar localmente
    with open("vuelos_batch.json", "w") as f:
        for v in vuelos:
            f.write(json.dumps(v) + "\n")
    print("\n[OK] Guardado en vuelos_batch.json")

    # Subir a GCS
    print(f"\nSubiendo a bucket: {BUCKET_NAME}")
    subir_a_gcs(vuelos, BUCKET_NAME, "landing/vuelos_batch.json")
