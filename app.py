from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Configuración del dataset
DATASET_PATH = "dataset_final_peliculas.csv"

def cargar_datos():
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Error: No se encontró {DATASET_PATH}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(DATASET_PATH)
        # Limpieza y normalización de datos
        df = df.fillna({
            "budget": 0, 
            "revenue": 0, 
            "rating_imdb": 0,
            "popularity": 0, 
            "streaming_disponible": "No disponible"
        })
        
        # Lógica de Negocio: Estado Financiero
        def calcular_estado(row):
            if row["budget"] > 0 and row["revenue"] > 0:
                return "Éxito ✅" if row["revenue"] > row["budget"] else "Fracaso ❌"
            return "Sin datos financieros ⚠️"
        
        df["estado_financiero"] = df.apply(calcular_estado, axis=1)
        return df
    except Exception as e:
        print(f"❌ Error al procesar el CSV: {e}")
        return pd.DataFrame()

@app.route("/")
def index():
    df = cargar_datos()
    if df.empty:
        return "Error: No hay datos disponibles. Revisa el archivo CSV."

    # Capturar filtros de búsqueda
    genero = request.args.get("genero", "").strip().lower()
    
    stats = {"total": 0, "promedio_rating": 0}

    if genero:
        # 1. Filtrar por género
        df = df[df["genero"].str.lower().str.contains(genero, na=False)]
        
        # 2. Ordenar por los mejores puntuados (Top 10)
        df = df.sort_values(by=["rating_imdb", "popularity"], ascending=False).head(10)
        
        # 3. Calcular estadísticas en tiempo real
        if not df.empty:
            stats["total"] = len(df)
            stats["promedio_rating"] = round(df["rating_imdb"].mean(), 1)
    else:
        # Si no hay búsqueda, mostramos las primeras 70
        df = df.head(70)

    peliculas = df.to_dict(orient="records")
    return render_template("index.html", peliculas=peliculas, stats=stats, busqueda=genero)

if __name__ == "__main__":
    app.run(debug=True)