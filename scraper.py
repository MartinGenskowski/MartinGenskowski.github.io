import cloudscraper
from bs4 import BeautifulSoup
import json
import re

URL = "https://www.transfermarkt.es/martin-genskowski/leistungsdaten/spieler/1005971"

try:
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    response = scraper.get(URL, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscamos los valores con la clase svelte que encontraste
    valores = soup.find_all(class_=re.compile(r'tm-player-performance__stats-list-item-value'))
    
    if valores:
        # El primer valor siempre es "Partidos"
        partidos_web = valores[0].text.strip()
        
        # Guardamos solo ese dato en el JSON
        with open('stats.json', 'w') as f:
            json.dump({"partidos": partidos_web}, f)
        print(f"Partidos actualizados: {partidos_web}")

except Exception as e:
    print(f"Error: {e}")