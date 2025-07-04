import os
import json
from datetime import datetime, timedelta

STATS_DIR = "stats"

# Cargar snapshot global de una fecha

def cargar_stats(fecha):
    ruta = os.path.join(STATS_DIR, f"{fecha}.json")
    if not os.path.exists(ruta):
        print(f"❌ No existe el archivo: {ruta}")
        return None
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

# Calcular MVP mensual como diferencia entre snapshots

def calcular_mvp_mensual(antes, despues):
    resultados = []
    for actual in despues["members"]:
        nombre = actual["name"]
        anterior = next((x for x in antes["members"] if x["name"] == nombre), None)

        if not anterior:
            continue

        dif = lambda campo: float(actual[campo]) - float(anterior.get(campo, 0))

        goles = dif("goals")
        asistencias = dif("assists")
        partidos = dif("gamesPlayed")
        pases = dif("passesMade")
        entradas = dif("tacklesMade")
        rojas = dif("redCards")
        mvps = dif("manOfTheMatch")
        valoracion = float(actual["ratingAve"])

        if partidos == 0:
            continue

        puntos = (
            goles * 3.5 +
            asistencias * 4.0 +
            pases * 0.05 +
            entradas * 2.0 +
            partidos * 0.5 +
            mvps * 2.5 -
            rojas * 2.0 +
            valoracion * 0.5
        )

        resultados.append({
            "jugador": nombre,
            "puntos": round(puntos, 2),
            "goles": int(goles),
            "asistencias": int(asistencias),
            "partidos": int(partidos),
            "pases": int(pases),
            "entradas": int(entradas),
            "mvps": int(mvps),
            "rojas": int(rojas),
            "valoracion": valoracion
        })

    return sorted(resultados, key=lambda x: x["puntos"], reverse=True)

if __name__ == "__main__":
    hoy = datetime.today().date()
    hace_un_mes = hoy - timedelta(days=30)

    fecha_actual = hoy.strftime("%Y-%m-%d")
    fecha_pasada = hace_un_mes.strftime("%Y-%m-%d")

    snapshot_actual = cargar_stats(fecha_actual)
    snapshot_anterior = cargar_stats(fecha_pasada)

    if not snapshot_actual or not snapshot_anterior:
        exit()

    ranking = calcular_mvp_mensual(snapshot_anterior, snapshot_actual)

    print(f"\n🏆 MVP Mensual ({fecha_pasada} → {fecha_actual}):\n")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} → {r['puntos']} pts")
        print(f"   🎯 {r['goles']} goles | 🎁 {r['asistencias']} asist. | 🧮 {r['partidos']} partidos")
        print(f"   ✅ {r['pases']} pases | 🛡️ {r['entradas']} entradas | 🥇 {r['mvps']} MVPs | ⭐ {r['valoracion']} val. media | 🟥 {r['rojas']} rojas\n")
