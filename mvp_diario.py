import json
import os
from datetime import datetime, timedelta

def cargar_stats(fecha):
    archivo = f"stats/{fecha}.json"
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo: {archivo}")
        return None
    with open(archivo, encoding="utf-8") as f:
        return json.load(f)

def calcular_mvp(anterior, actual):
    puntos_por_jugador = []

    for jugador_actual in actual["members"]:
        nombre = jugador_actual["name"]
        jugador_anterior = next((p for p in anterior["members"] if p["name"] == nombre), None)

        if not jugador_anterior:
            jugador_anterior = {
                "goals": "0", "assists": "0", "gamesPlayed": "0",
                "passesMade": "0", "tacklesMade": "0", "redCards": "0",
                "winRate": "0", "passSuccessRate": "0", "tackleSuccessRate": "0", "manOfTheMatch": "0"
            }

        dif = lambda campo: float(jugador_actual[campo]) - float(jugador_anterior.get(campo, 0))

        goles = dif("goals")
        asistencias = dif("assists")
        partidos = dif("gamesPlayed")
        if partidos == 0:
            continue

        pases = dif("passesMade")
        entradas = dif("tacklesMade")
        rojas = dif("redCards")
        mvps = dif("manOfTheMatch")

        pase_exito = float(jugador_actual["passSuccessRate"])
        entrada_exito = float(jugador_actual["tackleSuccessRate"])

        # Cálculo de pases fallidos
        if pase_exito == 0:
            pases_fallidos = pases  # asumimos todos fallados
        else:
            pases_fallidos = pases * ((100 - pase_exito) / pase_exito)

        acierto_tiro = float(jugador_actual["shotSuccessRate"])
        bonus_tiro = 0
        if acierto_tiro >= 50:
            bonus_tiro = 3.0
        elif acierto_tiro >= 30:
            bonus_tiro = 1.5
        elif acierto_tiro < 15:
            bonus_tiro = -1.0

        bonus_pases = 1.0 if pase_exito >= 85 else 0
        bonus_entradas = 1.0 if entrada_exito >= 20 else 0

        puntos = (
                goles * 3.5 +
                asistencias * 4.0 +
                pases * 0.05 +
                entradas * 2.0 +
                partidos * 0.5 +
                bonus_pases +
                bonus_entradas +
                bonus_tiro +
                mvps * 2.5 -
                rojas * 2.0 -
                pases_fallidos * 0.8
        )

        puntos_por_jugador.append({
            "jugador": nombre,
            "puntos": round(puntos, 2),
            "goles": int(goles),
            "asistencias": int(asistencias),
            "partidos": int(partidos),
            "pases": int(pases),
            "acierto_tiro": round(acierto_tiro, 1),
            "pase_exito": round(pase_exito, 1),
            "fallidos": int(pases_fallidos),
            "entradas": int(entradas),
            "entrada_exito": round(entrada_exito, 1),
            "mvps": int(mvps),
            "rojas": int(rojas)
        })

    return sorted(puntos_por_jugador, key=lambda x: x["puntos"], reverse=True)

if __name__ == "__main__":
    hoy = datetime.today()
    ayer = hoy - timedelta(days=1)

    fecha_actual = hoy.strftime("%Y-%m-%d")
    fecha_anterior = ayer.strftime("%Y-%m-%d")

    actual = cargar_stats(fecha_actual)
    anterior = cargar_stats(fecha_anterior)

    if not anterior or not actual:
        exit()

    ranking = calcular_mvp(anterior, actual)

    print(f"\n🏆 MVP Diario ({fecha_anterior} → {fecha_actual}):\n")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} → {r['puntos']} pts")
        print(f"   🎯 {r['goles']} goles | 🔫 {r['acierto_tiro']}% acierto tiro | 🎁 {r['asistencias']} asist. | 🧮 {r['partidos']} partidos")
        print(f"   ✅ {r['pases']} pases ({r['pase_exito']}% éxito) | ❌ {r['fallidos']} fallidos")
        print(f"   🛡️ {r['entradas']} entradas ({r['entrada_exito']}% éxito) | 🥇 {r['mvps']} MVPs | 🟥 {r['rojas']} rojas\n")
