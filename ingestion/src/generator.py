"""
Aero360 - Generador de Datos de Vuelos

Este módulo genera datos sintéticos de vuelos para simular
el flujo de información de una aerolínea en tiempo real.
"""

import json
import random
from datetime import datetime


def generar_datos_vuelo():
    """
    Genera un diccionario con datos aleatorios de un vuelo.
    
    Los datos simulan información típica de un sistema de gestión
    de vuelos: identificador, ruta, pasajeros y nivel de combustible.
    """
    # Códigos de vuelo de aerolíneas latinoamericanas y europeas
    vuelos = ['AR1302', 'LA456', 'IB203', 'AA901']
    
    # Aeropuertos principales (códigos IATA)
    origenes = ['EZE', 'SCL', 'MAD', 'MIA']
    destinos = ['GRU', 'CDG', 'JFK', 'LIM']
    
    data = {
        "flight_id": random.choice(vuelos),
        "timestamp": datetime.now().isoformat(),
        "origin": random.choice(origenes),
        "destination": random.choice(destinos),
        "passengers": random.randint(50, 250),
        "fuel_level": round(random.uniform(10.5, 99.9), 2)
    }
    return data


# Punto de entrada: genera un vuelo y lo guarda en archivo local
if __name__ == "__main__":
    vuelo_actual = generar_datos_vuelo()
    
    # Guardamos el vuelo en formato JSON para pruebas locales
    with open('vuelo_test.json', 'w') as f:
        json.dump(vuelo_actual, f, indent=2)
    
    print(f"Vuelo generado: {vuelo_actual['flight_id']}")
    print(f"Ruta: {vuelo_actual['origin']} → {vuelo_actual['destination']}")
    print(f"Pasajeros: {vuelo_actual['passengers']}")