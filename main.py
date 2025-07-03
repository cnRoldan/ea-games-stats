from utils import fetch_club_stats
import json
from datetime import datetime
import os

def guardar_datos_diarios():
    # Obtener fecha actual en formato YYYY-MM-DD
    fecha = datetime.today().strftime("%Y-%m-%d")
    directorio = "stats"
    os.makedirs(directorio, exist_ok=True)
    archivo = f"{directorio}/{fecha}.json"

    # Descargar y guardar
    data = fetch_club_stats(club_id=1005509)
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Datos guardados para el día {fecha} en: {archivo}")

if __name__ == "__main__":
    guardar_datos_diarios()
