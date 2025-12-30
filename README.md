# Trabajo final de Lenguaje de Programación 2
> [!NOTE]
> Todo lo implementado se ha desarrollado respetando las directivas del archivo robots.txt y los términos de servicio de las fuentes consultadas. Se implementaron tiempos de espera (delays) entre peticiones para evitar la saturación de los servidores externos.

<p align="center">
    <img src="images/popcorndb_logo_dark.png#gh-dark-mode-only" width="380">
    <img src="images/popcorndb_logo_light.png#gh-light-mode-only" width="380">
</p>

----  
Este proyecto es un ecosistema de datos diseñado para centralizar información cinematográfica proveniente de múltiples orígenes, permitiendo analizar la rentabilidad y disponibilidad de películas en servicios de streaming. El sistema automatiza todo el proceso, desde la extracción masiva de datos hasta su visualización en una plataforma web interactiva.

El objetivo principal de este proyecto es consolidar datos de APIs, Web Scraping y Datasets estáticos para ofrecer una visión 360° de la industria del cine, enfocándose en la relación entre el éxito financiero y la presencia en plataformas digitales.

Para leer la documentación completa consulte la [Wiki](https://github.com/CafinHarly/lp2_trabajo_final/wiki)
Para la página web ingrese [aqui](https://lp2-trabajo-final-pagina-web.onrender.com/)
----

# Estructura del proyecto

El proyecto se divide en tres fases críticas:

## 1. Extracción de los datos

- **JustWatch** ([fuente1.py](fuente1_Scraping_Duro.py)) : Realiza una búsqueda automatizada en JustWatch para identificar en qué plataformas (Netflix, Amazon, etc.) está disponible cada título.
- **API OMDb** ([fuente2.py](fuente2.py)): Actúa como el punto de entrada, extrayendo metadatos básicos (títulos, años, calificaciones) para una selección inicial de películas.
- **Kaggle Dataset** ([fuente3.py](FuenteN3.py)) : Descarga y limpia un dataset masivo de metadatos históricos para obtener cifras precisas de presupuesto y recaudación.
- **API TMDB** ([fuente4.py](fuente4.py)) : Enriquece la base de datos obteniendo las URLs oficiales de los pósters y validando la disponibilidad de streaming específicamente para la región de Perú.

## 2. Integración y limpieza

- **Motor de integración** ([integrador.py](integrador.py)):Consolida la información de todas las fuentes anteriores mediante una "llave" de unión basada en títulos normalizados.
- **Tratamiento de datos** El sistema elimina duplicados, maneja valores nulos y prepara las métricas financieras para el análisis final.

## 3. Visualización web

- **Dashboard Interactivo** ([app.py](app.py)) : Una aplicación Flask que permite al usuario explorar el catálogo final.
- **Lógica de Rentabilidad** : La interfaz calcula automáticamente si una película fue un "Éxito" o "Fracaso" comparando sus ingresos contra su presupuesto.
- **Filtros inteligentes** : Permite realizar búsquedas por texto y filtrar por géneros cinematográficos en tiempo real.

## 4. Requisitos

- Python 3.x
- Librerias: `Pandas`, `Requests`, ``selenium``, ``flask``, ``beautifulsoup4`` y ``kagglehub``

## 5. Integrantes

| Nombre | Usuario de GitHub |
|--------|--------------------|
| Fabricio Barrientos | [@fabriciobarrientos26](https://github.com/fabriciobarrientos26) |
| Harley Puma | [@CafinHarly](https://github.com/CafinHarly) |
| Raul Anton | [@RaulAM22](https://github.com/RaulAM22) |
