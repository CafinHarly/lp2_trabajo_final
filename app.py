import streamlit as st
import pandas as pd
import requests  # Faltaba importar requests explícitamente
import cloudscraper 
from bs4 import BeautifulSoup
import time
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador PRO", layout="wide", page_icon="🎬")
API_KEY_OMDB = "69d810ef" 

# ==========================================
# 🧠 LÓGICA 1: OMDb API (Oficial)
# ==========================================
def buscar_omdb(keyword):
    imdb_ids = []
    url = "https://www.omdbapi.com/"
    
    # Barra de progreso
    progress = st.progress(0)
    status = st.empty()
    
    # Buscamos en 2 páginas
    for page in range(1, 3):
        status.text(f"OMDb API: Buscando página {page}...")
        params = {"s": keyword, "type": "movie", "page": page, "apikey": API_KEY_OMDB}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("Response") == "True":
                for item in data["Search"]:
                    imdb_ids.append(item["imdbID"])
            else:
                break
        except Exception as e:
            st.error(f"Error conectando con OMDb: {e}")
            break
            
        progress.progress(page * 50)
    
    # Obtenemos detalles
    registros = []
    total = len(imdb_ids)
    
    if total > 0:
        for i, imdb_id in enumerate(imdb_ids):
            status.text(f"OMDb: Descargando detalles {i+1}/{total}...")
            params_detail = {"i": imdb_id, "apikey": API_KEY_OMDB}
            try:
                resp = requests.get(url, params=params_detail).json()
                
                if resp.get("Response") == "True":
                    registros.append({
                        "Fuente": "OMDb",
                        "Título": resp.get("Title"),
                        "Año": resp.get("Year"),
                        "Rating": resp.get("imdbRating"),
                        "Poster": resp.get("Poster")
                    })
            except:
                continue
    
    progress.empty()
    status.empty()
    return pd.DataFrame(registros)


# ==========================================
# 🕷️ LÓGICA 2: FilmAffinity (Anti-Bloqueo)
# ==========================================
def buscar_filmaffinity(keyword):
    # Simulamos ser un navegador real
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    url_base = "https://www.filmaffinity.com/pe/search.php"
    parametros = {'stext': keyword}
    
    status = st.empty()
    status.info(f"🕸️ Conectando a FilmAffinity...")
    
    try:
        time.sleep(random.uniform(0.5, 1.5)) # Pausa humana
        response = scraper.get(url_base, params=parametros)
        
        if response.status_code != 200:
            status.error(f"Error de conexión: {response.status_code}")
            return pd.DataFrame()

        soup = BeautifulSoup(response.text, 'html.parser')
        registros = []
        
        resultados = soup.find_all('div', class_='se-it')
        
        if not resultados:
            # Lógica de redirección directa
            if soup.find('h1', {'id': 'main-title'}):
                t = soup.find('h1', {'id': 'main-title'}).get_text(strip=True)
                registros.append({"Fuente": "FilmAffinity", "Título": t, "Año": "Ficha", "Rating": "-", "Poster": None})
                return pd.DataFrame(registros)
            else:
                status.warning("No se encontraron resultados.")
                return pd.DataFrame()
        
        status.text(f"Procesando {len(resultados)} resultados...")
        
        for item in resultados[:10]: 
            try:
                titulo = item.find('div', class_='mc-title').get_text(strip=True)
                anio = item.find('div', class_='ye-w').get_text(strip=True) if item.find('div', class_='ye-w') else "-"
                
                img_tag = item.find('img')
                poster = img_tag['src'] if img_tag else None
                if img_tag and 'data-src' in img_tag.attrs:
                    poster = img_tag['data-src']

                rating = item.find('div', class_='avgrat-box').get_text(strip=True) if item.find('div', class_='avgrat-box') else "-"

                registros.append({
                    "Fuente": "FilmAffinity",
                    "Título": titulo,
                    "Año": anio,
                    "Rating": rating,
                    "Poster": poster
                })
            except:
                continue

        status.empty()
        return pd.DataFrame(registros)

    except Exception as e:
        status.error(f"Error técnico: {e}")
        return pd.DataFrame()

# ==========================================
# 🎨 INTERFAZ PRINCIPAL
# ==========================================
st.title("🎬 Buscador Universal")

with st.sidebar:
    st.header("Configuración")
    fuente = st.radio("Fuente de datos:", ("OMDb API", "FilmAffinity"))

keyword = st.text_input("Escribe una película:", placeholder="Ej. Gladiador")

if st.button("Buscar Película"):
    if not keyword:
        st.warning("Escribe algo primero.")
    else:
        df = pd.DataFrame()
        
        # AQUÍ ESTABA EL ERROR ANTES: AHORA LLAMAMOS A LAS FUNCIONES CORRECTAS
        if fuente == "OMDb API":
            with st.spinner("Consultando OMDb..."):
                df = buscar_omdb(keyword)
        else:
            with st.spinner("Scrapeando FilmAffinity..."):
                df = buscar_filmaffinity(keyword)

        # Mostrar resultados
        if not df.empty:
            st.success(f"Encontradas {len(df)} películas.")
            st.dataframe(
                df,
                column_config={
                    "Poster": st.column_config.ImageColumn("Póster", width="small")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.error("No se encontraron resultados.")