import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.transfermarkt.es/martin-genskowski/leistungsdaten/spieler/1005971"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

def limpiar_numero(texto):
    if not texto or texto.strip() == '-' or texto.strip() == '':
        return "0"
    return re.sub(r'[^0-9]', '', texto)

try:
    print("Conectando con Transfermarkt...")
    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Extraer nombre de la Liga y Temporada
    # Buscamos el encabezado de la caja de rendimiento
    header_liga = soup.find('div', class_='box-headline')
    nombre_liga = "Competición"
    if header_liga:
        nombre_liga = header_liga.text.strip().split('\n')[0]

    # 2. Extraer "partidos posibles"
    # Este texto suele estar en un div pequeño arriba de la tabla
    partidos_posibles_text = "Datos no disponibles"
    info_div = soup.find('div', class_='large-8 columns')
    if info_div:
        footer_text = info_div.find('div', class_='table-footer')
        if not footer_text: # Si no está en el footer, buscar texto plano
             match = re.search(r'\d+ partidos posibles', soup.text)
             if match:
                 partidos_posibles_text = match.group(0)

    # 3. Extraer estadísticas de la tabla
    stats = {
        "liga": nombre_liga,
        "partidos_posibles": partidos_posibles_text,
        "partidos": "0", "goles": "0", "asistencias": "0",
        "amarillas": "0", "segundas_amarillas": "0", "rojas": "0",
        "cuota_xi": "0", "minutos_jugados": "0", "participaciones_gol": "0"
    }

    tabla = soup.find('table', class_='items')
    if tabla:
        tfoot = tabla.find('tfoot')
        if tfoot:
            columnas = tfoot.find_all('td')
            if len(columnas) >= 8:
                stats["partidos"] = limpiar_numero(columnas[2].text)
                stats["goles"] = limpiar_numero(columnas[3].text)
                stats["asistencias"] = limpiar_numero(columnas[4].text)
                stats["amarillas"] = limpiar_numero(columnas[5].text)
                stats["segundas_amarillas"] = limpiar_numero(columnas[6].text)
                stats["rojas"] = limpiar_numero(columnas[7].text)

    # Extraer porcentajes (Anillos)
    for caja in soup.find_all('div', class_='large-4'):
        texto_caja = caja.text.lower()
        num_span = caja.find('span')
        if num_span:
            numero = limpiar_numero(num_span.text)
            if 'cuota xi' in texto_caja: stats["cuota_xi"] = numero
            elif 'minutos' in texto_caja: stats["minutos_jugados"] = numero
            elif 'participaciones' in texto_caja: stats["participaciones_gol"] = numero

    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
    print("Archivo stats.json actualizado con éxito.")

except Exception as e:
    print(f"Error: {e}")