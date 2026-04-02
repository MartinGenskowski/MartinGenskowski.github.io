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

    # Diccionario base con valores por defecto
    stats = {
        "liga": "I Lyga", # Por defecto si no lo encuentra
        "partidos_posibles": "Datos no disponibles",
        "partidos": "0", "goles": "0", "asistencias": "0",
        "amarillas": "0", "segundas_amarillas": "0", "rojas": "0",
        "cuota_xi": "0", "minutos_jugados": "0", "participaciones_gol": "0"
    }

    # 1. Extraer nombre de la Liga (En Transfermarkt moderno suele estar en una etiqueta h2)
    header_liga = soup.find(['h2', 'div'], class_=re.compile(r'content-box-headline|box-headline'))
    if header_liga:
        # Tomamos el texto, le quitamos espacios extra y saltos de línea
        texto_liga = header_liga.text.strip().split('\n')[0]
        if texto_liga:
            stats["liga"] = texto_liga

    # Obtenemos todo el texto limpio de la página para buscar patrones con expresiones regulares (regex)
    texto_pagina = soup.get_text(separator=' ', strip=True).lower()

    # 2. Extraer "Partidos posibles"
    match_partidos = re.search(r'(\d+)\s*partidos posibles', texto_pagina)
    if match_partidos:
        stats["partidos_posibles"] = f"{match_partidos.group(1)} partidos posibles"

    # 3. Extraer estadísticas de las tarjetas (El NUEVO DISEÑO SVELTE de Transfermarkt)
    valores_stats = soup.find_all(class_=re.compile(r'tm-player-performance__stats-list-item-value'))
    
    # Transfermarkt siempre ordena estos 6 datos de izquierda a derecha
    if len(valores_stats) >= 6:
        stats["partidos"] = limpiar_numero(valores_stats[0].text)
        stats["goles"] = limpiar_numero(valores_stats[1].text)
        stats["asistencias"] = limpiar_numero(valores_stats[2].text)
        stats["amarillas"] = limpiar_numero(valores_stats[3].text)
        stats["segundas_amarillas"] = limpiar_numero(valores_stats[4].text)
        stats["rojas"] = limpiar_numero(valores_stats[5].text)

    # 4. Extraer porcentajes (Anillos)
    # Buscamos el número que está justo antes o después de la palabra clave en la web
    match_xi = re.search(r'cuota xi inicial\s*(\d+)', texto_pagina)
    if not match_xi: match_xi = re.search(r'(\d+)\s*%\s*cuota xi inicial', texto_pagina)
    if match_xi: stats["cuota_xi"] = match_xi.group(1)
        
    match_min = re.search(r'minutos jugados\s*(\d+)', texto_pagina)
    if not match_min: match_min = re.search(r'(\d+)\s*%\s*minutos jugados', texto_pagina)
    if match_min: stats["minutos_jugados"] = match_min.group(1)
        
    match_gol = re.search(r'participaciones de gol\s*(\d+)', texto_pagina)
    if not match_gol: match_gol = re.search(r'(\d+)\s*%\s*participaciones de gol', texto_pagina)
    if match_gol: stats["participaciones_gol"] = match_gol.group(1)

    print("Datos extraídos correctamente:", stats)

    # 5. Guardar el archivo JSON
    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
    print("Archivo stats.json actualizado con éxito.")

except Exception as e:
    print(f"Error crítico en el scraper: {e}")
    # Sistema a prueba de fallos: Si algo se rompe, crea un JSON con 0s para que la página de Martín no colapse
    stats_seguridad = {
        "liga": "Competición", "partidos_posibles": "Actualizando datos...",
        "partidos": "0", "goles": "0", "asistencias": "0",
        "amarillas": "0", "segundas_amarillas": "0", "rojas": "0",
        "cuota_xi": "0", "minutos_jugados": "0", "participaciones_gol": "0"
    }
    with open('stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats_seguridad, f, indent=4, ensure_ascii=False)