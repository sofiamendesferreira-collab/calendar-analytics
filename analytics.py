"""
analytics.py
============
Calcula estatísticas a partir da lista de eventos que o parser.py devolve.
"""
from datetime import date, timedelta
from config import EXPECTED_DAILY_HOURS


def daily_summary(eventos: list) -> dict:
    """Soma as horas trabalhadas em cada dia.

    Devolve um dicionário: {data: horas_trabalhadas}
    """
    horas_por_dia = {}

    for evento in eventos:
        dia = evento["data"]
        duracao = evento["duracao_horas"]
        horas_por_dia[dia] = horas_por_dia.get(dia, 0) + duracao

    return horas_por_dia
def overtime_summary(eventos: list) -> dict:
    """Para cada dia, calcula quantas horas passaram das EXPECTED_DAILY_HOURS."""
    horas_por_dia = daily_summary(eventos)

    overtime_por_dia = {}
    for dia, horas in horas_por_dia.items():
        extra = horas - EXPECTED_DAILY_HOURS
        overtime_por_dia[dia] = round(max(extra, 0), 2)

    return overtime_por_dia


def total_overtime(eventos: list) -> float:
    """Soma todo o overtime, desde o primeiro evento até ao último."""
    overtime_por_dia = overtime_summary(eventos)
    return round(sum(overtime_por_dia.values()), 2)
def client_stats(eventos: list) -> dict:
    """Soma as horas totais gastas em cada cliente."""
    horas_por_cliente = {}

    for evento in eventos:
        cliente = evento["cliente"]
        duracao = evento["duracao_horas"]
        horas_por_cliente[cliente] = horas_por_cliente.get(cliente, 0) + duracao

    # arredondar tudo a 2 casas decimais
    for cliente in horas_por_cliente:
        horas_por_cliente[cliente] = round(horas_por_cliente[cliente], 2)

    return horas_por_cliente
def type_stats(eventos: list) -> dict:
    """Soma as horas totais por tipo de evento: projeto, reuniao, formacao, outro."""
    horas_por_tipo = {}

    for evento in eventos:
        tipo = evento["tipo"]
        duracao = evento["duracao_horas"]
        horas_por_tipo[tipo] = horas_por_tipo.get(tipo, 0) + duracao

    for tipo in horas_por_tipo:
        horas_por_tipo[tipo] = round(horas_por_tipo[tipo], 2)

    return horas_por_tipo


def meeting_hours_internal_vs_client(eventos: list) -> dict:
    """Separa as horas de reunião entre internas (cliente = MJ) e de cliente."""
    internas = 0
    de_cliente = 0

    for evento in eventos:
        if evento["tipo"] != "reuniao":
            continue
        if evento["cliente"] == "MJ":
            internas += evento["duracao_horas"]
        else:
            de_cliente += evento["duracao_horas"]

    return {
        "internas": round(internas, 2),
        "de_cliente": round(de_cliente, 2),
    }
def period_range(tipo: str, data_referencia: date) -> tuple:
    """Dado um tipo ('Dia', 'Semana', 'Mês', 'Ano') e uma data de referência,
    devolve (data_inicio, data_fim) desse período."""

    if tipo == "Dia":
        return data_referencia, data_referencia

    if tipo == "Semana":
        inicio = data_referencia - timedelta(days=data_referencia.weekday())  # segunda-feira
        fim = inicio + timedelta(days=6)  # domingo
        return inicio, fim

    if tipo == "Mês":
        inicio = data_referencia.replace(day=1)
        if inicio.month == 12:
            fim = date(inicio.year + 1, 1, 1) - timedelta(days=1)
        else:
            fim = date(inicio.year, inicio.month + 1, 1) - timedelta(days=1)
        return inicio, fim

    if tipo == "Ano":
        return date(data_referencia.year, 1, 1), date(data_referencia.year, 12, 31)

    raise ValueError(f"Tipo de período desconhecido: {tipo}")


def expected_hours(eventos: list) -> float:
    """Horas esperadas no período: 8h por cada dia com pelo menos 1 evento
    registado (ignora fins de semana, feriados e férias automaticamente,
    já que nesses dias não há eventos no calendário)."""
    dias_com_eventos = set(evento["data"] for evento in eventos)
    return len(dias_com_eventos) * EXPECTED_DAILY_HOURS


def work_type_stats(eventos: list) -> dict:
    """Soma horas por tipo de trabalho (ex: WRA, Site Assessment) — só eventos de projeto."""
    horas_por_tipo_trabalho = {}
    for evento in eventos:
        if evento["tipo"] != "projeto":
            continue
        chave = evento["detalhe"] or "(sem tipo de trabalho)"
        horas_por_tipo_trabalho[chave] = horas_por_tipo_trabalho.get(chave, 0) + evento["duracao_horas"]

    for chave in horas_por_tipo_trabalho:
        horas_por_tipo_trabalho[chave] = round(horas_por_tipo_trabalho[chave], 2)
    return horas_por_tipo_trabalho


def project_stats(eventos: list) -> dict:
    """Soma horas por projeto (ex: Pilot WPP) — só eventos de projeto."""
    horas_por_projeto = {}
    for evento in eventos:
        if evento["tipo"] != "projeto":
            continue
        chave = evento["categoria"] or "(sem projeto)"
        horas_por_projeto[chave] = horas_por_projeto.get(chave, 0) + evento["duracao_horas"]

    for chave in horas_por_projeto:
        horas_por_projeto[chave] = round(horas_por_projeto[chave], 2)
    return horas_por_projeto