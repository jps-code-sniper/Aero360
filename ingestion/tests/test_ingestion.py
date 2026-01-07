"""
Tests unitarios para el módulo de ingestion
Ejecutar con: pytest tests/ -v
"""

import json
import os
import sys
import tempfile

# Agregamos el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generator import generar_datos_vuelo
from validator import validar_esquema, validar_reglas_negocio


class TestGenerador:
    """Tests para el generador de datos sintéticos"""
    
    def test_genera_diccionario(self):
        """Verifica que genera un diccionario válido"""
        vuelo = generar_datos_vuelo()
        assert isinstance(vuelo, dict)
    
    def test_campos_requeridos(self):
        """Verifica que todos los campos requeridos están presentes"""
        vuelo = generar_datos_vuelo()
        campos = ['flight_id', 'timestamp', 'origin', 'destination', 'passengers', 'fuel_level']
        for campo in campos:
            assert campo in vuelo, f"Falta el campo {campo}"
    
    def test_rango_pasajeros(self):
        """Verifica que los pasajeros están en rango válido"""
        for _ in range(10):
            vuelo = generar_datos_vuelo()
            assert 50 <= vuelo['passengers'] <= 250
    
    def test_rango_combustible(self):
        """Verifica que el combustible está en rango válido"""
        for _ in range(10):
            vuelo = generar_datos_vuelo()
            assert 10.5 <= vuelo['fuel_level'] <= 99.9


class TestValidadorEsquema:
    """Tests para la validación de esquema JSON"""
    
    def test_datos_validos(self):
        """Datos correctos deben pasar la validación"""
        datos = {
            "flight_id": "AR1302",
            "timestamp": "2024-01-15T10:30:00",
            "origin": "EZE",
            "destination": "GRU",
            "passengers": 180,
            "fuel_level": 85.5
        }
        es_valido, error = validar_esquema(datos)
        assert es_valido is True
        assert error == ""
    
    def test_flight_id_invalido(self):
        """Flight ID con formato incorrecto debe fallar"""
        datos = {
            "flight_id": "INVALIDO123",
            "timestamp": "2024-01-15T10:30:00",
            "origin": "EZE",
            "destination": "GRU",
            "passengers": 180,
            "fuel_level": 85.5
        }
        es_valido, error = validar_esquema(datos)
        assert es_valido is False
    
    def test_pasajeros_fuera_rango(self):
        """Pasajeros fuera del rango permitido debe fallar"""
        datos = {
            "flight_id": "AR1302",
            "timestamp": "2024-01-15T10:30:00",
            "origin": "EZE",
            "destination": "GRU",
            "passengers": 1000,  # Más de 500
            "fuel_level": 85.5
        }
        es_valido, error = validar_esquema(datos)
        assert es_valido is False


class TestValidadorReglasNegocio:
    """Tests para las reglas de negocio"""
    
    def test_mismo_origen_destino(self):
        """Origen igual a destino debe generar error"""
        datos = {
            "origin": "EZE",
            "destination": "EZE",
            "fuel_level": 80,
            "passengers": 150
        }
        es_valido, problemas = validar_reglas_negocio(datos)
        assert es_valido is False
        assert any("mismo aeropuerto" in p or "ERROR" in p for p in problemas)
    
    def test_combustible_bajo(self):
        """Combustible bajo debe generar advertencia"""
        datos = {
            "origin": "EZE",
            "destination": "GRU",
            "fuel_level": 15,
            "passengers": 150
        }
        es_valido, problemas = validar_reglas_negocio(datos)
        # Es válido pero con advertencia
        assert es_valido is True
        assert any("Combustible bajo" in p for p in problemas)
    
    def test_datos_normales(self):
        """Datos normales no deben generar problemas"""
        datos = {
            "origin": "EZE",
            "destination": "GRU",
            "fuel_level": 80,
            "passengers": 150
        }
        es_valido, problemas = validar_reglas_negocio(datos)
        assert es_valido is True
        assert len(problemas) == 0
