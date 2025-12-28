import pandas as pd

def limpiar_texto(texto):
    """Limpia títulos para maximizar coincidencias"""
    if pd.isna(texto): return ""
    texto = str(texto).lower()
    for char in [".", ":", ",", "-", "(", ")", "'"]:
        texto = texto.replace(char, "")
    return texto.strip()

def ejecutar_integracion():
    print("--- Procesando integración final de fuentes ---")
    try:
    # 1. Cargar fuentes
        df_f1_f2_f4= pd.read_csv("datos_integrados_124.csv")
        df_f3 = pd.read_csv("fuente_3_peliculas_limpio.csv")
    except FileNotFoundError as e:
        print(f"[ERROR] No se encontró el archivo necesario: {e.filename}")
        return
    # 2. Pre-limpieza de llaves de unión
    df_f1_f2_f4['key'] = df_f1_f2_f4['titulo'].apply(limpiar_texto)
    df_f3['key'] = df_f3['title'].apply(limpiar_texto)

    # 3. Eliminar duplicados en la Fuente 3 para evitar filas extra
    df_f3 = df_f3.drop_duplicates(subset=['key'])

    # 4. Unión (Merge)
    df_final = pd.merge(
        df_f1_f2_f4, 
        df_f3[['key', 'budget', 'revenue']], 
        on='key', 
        how='left'
    )

    # 5. TRATAMIENTO DE DATOS VACÍOS (Aquí es donde evitamos el WTF)
    df_final.loc[df_final['budget'] == 0, 'budget'] = None
    df_final.loc[df_final['revenue'] == 0, 'revenue'] = None

    # Limpiamos la columna auxiliar
    df_final.drop(columns=['key'], inplace=True)

    # 6. GUARDAR
    nombresalida = "dataset_final_peliculas.csv"
    df_final.to_csv(nombresalida, index=False)

    # Reporte de calidad para tu informe
    encontrados = df_final['budget'].notna().sum()
    print(f"Integración completada para {encontrados} de {len(df_final)} películas.")
    print("Datos cruzados correctamente.")
    print(f"Archivo generado: {nombresalida}")    
if __name__ == "__main__":
    ejecutar_integracion()