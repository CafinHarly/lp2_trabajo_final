from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# USA EL ARCHIVO QUE TIENE LOS DATOS INTEGRADOS
DATASET_PATH = "datos_integrados_124.csv" 

def cargar_datos():
    if not os.path.exists(DATASET_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(DATASET_PATH)
        
        # --- PROTECCIÓN CONTRA EL ERROR DE POPULARITY ---
        if 'popularity' not in df.columns:
            df['popularity'] = 0  # Si no existe, la crea con valor 0 para no fallar
            
        # Aseguramos que rating_imdb y genero también existan
        if 'rating_imdb' not in df.columns:
            df['rating_imdb'] = 0
        if 'genero' not in df.columns:
            df['genero'] = "Unknown"

        df = df.fillna({
            "budget": 0, "revenue": 0, "rating_imdb": 0,
            "popularity": 0, "plataformas": "No disponible"
        })
        
        # Lógica de rentabilidad
        def calcular_estado(row):
            presupuesto = pd.to_numeric(row.get("budget", 0), errors='coerce') or 0
            ganancia = pd.to_numeric(row.get("revenue", 0), errors='coerce') or 0
            if presupuesto > 0 and ganancia > 0:
                return "Éxito ✅" if ganancia > presupuesto else "Fracaso ❌"
            return "Sin datos financieros ⚠️"
        
        df["estado_financiero"] = df.apply(calcular_estado, axis=1)
        return df
    except Exception as e:
        print(f"Error cargando CSV: {e}")
        return pd.DataFrame()

@app.route("/")
def index():
    df = cargar_datos()
    if df.empty:
        return "Error: No se pudo cargar el archivo CSV. Verifica el nombre en el repositorio."

    genero = request.args.get("genero", "").strip().lower()
    stats = {"total": 0, "promedio_rating": 0}

    if genero:
        # Filtrado por género
        df = df[df["genero"].str.lower().str.contains(genero, na=False)]
        
        # Ordenar (Ya no fallará por 'popularity')
        df = df.sort_values(by=["rating_imdb", "popularity"], ascending=False).head(10)
        
        if not df.empty:
            stats["total"] = len(df)
            stats["promedio_rating"] = round(df["rating_imdb"].mean(), 1)
    else:
        df = df.head(70)

    peliculas = df.to_dict(orient="records")
    return render_template("index.html", peliculas=peliculas, stats=stats, busqueda=genero)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
