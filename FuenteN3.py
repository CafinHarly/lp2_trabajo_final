import kagglehub
import pandas as pd
import os

def preparar_fuente_3():
    print("--- Iniciando Proceso de Fuente 3 (Archivo Estático) ---")

    # 1. Descargar el dataset (esto detecta si ya existe para no repetir)
    # Se descarga en una carpeta oculta de tu usuario (cache)
    try:
        path = kagglehub.dataset_download("rounakbanik/the-movies-dataset")
        print(f"Dataset localizado en: {path}")
    except Exception as e:
        print(f"Error al descargar: {e}")
        return

    # 2. Definir el archivo específico que queremos (el de metadatos)
    archivo_origen = os.path.join(path, "movies_metadata.csv")
    
    # 3. Leer los datos con Pandas
    # low_memory=False evita advertencias por columnas con datos mixtos
    print("Leyendo archivo original...")
    df = pd.read_csv(archivo_origen, low_memory=False)

    # 4. Seleccionar solo las columnas interesantes para tu análisis
    # Esto hace que tu Fuente 3 sea más limpia y profesional
    columnas_seleccionadas = [
        'id', 'title', 'budget', 'revenue', 
        'release_date', 'vote_average', 'vote_count', 'popularity'
    ]
    
    # Filtramos el dataframe
    df_final = df[columnas_seleccionadas].copy()

    # 5. Limpieza básica: Eliminar filas sin título o sin fecha
    df_final.dropna(subset=['title', 'release_date'], inplace=True)

    # 6. GENERAR EL CSV PARA TU ANÁLISIS
    # Este es el archivo que entregarás o procesarás después
    nombre_salida = "fuente_3_peliculas_limpio.csv"
    df_final.to_csv(nombre_salida, index=False, encoding='utf-8')
    
    print(f"\n¡Éxito! Se ha generado el archivo: {os.path.abspath(nombre_salida)}")
    print(f"Total de registros procesados: {len(df_final)}")
    print("\nPrimeras 5 filas del nuevo archivo:")
    print(df_final.head())

if __name__ == "__main__":
    preparar_fuente_3()