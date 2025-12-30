import subprocess
import time

def ejecutar_script(nombre_archivo):
    print(f"\n🚀 Ejecutando: {nombre_archivo}...")
    try:
        # Ejecuta el script y espera a que termine
        subprocess.run(["python", nombre_archivo], check=True)
        print(f"✅ {nombre_archivo} completado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar {nombre_archivo}: {e}")
        return False
    return True

def iniciar_pipeline():
    start_time = time.time()
    
    # El orden lógico de tu Pipeline de Datos
    scripts = [
        "fuente2.py",                  # 1. Crea la base de datos (OMDb)
        "fuente1_Scraping_Duro.py",     # 2. Busca plataformas (Scraping)
        "FuenteN3.py",                  # 3. Descarga datos financieros (Kaggle)
        "fuente4.py",                  # 4. Busca pósters y verifica streaming (TMDB)
        "integrador.py"                # 5. Une todo en el archivo final
    ]

    for script in scripts:
        if not ejecutar_script(script):
            print("\n🛑 El proceso se detuvo debido a un error.")
            return

    total_time = round((time.time() - start_time) / 60, 2)
    print(f"\n✨ PIPELINE COMPLETADO en {total_time} minutos.")
    print("🌐 Iniciando la aplicación web PopCornDB...")
    
    # Finalmente lanza la aplicación web
    ejecutar_script("app.py")

if __name__ == "__main__":
    iniciar_pipeline()