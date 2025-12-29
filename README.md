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

----

# Estructura del proyecto

El proyecto se divide en tres fases críticas:

## Extracción de los datos

- **JustWatch** ([fuente1.py](fuente1_Scraping_Duro.py)) : Realiza una búsqueda automatizada en JustWatch para identificar en qué plataformas (Netflix, Amazon, etc.) está disponible cada título.
- **API OMDb** ([fuente2.py](fuente2.py)): Actúa como el punto de entrada, extrayendo metadatos básicos (títulos, años, calificaciones) para una selección inicial de películas.
- **Kaggle Dataset** ([fuente3.py](FuenteN3.py)) : Descarga y limpia un dataset masivo de metadatos históricos para obtener cifras precisas de presupuesto y recaudación.
- **API TMDB** ([fuente4.py](fuente4.py)) : Enriquece la base de datos obteniendo las URLs oficiales de los pósters y validando la disponibilidad de streaming específicamente para la región de Perú.

## Integración y limpieza

- **Motor de integración** ([integrador.py](integrador.py) :