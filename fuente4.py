import pandas as pd
import requests
import os
import time

# --- CONFIGURACIÓN ---
API_KEY = "503dbd676ae9d8d8fa1b4bff4628ac7c"
BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w500"
PAIS = "PE"

class Fuente4Media:
    def __init__(self, archivo_entrada):
        self.archivo_entrada = archivo_entrada
        print(f"--- Inicializando Fuente 4 para: {archivo_entrada} ---")

    def buscar_id(self, titulo):
        """Busca el ID de la película en TMDB"""
        pass

    def obtener_streaming(self, movie_id):
        """Busca en qué plataformas está disponible"""
        pass

    def obtener_poster(self, movie_id):
        """Descarga el póster de la película"""
        pass

    def ejecutar(self):
        print("Proceso aún no implementado.")

if __name__ == "__main__":
    # Prueba
    app = Fuente4Media("datos_integrados_f1_f2.csv")
    app.ejecutar()