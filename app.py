import streamlit as st
import pandas as pd
import cloudscraper # Necesario: pip install cloudscraper
from bs4 import BeautifulSoup
import time
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador PRO", layout="wide")
API_KEY_OMDB = "69d810ef" 

# ==========================================
# 🧠 LÓGICA OMDb (Igual que antes)
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
# 🕷️ LÓGICA FILMAFFINITY (CORREGIDA)
# ==========================================
def buscar_filmaffinity(keyword):
    # CONFIGURACIÓN "ANTIBOT" AVANZADA
    # Simulamos ser un Chrome real en Windows para pasar el filtro
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    url_base = "https://www.filmaffinity.com/pe/search.php" # Usamos /pe/ ya que estás en Perú
    parametros = {'stext': keyword}
    
    status = st.empty()
    status.info(f"🕸️ Conectando a FilmAffinity (Modo Navegador Real)...")
    
    try:
        # Añadimos un pequeño tiempo de espera aleatorio para parecer humanos
        time.sleep(random.uniform(0.5, 1.5))
        
        response = scraper.get(url_base, params=parametros)
        
        # VERIFICACIÓN DE BLOQUEO
        if response.status_code == 403:
            status.error("⛔ FilmAffinity detectó el script y bloqueó la conexión (Error 403). Intenta de nuevo en unos minutos.")
            return pd.DataFrame()
            
        if response.status_code != 200:
            status.error(f"Error de conexión: {response.status_code}")
            return pd.DataFrame()

        # PARSEO (LECTURA) DEL HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        registros = []
        
        # Buscamos las tarjetas de resultados (Clase estándar 'se-it')
        resultados = soup.find_all('div', class_='se-it')
        
        # Si no hay lista, verificamos si redirigió a una película única
        if not resultados:
            if soup.find('h1', {'id': 'main-title'}):
                # Caso especial: Búsqueda exacta redirige a la ficha
                titulo = soup.find('h1', {'id': 'main-title'}).get_text(strip=True)
                registros.append({
                    "Fuente": "FilmAffinity",
                    "Título": titulo,
                    "Año": "Ficha Directa",
                    "Rating": "Ver Link",
                    "Poster": None
                })
                status.success("¡Redirección directa encontrada!")
                return pd.DataFrame(registros)
            else:
                status.warning(f"Conexión exitosa, pero no vi películas para '{keyword}'. (El HTML llegó vacío de resultados)")
                return pd.DataFrame()
        
        status.text(f"Procesando {len(resultados)} resultados...")
        
        for item in resultados[:10]: 
            try:
                # Título
                t_tag = item.find('div', class_='mc-title')
                titulo = t_tag.get_text(strip=True) if t_tag else "Sin título"
                
                # Año
                y_tag = item.find('div', class_='ye-w')
                anio = y_tag.get_text(strip=True) if y_tag else "-"
                
                # Poster
                img_tag = item.find('img')
                poster = img_tag['src'] if img_tag else None
                # A veces la imagen está en 'data-src' por carga diferida
                if img_tag and 'data-src' in img_tag.attrs:
                    poster = img_tag['data-src']

                # Rating
                r_tag = item.find('div', class_='avgrat-box')
                rating = r_tag.get_text(strip=True) if r_tag else "-"

                registros.append({
                    "Fuente": "FilmAffinity",
                    "Título": titulo,
                    "Año": anio,
                    "Rating": rating,
                    "Poster": poster
                })
            except Exception:
                continue

        status.empty()
        return pd.DataFrame(registros)

    except Exception as e:
        status.error(f"Error técnico: {e}")
        return pd.DataFrame()

# ==========================================
# INTERFAZ (Igual que antes)
# ==========================================
st.title("🎬 Buscador Universal")
fuente = st.sidebar.radio("Fuente:", ("OMDb API", "FilmAffinity"))
keyword = st.text_input("Película:")

if st.button("Buscar"):
    if fuente == "OMDb API":
        st.warning("Función OMDb no incluida en este bloque (usa tu código anterior)")
    else:
        df = buscar_filmaffinity(keyword)
        if not df.empty:
            st.dataframe(df, column_config={"Poster": st.column_config.ImageColumn("Póster")})
        else:
            st.error("Sin resultados.")