from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

DATASET_PATH = "dataset_final_peliculas.csv"

LOGOS_URL = {
    "Netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Amazon Prime Video": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png",
    "Disney Plus": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
    "Max": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Max_logo.svg",
    "HBO Max": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Max_logo.svg",
    "Apple TV Plus": "https://upload.wikimedia.org/wikipedia/commons/2/28/Apple_TV_Plus_Logo.svg",
    "Star Plus": "https://upload.wikimedia.org/wikipedia/commons/7/71/Star%2B_logo.svg",
    "Paramount Plus": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Paramount_Plus.svg",
    "Claro video": "https://iconlogovector.com/uploads/images/2024/09/lg-66dc4e9a0be2b-Claro-video.webp",
    "MovistarTV": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Movistar_Play_logo.png",
    "Movistar Play": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Movistar_Play_logo.png",
    "Google Play Movies": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Google_Play_Movies_%26_TV_logo.svg",
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    "DIRECTV GO" : "https://logodownload.org/wp-content/uploads/2021/04/dgo-logo-0.png"
}
def procesar_plataformas(texto_plataformas):
    """
    Convierte 'Netflix, Amazon' en una lista de objetos con url de logo.
    """
    # Si es nulo o dice "No disponible", devolvemos lista vacía
    if pd.isna(texto_plataformas) or str(texto_plataformas).strip() in ["No disponible", ""]:
        return []
        
    lista_resultado = []
    nombres = [p.strip() for p in str(texto_plataformas).split(",")]
    
    for nombre in nombres:
        # BUSCAMOS SOLO SI EXISTE EN EL DICCIONARIO
        if nombre in LOGOS_URL:
            lista_resultado.append({
                "nombre": nombre, 
                "logo": LOGOS_URL[nombre]
            })
        # Si no está en el diccionario, no hacemos nada (evitamos el signo de ?)
            
    return lista_resultado

def cargar_datos():
    if not os.path.exists(DATASET_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(DATASET_PATH)
        
        # 1. FORZAMOS QUE LOS DATOS SEAN NÚMEROS (Esto arregla la rentabilidad vacía)
        df["budget"] = pd.to_numeric(df["budget"], errors='coerce').fillna(0)
        df["revenue"] = pd.to_numeric(df["revenue"], errors='coerce').fillna(0)
        df["rating_imdb"] = pd.to_numeric(df["rating_imdb"], errors='coerce').fillna(0)
        df["plataformas"] = df["plataformas"].fillna("No disponible")
        df["poster_url"] = df["poster_url"].fillna("https://via.placeholder.com/300x450?text=Sin+Poster")

        def calcular_estado(row):
            presupuesto = row["budget"]
            ganancia = row["revenue"]
            diferencia = ganancia - presupuesto
            
            def formato_moneda(valor):
                return "${:,.0f}".format(valor)

            if presupuesto > 0 and ganancia > 0:
                if diferencia > 0:
                    return {
                        "texto": "Éxito 💰", 
                        "clase": "exito", 
                        "monto": f"+ {formato_moneda(diferencia)}" 
                    }
                else:
                    return {
                        "texto": "Fracaso 📉", 
                        "clase": "fracaso", 
                        "monto": f"{formato_moneda(diferencia)}" 
                    }
            return {"texto": "Sin datos ⚠️", "clase": "neutro", "monto": ""}
        
        # Aplicamos la lógica
        estados = df.apply(calcular_estado, axis=1)
        df["estado_texto"] = estados.apply(lambda x: x["texto"])
        df["estado_clase"] = estados.apply(lambda x: x["clase"])
        df["estado_monto"] = estados.apply(lambda x: x["monto"]) 

        return df
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return pd.DataFrame()
def obtener_generos_unicos(df):
    """Extrae todos los géneros únicos del dataset para el menú."""
    generos = set()
    if "genero" in df.columns:
        for item in df["genero"].dropna().astype(str):
            # Separa por comas: "Action, Adventure" -> ["Action", "Adventure"]
            partes = [g.strip() for g in item.split(",")]
            generos.update(partes)
    return sorted(list(generos))   

@app.route("/")
def index():
    df = cargar_datos()
    # Obtenemos la lista de géneros para el menú
    lista_generos = obtener_generos_unicos(df)

    # Obtenemos los filtros del usuario
    busqueda_texto = request.args.get("q", "").strip().lower() # Input de texto
    filtro_genero = request.args.get("filtro_genero", "").strip() # Dropdown

    stats = {"total": 0, "promedio_rating": 0}

    if not df.empty:
        if filtro_genero:
            df = df[df["genero"].astype(str).str.contains(filtro_genero, na=False)]

        if busqueda_texto:
            mask_genero = df["genero"].astype(str).str.lower().str.contains(busqueda_texto, na=False)
            mask_titulo = df["titulo"].astype(str).str.lower().str.contains(busqueda_texto, na=False)
            df = df[mask_genero | mask_titulo]
        
        df = df.sort_values(by="rating_imdb", ascending=False)
        
        stats["total"] = len(df)
        stats["promedio_rating"] = round(df["rating_imdb"].mean(), 1)
        
        limit = 20 if (busqueda_texto or filtro_genero) else 70
        df = df.head(limit)

    peliculas = df.to_dict(orient="records")

    # Agregamos la lista de objetos de plataformas
    for peli in peliculas:
        peli['obj_plataformas'] = procesar_plataformas(peli['plataformas'])
    return render_template("index.html", peliculas=peliculas, stats=stats, busqueda=busqueda_texto, filtro_actual=filtro_genero, lista_generos=lista_generos)

# Inicio de la aplicación
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)