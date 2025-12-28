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
                return f"{IMG_BASE_URL}{poster_path}"
        except Exception as e:
            print(f"Error obteniendo poster: {e}")
            
        # Si falla, podemos devolver una imagen por defecto o None
        return "https://via.placeholder.com/300x450?text=No+Poster"

    def ejecutar(self):
        print(f"[INFO] Cargando dataset: {self.archivo_entrada}...")
        
        try:
            df = pd.read_csv(self.archivo_entrada)
        except FileNotFoundError:
            print("[ERROR] No se encuentra el archivo de entrada.")
            return

        col_titulo = 'titulo' 
        
        print(f"[INFO] Iniciando procesamiento de {len(df)} registros...")
        print("-" * 50)

        nuevos_streaming = []
        nuevas_urls_poster = []

        for index, row in df.iterrows():
            titulo = row[col_titulo]
            
            # 1. Buscar ID
            movie_id = self.buscar_id(titulo)

            # 2. Streaming
            st_info = self.obtener_streaming(movie_id)
            nuevos_streaming.append(st_info)

            # 3. Poster (URL)
            url_poster = self.obtener_poster(movie_id)
            nuevas_urls_poster.append(url_poster)
        
            estado_poster = "OK" if url_poster else "N/A"
            print(f"[{index+1}/{len(df)}] {titulo} | Prov: {st_info} | Img: {estado_poster}")
            
            time.sleep(0.1)

        self.df_resultado = df
        self.df_resultado['plataformas'] = nuevos_streaming
        self.df_resultado['poster_url'] = nuevas_urls_poster
        
        print("-" * 50)
        print("[OK] Procesamiento en memoria finalizado.")
        
        # Llamamos al guardado
        self.guardar_resultados()

if __name__ == "__main__":
    # Prueba
    app = Fuente4Media("datos_integrados_f1_f2.csv")
    app.ejecutar()