import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def configurar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # User-agent real para evitar bloqueos
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # Elimina la huella de 'navigator.webdriver'
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrapear_plataformas(driver, titulo):
    url = f"https://www.justwatch.com/pe/buscar?q={titulo.replace(' ', '%20')}"
    try:
        driver.get(url)
        time.sleep(4) # Espera crucial para que carguen los logos

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Buscamos la primera tarjeta de película
        item = soup.find("div", class_="title-list-grid__item")
        if not item:
            return "No encontrada"

        # Buscamos las imágenes de los proveedores (plataformas)
        # JustWatch usa el atributo 'alt' en las imágenes para el nombre de la plataforma
        imagenes = item.select("picture img")
        
        plataformas = []
        for img in imagenes:
            nombre = img.get("alt")
            # Filtramos para que solo guarde nombres de plataformas reales
            if nombre and nombre not in ["Poster", "Logo", titulo]:
                plataformas.append(nombre)

        # Limpiar duplicados
        res = ", ".join(sorted(list(set(plataformas))))
        return res if res else "Solo Alquiler/Compra"
    except:
        return "Error en conexión"

# --- EJECUCIÓN PARA 70 TÍTULOS ---
if __name__ == "__main__":
    print("🎬 Iniciando Scraping de 70 títulos...")
    
    # Cargar los 70 de la Fuente 2
    df = pd.read_csv("datos_peliculas_generales_omdb.csv").head(70)
    
    driver = configurar_driver()
    resultados = []

    for i, fila in df.iterrows():
        print(f"🔍 [{i+1}/70] Analizando: {fila['titulo']}")
        plataformas = scrapear_plataformas(driver, fila['titulo'])
        resultados.append(plataformas)
        time.sleep(1) # Pausa de cortesía

    driver.quit()

    # Guardar integración Fuente 1 + Fuente 2
    df.to_csv("datos_integrados_f1_f2.csv", index=False)
    print("\n✅ Archivo 'datos_integrados_f1_f2.csv' generado con éxito.")