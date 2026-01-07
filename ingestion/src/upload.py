"""
Aero360 - Carga de Archivos a Google Cloud Storage

Este módulo se encarga de subir los archivos JSON de vuelos
validados hacia el bucket de GCS configurado como "landing zone".
"""

import os
from google.cloud import storage
from dotenv import load_dotenv

# Cargamos variables de entorno desde archivo .env si existe
load_dotenv()

# Obtenemos la ruta de la carpeta donde está este script
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# Construimos la ruta al archivo JSON de prueba
# Navegamos: src -> ingestion -> Aero360 -> data -> flight_test.json
RUTA_JSON = os.path.join(DIRECTORIO_BASE, "..", "..", "data", "flight_test.json")


def subir_a_gcs(archivo_local: str, nombre_bucket: str, destino_gcs: str) -> bool:
    """
    Sube un archivo local al bucket de Google Cloud Storage.

    Parámetros:
        archivo_local: Ruta al archivo en el sistema local
        nombre_bucket: Nombre del bucket de GCS destino
        destino_gcs: Ruta dentro del bucket donde guardar el archivo

    Retorna:
        True si la subida fue exitosa, False en caso contrario
    """
    # Verificamos que el archivo exista antes de intentar subirlo
    if not os.path.exists(archivo_local):
        print(f"[ERROR] No se encontró el archivo en {archivo_local}")
        return False

    # Creamos el cliente de Storage y subimos el archivo
    cliente_storage = storage.Client()
    bucket = cliente_storage.bucket(nombre_bucket)
    blob = bucket.blob(destino_gcs)
    blob.upload_from_filename(archivo_local)

    print(f"[OK] Archivo subido a gs://{nombre_bucket}/{destino_gcs}")
    return True


# Configuración del bucket
# Usamos variable de entorno con fallback al valor por defecto
BUCKET_POR_DEFECTO = "aero360-482417-vuelos-landing"
MI_BUCKET = os.getenv("GCS_BUCKET_NAME", BUCKET_POR_DEFECTO)


# Punto de entrada principal
if __name__ == "__main__":
    print(f"Subiendo archivo a bucket: {MI_BUCKET}")
    subir_a_gcs(RUTA_JSON, MI_BUCKET, "landing/flight_test.json")
