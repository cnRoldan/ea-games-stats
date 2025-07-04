# EA Games Stats

Este proyecto contiene varios scripts en Python para descargar y analizar las estadísticas de un club de **EA SPORTS FC** (modo Pro Clubs). Permite obtener snapshots diarios, procesar los partidos jugados y calcular rankings de MVP diarios, semanales, mensuales y un historial acumulado.

## Dependencias
- Python 3
- [`requests`](https://pypi.org/project/requests/)

Instala las dependencias ejecutando:

```bash
pip install requests
```

## Configuración
En varios scripts se definen las constantes `CLUB_ID` y `PLATFORM`. Modifica estos valores con el identificador y la plataforma de tu club antes de ejecutar los ejemplos:

```python
CLUB_ID = "1005509"      # ID de tu club
PLATFORM = "common-gen5"  # Plataforma (ej. common-gen5, ps5, etc.)
```

Los archivos de estadísticas se guardan en la carpeta `stats/` y los partidos descargados se almacenan en `matches/`.

## Uso
A continuación se muestran los comandos básicos para cada script.

### Guardar estadísticas globales
Descarga las estadísticas del club y las guarda con la fecha actual:

```bash
python guardar_stats.py
```

Se crea un archivo `stats/AAAA-MM-DD.json`.

### Analizar partidos del día
Obtiene los partidos jugados hoy, los guarda en `matches/` y muestra el ranking diario de puntos por jugador:

```bash
python analizar_partidos.py
```

### Calcular MVP diario
Compara las estadísticas de ayer y hoy (archivos en `stats/`) para determinar el jugador más valioso del día:

```bash
python mvp.py
```

### Calcular MVP semanal
Requiere un snapshot de estadísticas de hace siete días. Ejecuta:

```bash
python mvp_semanal_stats.py
```

### Calcular MVP mensual
Calcula el MVP tomando como referencia las estadísticas de hace 30 días:

```bash
python mvp_mensual_stats.py
```

### Ranking histórico acumulado
A partir de todos los archivos dentro de `matches/`, genera un ranking histórico de puntos:

```bash
python ranking_historico.py
```

---
Estos scripts permiten llevar un seguimiento detallado del rendimiento de cada jugador en tu club de EA SPORTS FC.
