import requests
import json
import os
from datetime import datetime

CLUB_ID = "1005509"
PLATFORM = "common-gen5"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "accept": "application/json",
    "referer": "https://www.ea.com/"
}

def fetch_stats_globales():
    url = f"https://proclubs.ea.com/api/fc/members/stats?platform={PLATFORM}&clubId={CLUB_ID}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def guardar_stats_del_dia():
    fecha = datetime.today().strftime("%Y-%m-%d")
    os.makedirs("stats", exist_ok=True)
    datos = fetch_stats_globales()
    with open(f"stats/{fecha}.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)
    print(f"✅ Estadísticas globales guardadas en stats/{fecha}.json")

if __name__ == "__main__":
    guardar_stats_del_dia()
