"""
utils.py
========
Pequenas funções auxiliares usadas noutros ficheiros.
"""

import re
import os


def webcal_to_https(url: str) -> str:
    """Troca 'webcal://' por 'https://' no início do link, se necessário."""
    return re.sub(r"^webcal://", "https://", url.strip())


def ensure_dir(path: str) -> str:
    """Cria a pasta 'path' se ela ainda não existir."""
    os.makedirs(path, exist_ok=True)
    return path


def format_hours(hours: float) -> str:
    """Transforma 9.75 em '9h45', por exemplo."""
    whole_hours = int(hours)
    minutes = round((hours - whole_hours) * 60)
    return f"{whole_hours}h{minutes:02d}"