import json
from tabulate import tabulate

with open("stats/semana_actual.json", encoding="utf-8") as f:
    data = json.load(f)

jugadores = data["members"]

tabla_resumen = []
for j in jugadores:
    tabla_resumen.append([
        j["name"],
        int(j["goals"]),
        int(j["assists"]),
        int(j["gamesPlayed"]),
        float(j["ratingAve"]),
        int(j["passesMade"]),
        int(j["manOfTheMatch"]),
        int(j["redCards"])
    ])

headers = [
    "Jugador", "Goles", "Asistencias", "Partidos",
    "Valoración", "Pases", "MVPs", "Rojas"
]

print("\n📊 Estadísticas globales de Tigueres FC:\n")
print(tabulate(tabla_resumen, headers=headers, tablefmt="grid", stralign="center", numalign="center"))