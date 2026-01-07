"""
Aero360 - Validador de Datos de Vuelos

Este módulo valida los datos de vuelos antes de subirlos a GCS.
Aplica dos niveles de validación:
  1. Esquema JSON: estructura y tipos de datos
  2. Reglas de negocio: lógica específica de la aerolínea
"""

import json
import os
from typing import Tuple

from jsonschema import validate, ValidationError


# Esquema JSON que define la estructura esperada de un vuelo
FLIGHT_SCHEMA = {
    "type": "object",
    "required": [
        "flight_id",
        "timestamp",
        "origin",
        "destination",
        "passengers",
        "fuel_level",
    ],
    "properties": {
        "flight_id": {
            "type": "string",
            "pattern": "^[A-Z]{2}[0-9]{3,4}$",
            "description": "Formato: 2 letras + 3-4 dígitos (ej: AR1302)",
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "Marca de tiempo en formato ISO 8601",
        },
        "origin": {
            "type": "string",
            "pattern": "^[A-Z]{3}$",
            "description": "Código IATA del aeropuerto de origen (3 letras)",
        },
        "destination": {
            "type": "string",
            "pattern": "^[A-Z]{3}$",
            "description": "Código IATA del aeropuerto de destino (3 letras)",
        },
        "passengers": {
            "type": "integer",
            "minimum": 1,
            "maximum": 500,
            "description": "Cantidad de pasajeros (entre 1 y 500)",
        },
        "fuel_level": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Nivel de combustible en porcentaje (0-100)",
        },
    },
    "additionalProperties": False,
}


def validar_esquema(data: dict) -> Tuple[bool, str]:
    """
    Valida que los datos cumplan con el esquema JSON definido.

    Parámetros:
        data: Diccionario con los datos del vuelo

    Retorna:
        Tupla (es_valido, mensaje_error)
    """
    try:
        validate(instance=data, schema=FLIGHT_SCHEMA)
        return True, ""
    except ValidationError as e:
        return False, f"Error de esquema: {e.message}"


def validar_reglas_negocio(data: dict) -> Tuple[bool, list]:
    """
    Aplica reglas de negocio adicionales más allá del esquema.

    Estas reglas capturan lógica específica de la aerolínea que
    no puede expresarse solo con validación de tipos.

    Parámetros:
        data: Diccionario con los datos del vuelo

    Retorna:
        Tupla (es_valido, lista_de_problemas)
    """
    problemas = []

    # Regla 1: El origen y destino no pueden ser el mismo aeropuerto
    if data.get("origin") == data.get("destination"):
        problemas.append("[ERROR] El origen y destino son el mismo aeropuerto")

    # Regla 2: Alerta si el combustible está por debajo del 20%
    combustible = data.get("fuel_level", 0)
    if combustible < 20:
        problemas.append(f"[WARN] Advertencia: Combustible bajo ({combustible}%)")

    # Regla 3: Alerta si hay más de 400 pasajeros (capacidad inusual)
    pasajeros = data.get("passengers", 0)
    if pasajeros > 400:
        problemas.append(
            f"[WARN] Advertencia: Cantidad inusual de pasajeros ({pasajeros})"
        )

    # Determinamos si hay errores críticos (no solo advertencias)
    hay_errores = any("[ERROR]" in problema for problema in problemas)

    return not hay_errores, problemas


def validar_archivo_vuelo(ruta_archivo: str) -> Tuple[bool, dict]:
    """
    Valida un archivo JSON completo de datos de vuelo.

    Ejecuta todas las validaciones y genera un reporte detallado.

    Parámetros:
        ruta_archivo: Ruta al archivo JSON

    Retorna:
        Tupla (es_valido, resultado_validacion)
    """
    resultado = {
        "ruta_archivo": ruta_archivo,
        "es_valido": False,
        "esquema_valido": False,
        "reglas_validas": False,
        "errores": [],
        "advertencias": [],
    }

    # Verificamos que el archivo exista
    if not os.path.exists(ruta_archivo):
        resultado["errores"].append(f"Archivo no encontrado: {ruta_archivo}")
        return False, resultado

    # Intentamos cargar el JSON
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        resultado["errores"].append(f"JSON inválido: {e}")
        return False, resultado

    # Validación de esquema
    esquema_ok, error_esquema = validar_esquema(data)
    resultado["esquema_valido"] = esquema_ok
    if not esquema_ok:
        resultado["errores"].append(error_esquema)

    # Validación de reglas de negocio
    reglas_ok, problemas = validar_reglas_negocio(data)
    resultado["reglas_validas"] = reglas_ok

    for problema in problemas:
        if "[ERROR]" in problema:
            resultado["errores"].append(problema)
        else:
            resultado["advertencias"].append(problema)

    # El archivo es válido solo si pasa ambas validaciones
    resultado["es_valido"] = esquema_ok and reglas_ok

    return resultado["es_valido"], resultado


def imprimir_reporte(resultado: dict) -> None:
    """Imprime un reporte de validación formateado en consola."""
    print("\n" + "=" * 50)
    print("REPORTE DE VALIDACION DE VUELO")
    print("=" * 50)
    print(f"Archivo: {resultado['ruta_archivo']}")
    print(f"Esquema válido: {'SI' if resultado['esquema_valido'] else 'NO'}")
    print(f"Reglas de negocio: {'SI' if resultado['reglas_validas'] else 'NO'}")

    if resultado["errores"]:
        print("\nERRORES ENCONTRADOS:")
        for error in resultado["errores"]:
            print(f"  - {error}")

    if resultado["advertencias"]:
        print("\nADVERTENCIAS:")
        for advertencia in resultado["advertencias"]:
            print(f"  - {advertencia}")

    print("\n" + "-" * 50)
    if resultado["es_valido"]:
        print("[OK] RESULTADO: Los datos son VALIDOS para ingesta")
    else:
        print("[FAIL] RESULTADO: Los datos NO pasaron la validación")
    print("=" * 50 + "\n")


# Punto de entrada principal
if __name__ == "__main__":
    # Construimos la ruta al archivo de prueba
    DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
    ARCHIVO_TEST = os.path.join(DIRECTORIO_BASE, "..", "..", "data", "flight_test.json")

    # También buscamos el archivo generado localmente
    ARCHIVO_LOCAL = os.path.join(DIRECTORIO_BASE, "vuelo_test.json")

    # Usamos el archivo local si existe, sino el de prueba
    archivo_objetivo = ARCHIVO_LOCAL if os.path.exists(ARCHIVO_LOCAL) else ARCHIVO_TEST

    es_valido, resultado = validar_archivo_vuelo(archivo_objetivo)
    imprimir_reporte(resultado)

    # Código de salida para integración con CI/CD
    exit(0 if es_valido else 1)
