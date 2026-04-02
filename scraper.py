import requests
from bs4 import BeautifulSoup
import json
import datetime

# 1. La URL del perfil de Transfermarkt (REEMPLAZA ESTO por la URL real de Martín)
URL = "https://www.transfermarkt.es/martin-genskowski/profil/spieler/1005971"

# 2. Engañamos a Transfermarkt para que crea que somos un navegador web normal
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    # 3. Descargamos la página
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # 4. Buscamos los datos en el HTML (¡ATENCIÓN! Estas clases de HTML pueden variar en Transfermarkt)
    # Ejemplo genérico buscando en la tabla de rendimiento:
    
    # Supongamos que buscamos el total de partidos jugados esta temporada
    # Vas a tener que inspeccionar la página de TM para encontrar la clase exacta
    partidos_element = soup.find('span', class_='info-table__content--bold') 
    partidos = partidos_element.text.strip() if partidos_element else "N/A"

    # 5. Preparamos el archivo JSON
    stats_data = {
        "partidos": partidos,
        "minutos": "Por definir", # Repite el proceso de búsqueda para los minutos
        "ultima_actualizacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # 6. Guardamos los datos en stats.json
    with open('stats.json', 'w') as f:
        json.dump(stats_data, f, indent=4)
        
    print("Estadísticas actualizadas con éxito.")

except Exception as e:
    print(f"Error al extraer datos: {e}")