#!/bin/bash
cd ~/ea-stats

FECHA=$(date +%F)
LOG="logs/diario-${FECHA}.log"

# Ejecutar análisis diario y guardar salida específica
python3 main.py diario > "$LOG" 2>&1

# Enviar ese log por correo
python3 send_email.py "📊 Informe Diario EA Stats - $FECHA" "$LOG"

