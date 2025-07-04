import os
import json
from datetime import datetime
from collections import defaultdict

MATCHES_DIR = "matches"
CLUB_ID = "1005509"

# Clasificación por posición

def clasificar_pos(pos):
    try:
        pos = int(pos)
        if pos == 1:
            return "portero"
        elif 2 <= pos <= 5:
            return "defensor"
        elif 6 <= pos <= 13:
            return "centrocampista"
        else:
            return "delantero"
    except ValueError:
        pos = pos.lower()
        if "keeper" in pos:
            return "portero"
        elif "defender" in pos:
            return "defensor"
        elif "midfield" in pos:
            return "centrocampista"
        elif "forward" in pos:
            return "delantero"
        else:
            return "desconocido"

# Cargar todos los partidos

def cargar_partidos():
    partidos = []
    if not os.path.exists(MATCHES_DIR):
        return partidos
    for archivo in sorted(os.listdir(MATCHES_DIR)):
        if archivo.endswith(".json"):
            ruta = os.path.join(MATCHES_DIR, archivo)
            with open(ruta, encoding="utf-8") as f:
                try:
                    datos = json.load(f)
                    if isinstance(datos, list):
                        partidos.extend(datos)
                except Exception as e:
                    print(f"❌ Error leyendo {archivo}: {e}")
    return partidos

# Cálculo de puntuación por jugador

def calcular_puntos(jugador, pos, partidos):
    total = defaultdict(float)
    for p in partidos:
        for key in ["goals", "assists", "passesmade", "passattempts", "shots",
                    "tacklesmade", "tackleattempts", "redcards", "mom", "rating"]:
            total[key] += float(p.get(key, 0))
    partidos_jugados = len(partidos)

    pase_exito = (total["passesmade"] / total["passattempts"] * 100) if total["passattempts"] else 0
    entrada_exito = (total["tacklesmade"] / total["tackleattempts"] * 100) if total["tackleattempts"] else 0
    tiro_exito = (total["goals"] / total["shots"] * 100) if total["shots"] else 0
    pases_fallidos = total["passattempts"] - total["passesmade"]

    bonus_pases = 1.0 if pase_exito >= 85 else 0
    bonus_entradas = 1.0 if entrada_exito >= 20 else 0
    bonus_tiros = 0
    if tiro_exito >= 50:
        bonus_tiros = 3.0
    elif tiro_exito >= 30:
        bonus_tiros = 1.5
    elif tiro_exito < 15 and total["shots"] > 0:
        bonus_tiros = -1.0

    penalizacion_fallos = {
        "portero": 0.2,
        "defensor": 0.4,
        "centrocampista": 0.6,
        "delantero": 0.8
    }

    puntos = (
        total["goals"] * 3.5 +
        total["assists"] * 4.0 +
        total["passesmade"] * 0.05 +
        total["tacklesmade"] * 2.0 +
        partidos_jugados * 0.5 +
        bonus_pases +
        bonus_entradas +
        bonus_tiros +
        total["mom"] * 2.5 -
        total["redcards"] * 2.0 -
        pases_fallidos * penalizacion_fallos[pos]
    )

    if partidos_jugados > 1:
        puntos += (partidos_jugados - 1) * 0.5

    return {
        "jugador": jugador,
        "posicion": pos,
        "puntos": round(puntos, 2),
        "partidos": partidos_jugados,
        "goles": int(total["goals"]),
        "asistencias": int(total["assists"]),
        "pases": int(total["passesmade"]),
        "pase_exito": round(pase_exito, 1),
        "tiros": int(total["shots"]),
        "acierto_tiro": round(tiro_exito, 1),
        "entradas": int(total["tacklesmade"]),
        "entrada_exito": round(entrada_exito, 1),
        "mvps": int(total["mom"]),
        "rojas": int(total["redcards"]),
        "valoracion_media": round(total["rating"] / partidos_jugados, 2) if partidos_jugados else 0
    }

if __name__ == "__main__":
    print("📦 Cargando todos los partidos guardados...")
    partidos = cargar_partidos()
    if not partidos:
        print("⚠️ No se encontraron partidos.")
        exit()

    acumulado = defaultdict(list)
    for partido in partidos:
        jugadores = partido.get("players", {}).get(CLUB_ID, {})
        for _, datos in jugadores.items():
            nombre = datos.get("playername")
            if nombre:
                acumulado[nombre].append(datos)

    resultados = []
    for nombre, lista in acumulado.items():
        pos = clasificar_pos(lista[0].get("pos"))
        resultados.append(calcular_puntos(nombre, pos, lista))

    ranking = sorted(resultados, key=lambda x: x["puntos"], reverse=True)

    hoy = datetime.today().strftime("%Y-%m-%d")
    print(f"\n📊 Ranking Histórico Acumulado (hasta {hoy}):\n")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} → {r['puntos']} pts ({r['partidos']} partidos)")
        print(f"   🎯 {r['goles']} goles | 🔫 {r['acierto_tiro']}% tiro | 🎁 {r['asistencias']} asist.")
        print(f"   ✅ {r['pases']} pases ({r['pase_exito']}%) | 🛡️ {r['entradas']} entradas ({r['entrada_exito']}%)")
        print(f"   🥇 {r['mvps']} MVPs | 🟥 {r['rojas']} rojas | ⭐ {r['valoracion_media']} valoración media\n")
