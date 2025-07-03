import requests
import json
from datetime import datetime
from collections import defaultdict

CLUB_ID = "1005509"
PLATFORM = "common-gen5"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "accept": "application/json",
    "referer": "https://www.ea.com/"
}

# Clasificación de posición
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
        # Si pos es texto (ej. 'midfielder')
        if "keeper" in pos.lower():
            return "portero"
        elif "defender" in pos.lower():
            return "defensor"
        elif "midfield" in pos.lower():
            return "centrocampista"
        elif "forward" in pos.lower():
            return "delantero"
        else:
            return "desconocido"

def obtener_partidos_hoy():
    url = f"https://proclubs.ea.com/api/fc/clubs/matches?matchType=leagueMatch&platform={PLATFORM}&clubIds={CLUB_ID}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    partidos = response.json()
    hoy = datetime.today().date()
    return [p for p in partidos if datetime.fromtimestamp(p["timestamp"]).date() == hoy]

def obtener_estadisticas_globales():
    url = f"https://proclubs.ea.com/api/fc/members/stats?platform={PLATFORM}&clubId={CLUB_ID}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return {j["name"]: j for j in data["members"]}

def calcular_puntos(jugador, pos, partidos):
    # Suma todas las estadísticas
    total = defaultdict(float)
    for p in partidos:
        for key in ["goals", "assists", "passesmade", "passattempts", "shots",
                    "tacklesmade", "tackleattempts", "redcards", "mom", "rating"]:
            total[key] += float(p.get(key, 0))
    partidos_jugados = len(partidos)

    # Evitar división por cero
    pase_exito = (total["passesmade"] / total["passattempts"] * 100) if total["passattempts"] else 0
    entrada_exito = (total["tacklesmade"] / total["tackleattempts"] * 100) if total["tackleattempts"] else 0
    tiro_exito = (total["goals"] / total["shots"] * 100) if total["shots"] else 0
    pases_fallidos = int(total["passattempts"] - total["passesmade"])

    # Bonos
    bonus_pases = 1.0 if pase_exito >= 85 else 0
    bonus_entradas = 1.0 if entrada_exito >= 20 else 0
    bonus_tiros = 0
    if tiro_exito >= 50:
        bonus_tiros = 3.0
    elif tiro_exito >= 30:
        bonus_tiros = 1.5
    elif tiro_exito < 15 and total["shots"] > 0:
        bonus_tiros = -1.0

    # Penalizaciones por posición
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

    # Bonus progresivo por partidos > 1
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
        "pases_fallidos": pases_fallidos,
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
    print("📦 Cargando partidos de hoy...")
    partidos = obtener_partidos_hoy()
    if not partidos:
        print("⚠️ No se han jugado partidos hoy.")
        exit()

    globales = obtener_estadisticas_globales()
    acumulado = defaultdict(list)

    for partido in partidos:
        jugadores = partido["players"].get(CLUB_ID, {})
        for _, datos in jugadores.items():
            nombre = datos["playername"]
            acumulado[nombre].append(datos)

    resultados = []
    for nombre, lista in acumulado.items():
        pos = clasificar_pos(lista[0]["pos"])
        resultados.append(calcular_puntos(nombre, pos, lista))

    ranking = sorted(resultados, key=lambda x: x["puntos"], reverse=True)

    hoy = datetime.today().strftime("%Y-%m-%d")
    print(f"\n🏆 Ranking Acumulado Diario ({hoy}):\n")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} → {r['puntos']} pts ({r['partidos']} partidos)")
        print(f"   🎯 {r['goles']} goles | 🔫 {r['acierto_tiro']}% tiro | 🎁 {r['asistencias']} asist.")
        print(f"   ✅ {r['pases']} pases ({r['pase_exito']}% éxito) | ❌ {r['pases_fallidos']} fallidos")
        print(f"   🛡️ {r['entradas']} entradas ({r['entrada_exito']}%)")
        print(f"   🥇 {r['mvps']} MVPs | 🟥 {r['rojas']} rojas | ⭐ {r['valoracion_media']} valoración media\n")
