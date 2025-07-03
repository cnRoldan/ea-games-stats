import json
import os
from datetime import datetime, timedelta

def calcular_mvp_diario(snapshot_anterior, snapshot_actual):
    puntos_por_jugador = []

    for actual in snapshot_actual["members"]:
        jugador = actual["name"]
        anterior = next((p for p in snapshot_anterior["members"] if p["name"] == jugador), None)
        if not anterior:
            continue  # Jugador nuevo

        dif = lambda campo: float(actual[campo]) - float(anterior.get(campo, 0))

        goles = dif("goals")
        asistencias = dif("assists")
        partidos = dif("gamesPlayed")
        pases = dif("passesMade")
        entradas = dif("tacklesMade")
        rojas = dif("redCards")
        valoracion = float(actual["ratingAve"])

        puntos = (
            goles * 4.0 +
            asistencias * 3.5 +
            pases * 0.01 +
            entradas * 0.4 +
            partidos * 0.5 +
            ((float(actual["winRate"]) - float(anterior["winRate"])) // 10) * 1 -
            rojas * 2.0 +
            valoracion * 2
        )

        puntos_por_jugador.append({
            "jugador": jugador,
            "puntos": round(puntos, 2),
            "goles": int(goles),
            "asistencias": int(asistencias),
            "partidos": int(partidos),
            "pases": int(pases),
            "entradas": int(entradas),
            "valoracion": valoracion,
            "rojas": int(rojas)
        })

    return sorted(puntos_por_jugador, key=lambda x: x["puntos"], reverse=True)

if __name__ == "__main__":
    hoy = datetime.today()
    ayer = hoy - timedelta(days=1)

    fecha_hoy = hoy.strftime("%Y-%m-%d")
    fecha_ayer = ayer.strftime("%Y-%m-%d")

    archivo_actual = f"stats/{fecha_hoy}.json"
    archivo_anterior = f"stats/{fecha_ayer}.json"

    if not os.path.exists(archivo_actual) or not os.path.exists(archivo_anterior):
        print(f"❌ No se encontraron los archivos:\n  {archivo_anterior}\n  {archivo_actual}")
        exit(1)

    with open(archivo_anterior, encoding="utf-8") as f1, open(archivo_actual, encoding="utf-8") as f2:
        anterior = json.load(f1)
        actual = json.load(f2)

    ranking = calcular_mvp_diario(anterior, actual)

    print(f"\n🏆 MVP Diario ({fecha_ayer} → {fecha_hoy}):")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} → {r['puntos']} pts")
        print(f"   🎯 {r['goles']} goles | 🎁 {r['asistencias']} asist. | 🧮 {r['partidos']} partidos")
        print(f"   ✅ {r['pases']} pases | 🛡️ {r['entradas']} entradas | ⭐ {r['valoracion']} valoración | 🟥 {r['rojas']} rojas")