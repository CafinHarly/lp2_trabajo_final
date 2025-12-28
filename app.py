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
    "Claro video": "https://upload.wikimedia.org/wikipedia/commons/4/43/Claro_video_logo.svg",
    "MovistarTV": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Movistar_Play_logo.png"
}
def procesar_plataformas(texto_plataformas):
    """
    Convierte 'Netflix, Amazon' en una lista de objetos con url de logo.
    """
    if pd.isna(texto_plataformas) or texto_plataformas == "No disponible":
        return []
    lista_resultado = []
    nombres = [p.strip() for p in str(texto_plataformas).split(",")]
    for nombre in nombres:
        logo = LOGOS_URL.get(nombre, "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Question_mark_%28black%29.svg/200px-Question_mark_%28black%29.svg.png")
        lista_resultado.append({"nombre": nombre, "logo": logo})
        
    return lista_resultado

def cargar_datos():
    if not os.path.exists(DATASET_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(DATASET_PATH)
        df = df.fillna({
            "budget": 0, "revenue": 0, "rating_imdb": 0,
            "plataformas": "No disponible",
            "poster_url": "https://via.placeholder.com/300x450?text=Sin+Poster"
        })
        def calcular_estado(row):
            if row["budget"] > 0 and row["revenue"] > 0:
                return "Éxito ✅" if row["revenue"] > row["budget"] else "Fracaso ❌"
            return "Sin datos financieros ⚠️"
        df["estado_financiero"] = df.apply(calcular_estado, axis=1)
        return df
    except:
        return pd.DataFrame()

@app.route("/")
def index():
    df = cargar_datos()
    genero = request.args.get("genero", "").strip().lower()
    stats = {"total": 0, "promedio_rating": 0}

    if genero:
        df = df[df["genero"].str.lower().str.contains(genero, na=False)]
        df = df.sort_values(by=["rating_imdb", "popularity"], ascending=False).head(10)
        if not df.empty:
            stats["total"] = len(df)
            stats["promedio_rating"] = round(df["rating_imdb"].mean(), 1)
    else:
        df = df.head(70)

    peliculas = df.to_dict(orient="records")

    # Agregamos la lista de objetos de plataformas
    for peli in peliculas:
        peli['obj_plataformas'] = procesar_plataformas(peli['plataformas'])
    return render_template("index.html", peliculas=peliculas, stats=stats, busqueda=genero)

# Inicio de la aplicación
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)