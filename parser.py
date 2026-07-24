"""
parser.py
=========
Vai buscar o calendário e transforma-o numa lista organizada de eventos.
"""

import requests
from icalendar import Calendar
from utils import webcal_to_https


def load_ics_bytes(source: str) -> bytes:
    """Descarrega o conteúdo do calendário a partir de um link, ou lê um
    ficheiro .ics local, dependendo do que 'source' for."""
    if source.startswith("http") or source.startswith("webcal"):
        url = webcal_to_https(source)
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()
        return resposta.content
    else:
        with open(source, "rb") as f:
            return f.read()
def split_title(titulo: str) -> dict:
    """Divide um título em Cliente / Projeto-ou-Categoria / Detalhe.

    Exemplos:
        'Maingrid - Pilot WPP - WRA'   -> projeto
        'MJ - Meeting - Weekly Sync'   -> reunião interna
    """
    partes = [p.strip() for p in titulo.split(" - ")]

    if len(partes) < 2:
        return {"tipo": "outro", "cliente": partes[0], "categoria": "", "detalhe": ""}

    cliente = partes[0]
    segundo = partes[1]
    terceiro = partes[2] if len(partes) >= 3 else ""

    palavras_reuniao = {"meeting", "reuniao", "reunião"}
    palavras_formacao = {"training", "formacao", "formação"}

    if segundo.lower() in palavras_reuniao:
        return {"tipo": "reuniao", "cliente": cliente, "categoria": "Reunião", "detalhe": terceiro}
    if segundo.lower() in palavras_formacao:
        return {"tipo": "formacao", "cliente": cliente, "categoria": "Formação", "detalhe": terceiro}

    # Se não for reunião nem formação, assumimos que é um projeto
    return {"tipo": "projeto", "cliente": cliente, "categoria": segundo, "detalhe": terceiro}
def load_events(source: str) -> list:
    """Lê o calendário todo e devolve uma lista de eventos já organizados."""
    conteudo = load_ics_bytes(source)
    calendario = Calendar.from_ical(conteudo)

    eventos = []
    for componente in calendario.walk("VEVENT"):
        titulo = str(componente.get("SUMMARY", "Sem título"))
        inicio = componente.get("DTSTART").dt
        fim_prop = componente.get("DTEND")

        # ignora eventos sem hora de fim, ou eventos de "dia inteiro"
        if fim_prop is None or not hasattr(inicio, "hour"):
            continue

        fim = fim_prop.dt
        duracao_horas = round((fim - inicio).total_seconds() / 3600, 2)

        info = split_title(titulo)
        eventos.append({
            "titulo": titulo,
            "inicio": inicio,
            "fim": fim,
            "data": inicio.date(),
            "duracao_horas": duracao_horas,
            **info,   # junta tipo/cliente/categoria/detalhe
        })

    return eventos