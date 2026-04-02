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
    
    # Valores por defecto
    stats = {
        "liga": "Competición",
        "partidos_posibles": "Datos no disponibles",
        "partidos": "0", "goles": "0", "asistencias": "0",
        "amarillas": "0", "segundas_amarillas": "0", "rojas": "0",
        "cuota_xi": "0", "minutos_jugados": "0", "participaciones_gol": "0"
    }

    # 1. Extraer nombre de la Liga (Usando el data-testid infalible)
    liga_element = soup.find('a', {'data-testid': 'performance-headline-link'})
    if liga_element:
        stats["liga"] = liga_element.text.strip()

    # 2. Partidos Posibles (Buscamos el patrón de texto en español)
    match = re.search(r'(\d+)\s*partidos posibles', soup.text, re.IGNORECASE)
    if match:
        stats["partidos_posibles"] = f"{match.group(1)} partidos posibles"

    # 3. Extraer estadísticas de las tarjetas (Goles, Asistencias, etc.)
    valores_stats = soup.find_all(class_=re.compile(r'tm-player-performance__stats-list-item-value'))
    if len(valores_stats) >= 6:
        stats["partidos"] = limpiar_numero(valores_stats[0].text)
        stats["goles"] = limpiar_numero(valores_stats[1].text)
        stats["asistencias"] = limpiar_numero(valores_stats[2].text)
        stats["amarillas"] = limpiar_numero(valores_stats[3].text)
        stats["segundas_amarillas"] = limpiar_numero(valores_stats[4].text)
        stats["rojas"] = limpiar_numero(valores_stats[5].text)

    # 4. Extraer porcentajes de los Anillos (Usando data-testid)
    gauges = soup.find_all('div', class_=re.compile(r'tm-player-performance__gauge'))
    for gauge in gauges:
        term_el = gauge.find('span', {'data-testid': 'gauge-term'})
        val_el = gauge.find('span', {'data-testid': 'gauge-percentage'})
        
        if term_el and val_el:
            texto_caja = term_el.text.lower()
            numero = limpiar_numero(val_el.text)
            
            if 'cuota xi' in texto_caja:
                stats["cuota_xi"] = numero
            elif 'minutos' in texto_caja:
                stats["minutos_jugados"] = numero
            elif 'participaciones' in texto_caja:
                stats["participaciones_gol"] = numero

    # Guardar archivo JSON
    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
    
    print("Éxito. Datos extraídos:")
    print(stats)

except Exception as e:
    print(f"Error crítico en el scraper: {e}")