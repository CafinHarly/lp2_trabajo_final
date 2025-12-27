import requests
import pandas as pd
import time

API_KEY = "69d810ef"
BASE_URL = "https://www.omdbapi.com/"

KEYWORDS_GENERALES = [
    "love", "war", "dark", "star", "life","world", "game", "last"
]

MAX_PELICULAS = 70 

def buscar_peliculas_generales(keywords, paginas=1):
    imdb_ids = set()
    print("🔍 Paso 1: Buscando IDs de películas en la API...")

    for kw in keywords:
        if len(imdb_ids) >= MAX_PELICULAS:
            break
        
        print(f"   -> Buscando por palabra clave: '{kw}'")
        for page in range(1, paginas + 1):
            params = {
                "s": kw,
                "type": "movie",
                "page": page,
                "apikey": API_KEY
            }

            try:
                response = requests.get(BASE_URL, params=params)
                data = response.json()

                if data.get("Response") == "True":
                    for item in data["Search"]:
                        imdb_ids.add(item["imdbID"])
                else:
                    break
            except Exception as e:
                print(f"      Error en búsqueda: {e}")

            time.sleep(0.3)

    print(f"✅ Se encontraron {len(imdb_ids)} IDs únicos.\n")
    return list(imdb_ids)


def obtener_detalle_peliculas(imdb_ids):
    registros = []
    total_a_procesar = min(len(imdb_ids), MAX_PELICULAS)
    
    print(f"🚀 Paso 2: Extrayendo detalles de {total_a_procesar} películas...")

    for i, imdb_id in enumerate(imdb_ids):
        if i >= MAX_PELICULAS:
            break

        params = {
            "i": imdb_id,
            "apikey": API_KEY
        }

        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if data.get("Response") == "True":
                registros.append({
                    "imdb_id": data["imdbID"],
                    "titulo": data["Title"],
                    "anio": data["Year"],
                    "genero": data["Genre"],
                    "rating_imdb": float(data["imdbRating"]) if data["imdbRating"] != "N/A" else None
                })
                # Esto te permite ver el progreso en VS Code
                print(f"   [{i+1}/{total_a_procesar}] Procesado: {data['Title']}")
        except Exception as e:
            print(f"      Error al obtener detalle de {imdb_id}: {e}")

        time.sleep(0.3)

    return pd.DataFrame(registros)

if __name__ == "__main__":
    start_time = time.time() # Para medir cuánto tarda
    
    ids = buscar_peliculas_generales(KEYWORDS_GENERALES)
    df_api = obtener_detalle_peliculas(ids)

    # Guardar el archivo
    df_api.to_csv("datos_peliculas_generales_omdb.csv", index=False)

    print("\n" + "="*30)
    print("✨ ¡EXTRACCIÓN EXITOSA!")
    print(f"📊 Total: {len(df_api)} películas guardadas.")
    print(f"🕒 Tiempo total: {round(time.time() - start_time, 2)} segundos.")
    print("="*30)
    print(df_api.head())