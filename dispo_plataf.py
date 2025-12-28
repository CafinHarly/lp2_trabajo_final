import requests

# Configuración
API_KEY = '503dbd676ae9d8d8fa1b4bff4628ac7c'
BASE_URL = 'https://api.themoviedb.org/3'
PAIS = 'PE'

def consultar_peliculas():
    # Obtener peliculas populares
    url_populares = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-MX&page=1"
    res = requests.get(url_populares)
    
    if res.status_code != 200:
        print("Error de conexión.")
        return

    peliculas = res.json()['results']

    # Iterar y buscar proveedores
    for peli in peliculas:
        movie_id = peli['id']
        titulo = peli['title']
        
        url_prov = f"{BASE_URL}/movie/{movie_id}/watch/providers?api_key={API_KEY}"
        res_prov = requests.get(url_prov)
        data_prov = res_prov.json()
        
        plataformas = "No disponible en streaming"
        
        if 'results' in data_prov and PAIS in data_prov['results']:
            flatrate = data_prov['results'][PAIS].get('flatrate')
            if flatrate:
                nombres = [p['provider_name'] for p in flatrate]
                plataformas = ", ".join(nombres)
        
        print(f"{titulo} | {plataformas}")

if __name__ == "__main__":
    consultar_peliculas()