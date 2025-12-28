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
        url = f"{BASE_URL}/search/movie"
        params = {'api_key': API_KEY, 'query': titulo, 'language': 'es-MX'}
        try:
            res = requests.get(url, params=params)
            data = res.json()
            if data['results']:
                return data['results'][0]['id']
        except Exception as e:
            print(f"Error ID {titulo}: {e}")
        return None
    
    def obtener_streaming(self, movie_id):
        """Busca en qué plataformas está disponible"""
        if not movie_id: return "Sin ID"
        
        url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
        params = {'api_key': API_KEY}
        try:
            res = requests.get(url, params=params)
            data = res.json()
            if 'results' in data and PAIS in data['results']:
                flatrate = data['results'][PAIS].get('flatrate')
                if flatrate:
                    nombres = [p['provider_name'] for p in flatrate]
                    return ", ".join(nombres)
        except:
            pass
        return "No disponible en streaming"

    def obtener_poster(self, movie_id):
        """Obtiene la URL absoluta del póster para usar en web"""
        if not movie_id: return None
        
        url_api = f"{BASE_URL}/movie/{movie_id}"
        try:
            # Consultamos los detalles de la película
            res = requests.get(url_api, params={'api_key': API_KEY})
            data = res.json()
            
            poster_path = data.get('poster_path')
            if poster_path:
                # Concatenamos la URL base de imágenes de TMDB
                # w500 es un buen tamaño para web (no muy pesado, buena calidad)
                return f"{IMG_BASE_URL}{poster_path}"
        except Exception as e:
            print(f"Error obteniendo poster: {e}")
            
        # Si falla, podemos devolver una imagen por defecto o None
        return "https://via.placeholder.com/300x450?text=No+Poster"

    def ejecutar(self):
        print("Proceso aún no implementado.")

if __name__ == "__main__":
    # Prueba
    app = Fuente4Media("datos_integrados_f1_f2.csv")
    app.ejecutar()