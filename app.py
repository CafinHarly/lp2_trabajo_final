import streamlit as st
import requests
import pandas as pd
import cloudscraper  # Importante para saltar el bloqueo 403
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Buscador de Películas Pro", layout="wide", page_icon="🎬")

# --- CONSTANTES ---
API_KEY_OMDB = "69d810ef" 

# ==========================================
# 🧠 LÓGICA 1: OMDb API (Oficial y Rápido)
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
# 🕷️ LÓGICA 2: FilmAffinity (Web Scraping Anti-Bloqueo)
# ==========================================
def buscar_filmaffinity(keyword):
    # 1. Crear el scraper que simula ser un navegador real
    scraper = cloudscraper.create_scraper() 
    
    url_base = "https://www.filmaffinity.com/es/search.php"
    parametros = {'stext': keyword}
    
    status = st.empty()
    status.info(f"🕸️ Conectando con FilmAffinity (Modo Stealth)...")
    
    try:
        # Usamos scraper.get en lugar de requests.get para evitar el error 403
        response = scraper.get(url_base, params=parametros)
        
        if response.status_code != 200:
            status.error(f"Error: El servidor devolvió código {response.status_code}")
            return pd.DataFrame()

        # 2. Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        registros = []
        
        # Buscamos las tarjetas de resultados (clase 'se-it')
        resultados = soup.find_all('div', class_='se-it')
        
        if not resultados:
            # Caso especial: A veces redirige directo a la película si el nombre es exacto
            if soup.find('h1', {'id': 'main-title'}):
                status.warning("⚠️ FilmAffinity redirigió a una ficha única (lógica pendiente). Intenta una búsqueda más general.")
            else:
                status.warning("No se encontraron resultados en FilmAffinity.")
            return pd.DataFrame()
        
        status.text(f"Procesando {len(resultados)} resultados encontrados...")
        
        # Limitamos a 10 resultados para no hacer esperar al usuario
        for item in resultados[:10]: 
            try:
                # Extracción segura de datos
                titulo = item.find('div', class_='mc-title').get_text(strip=True)
                
                anio_tag = item.find('div', class_='ye-w')
                anio = anio_tag.get_text(strip=True) if anio_tag else "-"
                
                img_tag = item.find('img')
                poster_url = img_tag['src'] if img_tag else None
                
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

        status.empty()
        return pd.DataFrame(registros)

    except Exception as e:
        status.error(f"Error grave en el scraping: {e}")
        return pd.DataFrame()

# ==========================================
# 🎨 INTERFAZ GRÁFICA (FRONTEND)
# ==========================================

st.title("🎬 Buscador Universal de Películas")
st.markdown("Compara resultados entre la API oficial y Web Scraping en vivo.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    fuente = st.radio(
        "📍 Fuente de datos:",
        ("OMDb API (Oficial)", "FilmAffinity (Scraping)")
    )
    st.info("Nota: FilmAffinity usa `cloudscraper` para evadir bloqueos 403.")

# --- ZONA DE BÚSQUEDA ---
col1, col2 = st.columns([3, 1])
with col1:
    keyword = st.text_input("Nombre de la película:", placeholder="Ej. Avengers, Titanic, Matrix...")
with col2:
    st.write("") # Espacio para alinear
    st.write("") 
    buscar_btn = st.button("🔍 Buscar", use_container_width=True)

# --- EJECUCIÓN ---
if buscar_btn:
    if not keyword:
        st.toast("⚠️ Por favor escribe el nombre de una película.")
    else:
        df_resultados = pd.DataFrame()
        
        if "OMDb" in fuente:
            df_resultados = buscar_omdb(keyword)
        else:
            df_resultados = buscar_filmaffinity(keyword)

        # MOSTRAR RESULTADOS
        if not df_resultados.empty:
            st.success(f"✅ Se encontraron **{len(df_resultados)}** películas en {fuente}")
            
            st.dataframe(
                df_resultados,
                column_config={
                    "Poster": st.column_config.ImageColumn("Póster", width="small"),
                    "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Botón de descarga
            csv = df_resultados.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f'resultados_{fuente}_{keyword}.csv',
                mime='text/csv',
            )
        else:
            st.error("No se encontraron resultados o hubo un error de conexión.")