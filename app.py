import streamlit as st
from parser import load_events
from analytics import daily_summary, overtime_summary, total_overtime, client_stats, type_stats

st.set_page_config(page_title="Horas de Trabalho", layout="wide")
st.title("📊 Dashboard de Horas de Trabalho")

def verificar_password():
    """Mostra uma caixa de password e só deixa continuar se estiver correta."""

    def password_correta():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["autenticado"] = True
            del st.session_state["password"]  # não guarda a password em memória
        else:
            st.session_state["autenticado"] = False

    if st.session_state.get("autenticado", False):
        return True

    st.text_input("Password", type="password", on_change=password_correta, key="password")

    if "autenticado" in st.session_state and not st.session_state["autenticado"]:
        st.error("Password incorreta")

    return False


if not verificar_password():
    st.stop()  # não deixa correr o resto do dashboard sem password certa

LINK_ICLOUD = st.secrets["link_icloud"]

from analytics import period_range, expected_hours, work_type_stats, project_stats

eventos_todos = load_events(LINK_ICLOUD)

st.sidebar.header("Filtros")

opcoes_periodo = ["Dia", "Semana", "Mês", "Ano", "Personalizado", "Todo o Período"]
tipo_periodo = st.sidebar.selectbox("Período", opcoes_periodo, index=1)

todas_as_datas = [e["data"] for e in eventos_todos]
data_min = min(todas_as_datas)
data_max = max(todas_as_datas)

if tipo_periodo == "Todo o Período":
    inicio, fim = data_min, data_max

elif tipo_periodo == "Personalizado":
    intervalo = st.sidebar.date_input(
        "Escolhe o intervalo",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )
    # só atualiza quando já tens as 2 datas escolhidas (início e fim)
    if len(intervalo) == 2:
        inicio, fim = intervalo
    else:
        inicio, fim = data_min, data_max

else:
    data_referencia = st.sidebar.date_input(
        "Data de referência",
        value=data_max,
        min_value=data_min,
        max_value=data_max,
    )
    inicio, fim = period_range(tipo_periodo, data_referencia)

eventos = [e for e in eventos_todos if inicio <= e["data"] <= fim]

st.sidebar.caption(f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}")

horas_dia = daily_summary(eventos)
overtime_dia = overtime_summary(eventos)
total_horas = round(sum(horas_dia.values()), 2)
total_extra = total_overtime(eventos)

col1, col2, col3 = st.columns(3)
col1.metric("Total de horas trabalhadas", f"{total_horas} h")
col2.metric("Total de overtime", f"{total_extra} h")
col3.metric("Nº de eventos", len(eventos))

horas_esperadas = expected_hours(eventos)
diferenca = round(total_horas - horas_esperadas, 2)

st.subheader("Horas esperadas vs. trabalhadas")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Horas esperadas neste período", f"{horas_esperadas} h")
col_b.metric("Horas trabalhadas", f"{total_horas} h")

if diferenca >= 0:
    col_c.metric("Diferença", f"+{diferenca} h", delta=f"{diferenca} h acima do esperado")
else:
    col_c.metric("Diferença", f"{diferenca} h", delta=f"{diferenca} h abaixo do esperado")

import plotly.express as px
import pandas as pd

st.subheader("Horas trabalhadas por dia")

df_dias = pd.DataFrame({
    "Data": list(horas_dia.keys()),
    "Horas": list(horas_dia.values()),
})
df_dias = df_dias.sort_values("Data")

fig = px.bar(df_dias, x="Data", y="Horas", title="")
fig.add_hline(y=8, line_dash="dash", line_color="gray",
              annotation_text="Dia normal (8h)")

st.plotly_chart(fig, use_container_width=True)
st.subheader("Horas por Cliente")

dados_cliente = client_stats(eventos)
df_cliente = pd.DataFrame({
    "Cliente": list(dados_cliente.keys()),
    "Horas": list(dados_cliente.values()),
}).sort_values("Horas", ascending=False)

fig_cliente = px.bar(df_cliente, x="Cliente", y="Horas")
st.plotly_chart(fig_cliente, use_container_width=True)


st.subheader("Distribuição por Tipo de Atividade")

dados_tipo = type_stats(eventos)
df_tipo = pd.DataFrame({
    "Tipo": list(dados_tipo.keys()),
    "Horas": list(dados_tipo.values()),
})

fig_tipo = px.pie(df_tipo, names="Tipo", values="Horas")
st.plotly_chart(fig_tipo, use_container_width=True)
st.subheader("Percentagem por Tipo de Trabalho")

dados_tipo_trabalho = work_type_stats(eventos)
if dados_tipo_trabalho:
    df_tipo_trabalho = pd.DataFrame({
        "Tipo de Trabalho": list(dados_tipo_trabalho.keys()),
        "Horas": list(dados_tipo_trabalho.values()),
    })
    fig_tipo_trabalho = px.pie(df_tipo_trabalho, names="Tipo de Trabalho", values="Horas")
    st.plotly_chart(fig_tipo_trabalho, use_container_width=True)
else:
    st.info("Sem eventos de projeto neste período.")


st.subheader("Percentagem por Projeto")

dados_projeto = project_stats(eventos)
if dados_projeto:
    df_projeto = pd.DataFrame({
        "Projeto": list(dados_projeto.keys()),
        "Horas": list(dados_projeto.values()),
    })
    fig_projeto = px.pie(df_projeto, names="Projeto", values="Horas")
    st.plotly_chart(fig_projeto, use_container_width=True)
else:
    st.info("Sem eventos de projeto neste período.")