#!/bin/bash
cd ~/ea-stats

FECHA=$(date +%F)
LOG="logs/semanal-${FECHA}.log"

python3 main.py semanal > "$LOG" 2>&1
python3 send_email.py "🏆 Ranking Semanal EA Stats - $FECHA" "$LOG"
