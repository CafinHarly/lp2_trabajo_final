import streamlit as st
import pandas as pd
import requests
import cloudscraper
from bs4 import BeautifulSoup
import time
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador PRO", layout="wide", page_icon="🎬")
API_KEY_OMDB = "69d810ef"

# ==========================================
# 🧠 LÓGICA 1: OMDb API
# ==========================================
def buscar_omdb(keyword):
    url = "https://www.omdbapi.com/"
    imdb_ids = []
    registros = []
    
    for page in range(1, 3):
        try:
            params = {"s": keyword, "type": "movie", "page": page, "apikey": API_KEY_OMDB}
            data = requests.get(url, params=params).json()
            if data.get("Response") == "True":
                for item in data["Search"]:
                    imdb_ids.append(item["imdbID"])
            else:
                break
        except:
            break

    for imdb_id in imdb_ids:
        try:
            params = {"i": imdb_id, "apikey": API_KEY_OMDB}
            item = requests.get(url, params=params).json()
            if item.get("Response") == "True":
                registros.append({
                    "Título": item.get("Title"),
                    "Año": item.get("Year"),
                    "Rating": item.get("imdbRating"),
                    "Poster": item.get("Poster"),
                    "Fuente": "OMDb"
                })
        except:
            continue     
    return pd.DataFrame(registros)

# ==========================================
# 🕷️ LÓGICA 2: FilmAffinity (ACTUALIZADA AL HTML NUEVO)
# ==========================================
def buscar_filmaffinity(keyword):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    # Usamos /pe/ para coincidir con tu HTML
    url = "https://www.filmaffinity.com/pe/search.php"
    
    try:
        time.sleep(random.uniform(0.5, 1.0))
        response = scraper.get(url, params={'stext': keyword})
        
        if response.status_code != 200:
            return pd.DataFrame()

        soup = BeautifulSoup(response.text, 'html.parser')
        registros = []
        
        # 1. CAMBIO CLAVE: Buscamos 'movie-card' en lugar de 'se-it'
        cards = soup.find_all('div', class_='movie-card')
        
        # Si no hay cartas, revisamos si es redirección única (título directo)
        if not cards and soup.find('h1', {'id': 'main-title'}):
            # Lógica simple para ficha única
            t = soup.find('h1', {'id': 'main-title'}).get_text(strip=True)
            registros.append({"Título": t, "Año": "Ficha", "Rating": "-", "Poster": None, "Fuente": "FilmAffinity"})
            return pd.DataFrame(registros)

        for card in cards[:15]:
            try:
                # --- EXTRACCIÓN BASADA EN TU HTML ---
                
                # TÍTULO: div class="mc-title" -> a
                title_div = card.find('div', class_='mc-title')
                titulo = title_div.a.get_text(strip=True) if title_div else "Sin Título"
                
                # AÑO: span class="mc-year"
                year_span = card.find('span', class_='mc-year')
                anio = year_span.get_text(strip=True) if year_span else "-"
                
                # RATING: div class="avg" (dentro de fa-avg-rat-box)
                rat_div = card.find('div', class_='avg')
                rating = rat_div.get_text(strip=True) if rat_div else "N/A"
                
                # POSTER: img class="lazyload", atributo data-srcset
                img_tag = card.find('img')
                poster = None
                
                if img_tag:
                    # Tu HTML usa data-srcset="url 150w, url 300w, url 400w"
                    if 'data-srcset' in img_tag.attrs:
                        srcset = img_tag['data-srcset']
                        # Dividimos por comas para separar las versiones
                        urls = srcset.split(',')
                        # Tomamos la última (suele ser la más grande) o la segunda
                        # Limpiamos espacios y quitamos el indicador de tamaño " 300w"
                        # Ejemplo: " https://pics...mmed.jpg 300w" -> split(' ') -> ["", "https://...", "300w"]
                        
                        # Intentamos buscar la versión "mmed" o "large"
                        best_url = urls[-1].strip().split(' ')[0] # Coge la última (large)
                        
                        # Si prefieres la mediana (mmed) que indicaste:
                        for u in urls:
                            if "mmed.jpg" in u:
                                best_url = u.strip().split(' ')[0]
                                break
                                
                        poster = best_url
                        
                    elif 'src' in img_tag.attrs and "empty.gif" not in img_tag['src']:
                        poster = img_tag['src']

                registros.append({
                    "Título": titulo,
                    "Año": anio,
                    "Rating": rating,
                    "Poster": poster,
                    "Fuente": "FilmAffinity"
                })
            except Exception as e:
                # print(e) # Descomentar para depurar
                continue
                
        return pd.DataFrame(registros)

    except Exception as e:
        st.error(f"Error interno: {e}")
        return pd.DataFrame()

# ==========================================
# 🎨 INTERFAZ GRÁFICA
# ==========================================
st.title("🎬 Buscador Universal")

col1, col2 = st.columns([1, 3])
with col1:
    fuente = st.radio("Fuente:", ["OMDb API", "FilmAffinity"])
with col2:
    keyword = st.text_input("Película a buscar:", placeholder="Ej. Star Wars")

if st.button("🔍 Buscar", type="primary"):
    if not keyword:
        st.warning("Escribe algo primero.")
    else:
        df = pd.DataFrame()
        
        with st.spinner(f"Buscando en {fuente}..."):
            if fuente == "OMDb API":
                df = buscar_omdb(keyword)
            else:
                df = buscar_filmaffinity(keyword)
        
        if not df.empty:
            st.success(f"Encontrados {len(df)} resultados.")
            
            st.dataframe(
                df,
                column_config={
                    "Poster": st.column_config.ImageColumn("Póster", width="small"),
                    "Rating": st.column_config.TextColumn("Nota"),
                    "Año": st.column_config.TextColumn("Año"),
                },
                use_container_width=True,
                hide_index=True,
                column_order=("Poster", "Título", "Año", "Rating", "Fuente")
            )
        else:
            st.error("No se encontraron resultados o hubo un bloqueo.")