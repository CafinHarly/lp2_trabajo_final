import pandas as pd

def limpiar_texto(texto):
    """Limpia títulos para maximizar coincidencias"""
    if pd.isna(texto): return ""
    texto = str(texto).lower()
    # Quitamos caracteres especiales comunes que arruinan el merge
    for char in [".", ":", ",", "-", "(", ")", "'"]:
        texto = texto.replace(char, "")
    return texto.strip()

def ejecutar_integracion_mejorada():
    print("--- 🛠️ INICIANDO INTEGRACIÓN MEJORADA (SIN CEROS INNECESARIOS) ---")

    # 1. Cargar fuentes
    df_f1_f2 = pd.read_csv("datos_integrados_f1_f2.csv")
    df_f3 = pd.read_csv("fuente_3_peliculas_limpio.csv")

    # 2. Pre-limpieza de llaves de unión
    df_f1_f2['key'] = df_f1_f2['titulo'].apply(limpiar_texto)
    df_f3['key'] = df_f3['title'].apply(limpiar_texto)

    # 3. Eliminar duplicados en la Fuente 3 para evitar filas extra
    df_f3 = df_f3.drop_duplicates(subset=['key'])

    # 4. Unión (Merge)
    # Solo traemos las columnas que realmente tienen datos útiles
    df_final = pd.merge(
        df_f1_f2, 
        df_f3[['key', 'budget', 'revenue', 'popularity']], 
        on='key', 
        how='left'
    )

    # 5. TRATAMIENTO DE DATOS VACÍOS (Aquí es donde evitamos el WTF)
    # En lugar de 0.0, si el presupuesto es 0, lo tratamos como "Dato no disponible"
    # para que no arruine tus gráficas de promedio.
    df_final.loc[df_final['budget'] == 0, 'budget'] = None
    df_final.loc[df_final['revenue'] == 0, 'revenue'] = None

    # Limpiamos la columna auxiliar
    df_final.drop(columns=['key'], inplace=True)

    # 6. GUARDAR
    df_final.to_csv("dataset_final_peliculas.csv", index=False)
    
    # Reporte de calidad para tu informe
    encontrados = df_final['budget'].notna().sum()
    print(f"📊 Calidad de integración: Se hallaron datos financieros para {encontrados} de {len(df_final)} películas.")
    print("✅ Archivo 'dataset_final_peliculas.csv' actualizado.")

if __name__ == "__main__":
    ejecutar_integracion_mejorada()