import streamlit as st
import requests
import pandas as pd
import time
from bs4 import BeautifulSoup # Importante para el scraping

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador Multi-Fuente", layout="wide")
API_KEY_OMDB = "69d810ef" 

# ==========================================
# 🧠 LÓGICA 1: OMDb API (Tu código anterior)
# ==========================================
def buscar_omdb(keyword):
    # Buscamos primero los IDs
    imdb_ids = []
    url = "https://www.omdbapi.com/"
    
    # Barra de progreso simulada
    progress = st.progress(0)
    status = st.empty()
    
    # Buscamos 2 páginas para que sea rápido
    for page in range(1, 3):
        status.text(f"OMDb API: Buscando página {page}...")
        params = {"s": keyword, "type": "movie", "page": page, "apikey": API_KEY_OMDB}
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("Response") == "True":
            for item in data["Search"]:
                imdb_ids.append(item["imdbID"])
        else:
            break
        progress.progress(page * 50)
    
    # Obtenemos detalles
    registros = []
    total = len(imdb_ids)
    
    for i, imdb_id in enumerate(imdb_ids):
        status.text(f"OMDb: Descargando detalles {i+1}/{total}...")
        params_detail = {"i": imdb_id, "apikey": API_KEY_OMDB}
        resp = requests.get(url, params=params_detail).json()
        
        if resp.get("Response") == "True":
            registros.append({
                "Fuente": "OMDb",
                "Título": resp.get("Title"),
                "Año": resp.get("Year"),
                "Rating": resp.get("imdbRating"),
                "Poster": resp.get("Poster")
            })
    
    progress.empty()
    status.empty()
    return pd.DataFrame(registros)

# ==========================================
# 🕷️ LÓGICA 2: FilmAffinity (WEB SCRAPING)
# ==========================================
def buscar_filmaffinity(keyword):
    # Usamos params para que requests se encargue de los espacios en "Toy Story" -> "Toy+Story"
    url_base = "https://www.filmaffinity.com/es/search.php"
    parametros = {'stext': keyword}
    
    # CABECERAS COMPLETAS (El disfraz perfecto)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8', # Importante para que sepan que hablas español
        'Referer': 'https://www.google.com/', # Fingimos venir de Google
        'Connection': 'keep-alive'
    }
    
    st.info(f"🕸️ Intentando conectar con FilmAffinity para: {keyword}...")
    
    try:
        response = requests.get(url_base, params=parametros, headers=headers, timeout=10)
        
        # DEBUG: Si falla, esto nos dirá por qué en la pantalla
        if response.status_code != 200:
            st.error(f"Error de conexión. Código: {response.status_code}")
            return pd.DataFrame()

        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        registros = []
        
        # Buscamos los resultados (Clase 'se-it' es la tarjeta de la peli en la lista)
        resultados = soup.find_all('div', class_='se-it')
        
        if not resultados:
            st.warning("Conectó, pero no encontré las etiquetas 'se-it'. Puede que FilmAffinity haya cambiado su diseño o redirigido a la ficha directa.")
        
        for item in resultados[:5]: 
            try:
                # Título
                titulo_tag = item.find('div', class_='mc-title')
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sin título"
                
                # Año
                anio_tag = item.find('div', class_='ye-w')
                anio = anio_tag.get_text(strip=True) if anio_tag else "-"
                
                # Poster
                img_tag = item.find('img')
                poster_url = img_tag['src'] if img_tag else None
                
                # Rating
                rating_tag = item.find('div', class_='avgrat-box')
                rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

                registros.append({
                    "Fuente": "FilmAffinity",
                    "Título": titulo,
                    "Año": anio,
                    "Rating": rating,
                    "Poster": poster_url
                })
            except Exception:
                continue

        return pd.DataFrame(registros)

    except Exception as e:
        st.error(f"Ocurrió un error grave: {e}")
        return pd.DataFrame()