import streamlit as st
import requests
import pandas as pd
import time

# --- CONFIGURACIÓN ---
API_KEY = "69d810ef"  # Nota: Idealmente esto no debe ser público, pero sirve para probar
BASE_URL = "https://www.omdbapi.com/"

# --- TÍTULO DE LA PÁGINA ---
st.set_page_config(page_title="Buscador de Películas", layout="wide")
st.title("🎬 Buscador de Películas (OMDb API)")
st.markdown("Escribe una palabra clave para buscar películas y ver sus detalles.")

# --- FUNCIONES (Lógica de tu amigo) ---
def buscar_peliculas(keyword, paginas=3):
    imdb_ids = []
    # Barra de progreso en la interfaz
    progress_bar = st.progress(0)
    
    for page in range(1, paginas + 1):
        params = {
            "s": keyword,
            "type": "movie",
            "page": page,
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data.get("Response") == "True":
            for item in data["Search"]:
                imdb_ids.append(item["imdbID"])
        else:
            break
        
        # Actualizar barra de progreso
        progress_bar.progress(page / paginas)
        time.sleep(0.5) # Reduje un poco el tiempo para que no sea tan lento

    progress_bar.empty() # Limpiar barra al terminar
    return list(set(imdb_ids)) 

def obtener_detalle_peliculas(imdb_ids):
    registros = []
    total = len(imdb_ids)
    
    if total == 0:
        return pd.DataFrame()

    status_text = st.empty() # Texto cambiante en pantalla
    
    for i, imdb_id in enumerate(imdb_ids):
        status_text.text(f"Descargando detalles: {i+1} de {total} películas...")
        
        params = {
            "i": imdb_id,
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data.get("Response") == "True":
            registros.append({
                "IMDb ID": data.get("imdbID"),
                "Título": data.get("Title"),
                "Año": data.get("Year"),
                "Género": data.get("Genre"),
                "Rating": data.get("imdbRating"),
                "Poster": data.get("Poster") # Agregué el póster para que se vea mejor
            })
        
        # time.sleep(0.2) # Opcional: Pausa pequeña para no saturar

    status_text.success("¡Datos descargados con éxito!")
    return pd.DataFrame(registros)

# --- INTERFAZ DE USUARIO ---

# 1. Input del usuario
keyword = st.text_input("Ingresa la palabra clave (ej. Love, Batman, Star):")

# 2. Botón de búsqueda
if st.button("Buscar Películas"):
    if keyword:
        with st.spinner('Buscando IDs de películas...'):
            ids = buscar_peliculas(keyword, paginas=2) # Puse 2 páginas para que sea rápido probar
        
        st.write(f"Se encontraron **{len(ids)}** películas. Obteniendo detalles...")
        
        df_api = obtener_detalle_peliculas(ids)

        if not df_api.empty:
            # MOSTRAR TABLA INTERACTIVA
            st.dataframe(
                df_api,
                column_config={
                    "Poster": st.column_config.ImageColumn("Póster"), # Muestra la imagen real
                },
                hide_index=True
            )
            
            # Opción para descargar los resultados
            csv = df_api.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar resultados como CSV",
                data=csv,
                file_name=f'peliculas_{keyword}.csv',
                mime='text/csv',
            )
        else:
            st.warning("No se encontraron resultados o hubo un error.")
    else:
        st.error("Por favor, escribe una palabra clave.")