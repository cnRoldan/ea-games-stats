def calcular_puntos(nombre, pos, stats_hoy, stats_ayer):
    def diff(campo):
        return float(stats_hoy.get(campo, 0)) - float(stats_ayer.get(campo, 0))

    # Diferencias principales
    goles = diff("goals")
    asistencias = diff("assists")
    pases_realizados = diff("passesMade")
    tackles = diff("tacklesMade")
    mvps = diff("manOfTheMatch")
    rojas = diff("redCards")
    partidos = diff("gamesPlayed")
    clean_def = diff("cleanSheetsDef")
    clean_gk = diff("cleanSheetsGK")

    # Porcentajes y promedios actuales
    pase_exito = float(stats_hoy.get("passSuccessRate", 0))
    entrada_exito = float(stats_hoy.get("tackleSuccessRate", 0))
    tiro_exito = float(stats_hoy.get("shotSuccessRate", 0))
    valoracion_media = float(stats_hoy.get("ratingAve", 0))
    win_rate = float(stats_hoy.get("winRate", 0))

    ratio_goleador = goles / partidos if partidos > 0 else 0
    ratio_pases = pases_realizados / partidos if partidos > 0 else 0

    # Estimación de pases intentados y fallidos
    if pase_exito > 0:
        pases_intentados = int(round(pases_realizados / (pase_exito / 100)))
    else:
        pases_intentados = int(pases_realizados)
    pases_fallidos = pases_intentados - int(pases_realizados)

    # Multiplicadores por posición
    if pos == "midfielder":
        tackle_valor = 2.0
        pase_valor = 0.01
    elif pos == "defender":
        tackle_valor = 0.6
        pase_valor = 0.015
    elif pos == "goalkeeper":
        tackle_valor = 0.8
        pase_valor = 0.02
    else:
        tackle_valor = 0.5
        pase_valor = 0.01

    # Nuevo bonus de portería a 0
    bonus_clean = 0
    if pos == "defender":
        bonus_clean = clean_def * 12
    elif pos == "goalkeeper":
        bonus_clean = clean_gk * 12

    # Bonus por precisión de pase
    bonus_pase = 0
    if pase_exito >= 80:
        bonus_pase = 2
    elif pase_exito < 70:
        bonus_pase = -1.5

    # Bonus por precisión de tiro
    bonus_tiro = 0
    if tiro_exito >= 40:
        bonus_tiro = 1.5
    elif tiro_exito < 20 and partidos > 0:
        bonus_tiro = -1

    # Bonus por entradas efectivas
    bonus_tackle = 1 if entrada_exito > 25 and tackles > 5 else 0

    # Penalización fuerte por pases fallidos
    penalizacion_pases = pases_fallidos * 0.3

    # Cálculo total
    puntos = (
        goles * 2.0 +
        asistencias * 3.5 +
        pases_realizados * pase_valor +
        tackles * tackle_valor +
        partidos * 0.5 +
        mvps * 4.0 +
        valoracion_media * 1 +
        (win_rate // 10) * 1 +
        bonus_clean +
        bonus_pase +
        bonus_tiro +
        bonus_tackle -
        rojas * 2 -
        penalizacion_pases
    )

    return {
        "jugador": nombre,
        "posicion": pos,
        "puntos": round(puntos, 2),
        "partidos": int(partidos),
        "goles": int(goles),
        "asistencias": int(asistencias),
        "pases": int(pases_realizados),
        "pase_exito": round(pase_exito, 1),
        "pases_fallidos": int(pases_fallidos),
        "pases_intentados": int(pases_intentados),
        "tiros": "-",  # No disponibles en stats
        "acierto_tiro": round(tiro_exito, 1),
        "entradas": int(tackles),
        "entrada_exito": round(entrada_exito, 1),
        "mvps": int(mvps),
        "rojas": int(rojas),
        "valoracion_media": round(valoracion_media, 2),
        "clean_sheets": int(clean_def if pos == "defender" else clean_gk if pos == "goalkeeper" else 0),
        "ratio_pases": round(ratio_pases, 2),
        "ratio_goleador": round(ratio_goleador, 2),
        "cleanSheetsDef": int(clean_def),
        "cleanSheetsGK": int(clean_gk)
    }
