"""
config.py
=========
Aqui ficam todas as definições que podes querer ajustar.
"""

from datetime import date

# De onde vamos buscar o calendário: caminho de um ficheiro .ics local,
# ou um link https://... (o teu link do iCloud)
CALENDAR_SOURCE = "calendar.ics"

# Quantas horas contas por dia de trabalho normal
EXPECTED_DAILY_HOURS = 8.0

# Onde vão parar os relatórios e gráficos gerados
OUTPUT_DIR = "output"