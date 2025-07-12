import os
import json
from datetime import datetime
import subprocess
import sys
from statistics import mean
from config.puntuacion import calcular_puntos

STATS_DIR = "stats"

PERIODOS = {
    "diario": 1,
    "semanal": 7
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

def calcular_media_mensual():
    RUTA_SEMANAL = "rankings_semanal"
    archivos = sorted([
        f for f in os.listdir(RUTA_SEMANAL)
        if f.endswith(".json")
    ])

    if not archivos:
        print("❌ No hay rankings semanales para calcular la media mensual.")
        return

    acumulado = {}

    for f in archivos:
        with open(os.path.join(RUTA_SEMANAL, f), encoding="utf-8") as jf:
            ranking = json.load(jf).get("top3", [])
            for r in ranking:
                nombre = r["jugador"]
                puntos = r["puntos"]
                if nombre not in acumulado:
                    acumulado[nombre] = []
                acumulado[nombre].append(puntos)

    promedio = [{
        "jugador": nombre,
        "puntos": round(mean(puntos), 2),
        "apariciones": len(puntos)
    } for nombre, puntos in acumulado.items()]

    promedio_ordenado = sorted(promedio, key=lambda x: x["puntos"], reverse=True)
    hoy_fecha = datetime.today().strftime("%Y-%m-%d")

    resumen = {
        "fecha": hoy_fecha,
        "ranking_mensual": promedio_ordenado[:10]
    }

    os.makedirs("rankings_mensual", exist_ok=True)
    with open(f"rankings_mensual/ranking-mensual-{hoy_fecha}.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)

    print(f"📊 Media mensual calculada y guardada en rankings_mensual/ranking-mensual-{hoy_fecha}.json")

if __name__ == "__main__":
    periodo = sys.argv[1] if len(sys.argv) > 1 else "semanal"
    entorno = sys.argv[2] if len(sys.argv) > 2 else "aws"

    if periodo == "mensual":
        calcular_media_mensual()
        sys.exit(0)

    n_dias = PERIODOS.get(periodo, None)

    if n_dias is None:
        try:
            n_dias = int(periodo)
        except ValueError:
            print(f"❌ Periodo inválido: {periodo}")
            sys.exit(1)

    print("📥 Descargando snapshot actual...")
    os.makedirs(STATS_DIR, exist_ok=True)

    try:
        if entorno == "local":
            subprocess.run(["python3", "guardar_stats.py"], check=True)
        else:
            subprocess.run(["node", "../ea_scraper/fetch_stats.js"], check=True)
    except Exception as e:
        print(f"❌ Error al obtener stats: {e}")
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
        if stats_ayer is None:
            stats_ayer = {k: "0" for k in stats_hoy}

        partidos_hoy = int(stats_hoy.get("gamesPlayed", 0))
        partidos_ayer = int(stats_ayer.get("gamesPlayed", 0))
        if partidos_hoy <= partidos_ayer:
            continue

        pos = stats_hoy.get("favoritePosition", "unknown")
        res = calcular_puntos(nombre, pos, stats_hoy, stats_ayer)
        res["puntos"] = round(res["puntos"] / n_dias, 2)
        resultados.append(res)

    ranking = sorted(resultados, key=lambda x: x["puntos"], reverse=True)

    if not ranking:
        print("ℹ️ No se jugaron partidos durante el periodo. No hay ranking disponible.")
        sys.exit(0)

    hoy_fecha = datetime.today().strftime("%Y-%m-%d")

    print(f"\n📊 Ranking medio diario ({periodo}) hasta {hoy_fecha}:\n")
    for i, r in enumerate(ranking, 1):
        print(f"{i}. {r['jugador']} ({r['posicion']}) → {r['puntos']} pts/día ({r['partidos']} partidos)")
        print(f"   🎯 {r['goles']} goles | 🔫 {r['acierto_tiro']}% tiro | 🎁 {r['asistencias']} asist.")
        print(f"   📈 Ratio pases: {r['ratio_pases']} por partido | ⚽ Ratio goleador: {r['ratio_goleador']}")
        print(f"   ✅ {r['pases']} pases / {r['pases_intentados']} intentos ({r['pase_exito']}%)")
        print(f"   🛡️ {r['entradas']} entradas ({r['entrada_exito']}%) | 🥇 {r['mvps']} MVPs | 🟥 {r['rojas']} rojas | ⭐ {r['valoracion_media']} valoración")
        if r["posicion"] == "defender":
            print(f"   🧤 Porterías a 0: {r.get('cleanSheetsDef', 0)} como defensor")
        elif r["posicion"] == "goalkeeper":
            print(f"   🧤 Porterías a 0: {r.get('cleanSheetsGK', 0)} como portero")
        print()

    if ranking:
        resumen = {
            "fecha": hoy_fecha,
            "mvp": ranking[0],
            "top3": ranking[:3]
        }

        ruta_destino = {
            "diario": "rankings_diario",
            "semanal": "rankings_semanal"
        }.get(periodo, "rankings")

        os.makedirs(ruta_destino, exist_ok=True)

        with open(f"{ruta_destino}/ranking-{periodo}-{hoy_fecha}.json", "w", encoding="utf-8") as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        print(f"🏆 Ranking guardado en {ruta_destino}/ranking-{periodo}-{hoy_fecha}.json")

        # Guardar JSON para web
        os.makedirs("data", exist_ok=True)
        ranking_web = {
            "fecha": datetime.today().strftime("%d/%m/%Y"),
            "jugadores": [
                {"nombre": r["jugador"], "puntos": r["puntos"]}
                for r in ranking
            ]
        }
        with open("data/ranking.json", "w", encoding="utf-8") as fw:
            json.dump(ranking_web, fw, indent=2, ensure_ascii=False)
        print("🌐 Archivo data/ranking.json actualizado para la página web.")

        if periodo == "semanal":
            for f in os.listdir(STATS_DIR):
                ruta = os.path.join(STATS_DIR, f)
                if f != f"{hoy_fecha}.json" and f.endswith(".json"):
                    os.remove(ruta)
            print("🧹 Limpiados archivos antiguos de stats/. Solo queda el más reciente.")
