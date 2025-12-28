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
        self.df_resultado = None
        print(f"--- Inicializando Fuente 4 para: {archivo_entrada} ---")

    def buscar_id_por_imdb(self, imdb_id):
        # Para unificar el id con una excepción para obtener su disponibilidad en streaming 
        if pd.isna(imdb_id) or str(imdb_id).strip() == "":
            return None

        # Endpoint '/find/{id}' es específico para IDs externos
        url = f"{BASE_URL}/find/{imdb_id}"
        params = {
            'api_key': API_KEY,
            'external_source': 'imdb_id'
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if data.get('movie_results'):
                return data['movie_results'][0]['id']
        except Exception as e:
            print(f"[ERROR] Buscando ID para {imdb_id}: {e}")
            
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

    def obtener_poster_url(self, movie_id):
        """Obtiene la URL absoluta del póster para usar en web"""
        if not movie_id: return None
        
        url_api = f"{BASE_URL}/movie/{movie_id}"
        try:
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
        
        print(f"[INFO] Iniciando procesamiento de {len(df)} registros...")
        print("-" * 60)

        col_streaming = []
        col_posters = []

        for index, row in df.iterrows():
            id_externo = row['imdb_id']
            # Usamos el título solo para mostrarlo en el log (si existe)
            titulo_ref = row.get('titulo', 'Pelicula') 
            
            # 1. Obtener ID de TMDB
            tmdb_id = self.buscar_id_por_imdb(id_externo)

            # 2. Obtener datos usando ese ID
            st_info = self.obtener_streaming(tmdb_id)
            url_img = self.obtener_poster_url(tmdb_id)
            
            col_streaming.append(st_info)
            col_posters.append(url_img)
            
            estado_img = "OK" if "http" in str(url_img) else "Falta"
            print(f"[{index+1}/{len(df)}] {id_externo} | Stream: {st_info[:15]}... | Poster: {estado_img}")
            
            time.sleep(0.1) 

        self.df_resultado = df
        self.df_resultado['plataformas'] = col_streaming
        self.df_resultado['poster_url'] = col_posters
        
        print("-" * 60)
        print("[OK] Procesamiento en memoria finalizado.")

        self.guardar_resultados()
        
    def guardar_resultados(self):
        nombre_salida = "datos_integrados_124.csv"
        try:
            self.df_resultado.to_csv(nombre_salida, index=False)
            print(f"[INFO] Archivo generado exitosamente: {nombre_salida}")
        except Exception as e:
            print(f"[ERROR] Fallo al guardar archivo: {e}")

if __name__ == "__main__":
    app = Fuente4Media("datos_integrados_f1_f2.csv") 
    app.ejecutar()