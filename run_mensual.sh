#!/bin/bash
cd ~/ea-stats

FECHA=$(date +%F)
LOG="logs/mensual-${FECHA}.log"

python3 main.py mensual > "$LOG" 2>&1
python3 send_email.py "📈 Informe Mensual EA Stats - $FECHA" "$LOG"
