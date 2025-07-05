import os
import json
from datetime import datetime
import subprocess
import sys

try:
    print("📥 Descargando snapshot actual con guardar_stats.py...")
    subprocess.run(["python3", "guardar_stats.py"], check=True)
except Exception as e:
    print(f"❌ Error al ejecutar guardar_stats.py: {e}")
    exit(1)

from config.puntuacion import calcular_puntos

STATS_DIR = "stats"

# Asigna días según periodo textual
PERIODOS = {
    "diario": 1,
    "semanal": 7,
    "mensual": 30
}

def cargar_snapshots(n_dias=1):
    archivos = sorted([
        f for f in os.listdir(STATS_DIR)
        if f.endswith(".json")
    ])
    if len(archivos) < n_dias + 1:
        print(f"❌ Se requieren al menos {n_dias + 1} snapshots para calcular un periodo de {n_dias} días.")
        return None, None

    archivo_inicio = archivos[-(n_dias + 1)]
    archivo_fin = archivos[-1]

    with open(os.path.join(STATS_DIR, archivo_inicio), encoding="utf-8") as f1, \
         open(os.path.join(STATS_DIR, archivo_fin), encoding="utf-8") as f2:
        inicio = json.load(f1)
        fin = json.load(f2)

    return inicio, fin

if __name__ == "__main__":
    # Puedes pasar un argumento por línea de comandos, como: python main.py semanal
    periodo = sys.argv[1] if len(sys.argv) > 1 else "semanal"
    n_dias = PERIODOS.get(periodo, None)

    if n_dias is None:
        try:
            n_dias = int(periodo)
        except ValueError:
            print(f"❌ Periodo inválido: {periodo}")
            sys.exit(1)

    print(f"📦 Calculando ranking para los últimos {n_dias} días...")

    ayer, hoy = cargar_snapshots(n_dias=n_dias)
    if not ayer or not hoy:
        sys.exit(1)

    miembros_ayer = {m["name"]: m for m in ayer["members"]}
    miembros_hoy = {m["name"]: m for m in hoy["members"]}

    resultados = []

    for nombre, stats_hoy in miembros_hoy.items():
        stats_ayer = miembros_ayer.get(nombre)

        # Si el jugador es nuevo, lo tratamos como snapshot vacío anterior
        if stats_ayer is None:
            stats_ayer = {k: "0" for k in stats_hoy}

        partidos_hoy = int(stats_hoy.get("gamesPlayed", 0))
        partidos_ayer = int(stats_ayer.get("gamesPlayed", 0))
        if partidos_hoy <= partidos_ayer:
            continue  # no jugó durante el periodo

        pos = stats_hoy.get("favoritePosition", "unknown")
        res = calcular_puntos(nombre, pos, stats_hoy, stats_ayer)

        # ✅ Normalización por día
        res["puntos"] = round(res["puntos"] / n_dias, 2)
        resultados.append(res)

    ranking = sorted(resultados, key=lambda x: x["puntos"], reverse=True)
    hoy_fecha = datetime.today().strftime("%Y-%m-%d")

    print(f"\n📊 Ranking medio diario ({periodo}) hasta {hoy_fecha}:\n")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} → {r['puntos']} pts/día ({r['partidos']} partidos)")
        print(f"   🎯 {r['goles']} goles | 🔫 {r['acierto_tiro']}% tiro | 🎁 {r['asistencias']} asist.")
        print(f"   📈 Ratio pases: {r['ratio_pases']} por partido | ⚽ Ratio goleador: {r['ratio_goleador']}")
        print(f"   ✅ {r['pases']} pases / {r['pases_intentados']} intentos ({r['pase_exito']}%)")
        print(f"   🛡️ {r['entradas']} entradas ({r['entrada_exito']}%) | 🥇 {r['mvps']} MVPs | 🟥 {r['rojas']} rojas | ⭐ {r['valoracion_media']} valoración\n")
