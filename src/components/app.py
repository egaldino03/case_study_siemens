from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import pyspark.sql.functions as F
import seaborn as sns
import streamlit as st
from langchain.messages import AIMessage, HumanMessage
from pyspark.sql import DataFrame, SparkSession

try:
    from src.components.card_kpis import (
        get_connected_not_srs,
        get_disconnected,
        get_srs_ready_pct,
        total_equipment,
    )
except ModuleNotFoundError:
    from card_kpis import (
        get_connected_not_srs,
        get_disconnected,
        get_srs_ready_pct,
        total_equipment,
    )

try:
    from src.components.sidebar import get_filters
except ModuleNotFoundError:
    from sidebar import get_filters

try:
    from src.components.viz import (
        business_line_adherence_viz,
        equipment_for_srs_activation_viz,
        excel_data,
        service_distribution_viz,
    )
except ModuleNotFoundError:
    from viz import (
        business_line_adherence_viz,
        equipment_for_srs_activation_viz,
        excel_data,
        service_distribution_viz,
    )
try:
    from src.agents.executive_helper import get_agent
except ModuleNotFoundError:
    from agents.executive_helper import get_agent

INITIAL_MESSAGE = (
    "Olá! 👋 Sou seu Assistente Executivo.\n\n"
    "Posso ajudar você a analisar **equipamentos, conectividade "
    "SRS, regiões, estados, cidades e linhas de equipamentos**.\n\n"
    "Faça uma pergunta sobre os dados do dashboard."
)

st.set_page_config(
    page_title="Siemens Healthineers Monthly SRS follow-up Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def load_agent():
    return get_agent()


agent = load_agent()

if "messages" not in st.session_state:

    st.session_state.messages = [AIMessage(content=INITIAL_MESSAGE)]


def get_final_ai_message(messages):
    """Retorna a ultima mensagem do agente."""
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            return message

    return None


with st.sidebar:
    st.image(
        "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/79/Siemens_Healthineers_logo.svg/1280px-Siemens_Healthineers_logo.svg.png?utm_source=pt.wikipedia.org&utm_campaign=index&utm_content=thumbnail"
    )
    region_list = ["Todas as Regionais"]
    selected_region = st.multiselect(
        "Regional de Serviço".upper(), region_list + get_filters("service_region")
    )

    business_list = ["Todas as Linhas"]
    selected_business = st.multiselect(
        "linha de negócio".upper(), business_list + get_filters("business_line")
    )

    status_list = ["Todos os Status"]
    selected_connection = st.multiselect(
        "status da conexão".upper(), status_list + get_filters("level_of_connection")
    )

filter_dict = {}

if selected_region and "Todas as Regionais" not in selected_region:
    filter_dict["service_region"] = selected_region

if selected_business and "Todas as Linhas" not in selected_business:
    filter_dict["business_line"] = selected_business

if selected_connection and "Todos os Status" not in selected_connection:
    filter_dict["level_of_connection"] = selected_connection

st.markdown("# Monitor de Conectividade Brasil", text_alignment="left")
st.markdown(
    "Acompanhamento mensal de equipamentos e metas de acesso remoto SRS",
    text_alignment="left",
)

chat_container = st.container(border=True)
st.subheader("Assistente Executivo")
with chat_container:
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            continue

        with st.chat_message(role):
            st.markdown(message.content)

    user_input = st.chat_input("Pergunte sobre equipamentos, conectividade, região...")

    if user_input:
        human_message = HumanMessage(content=user_input)
        st.session_state.messages.append(human_message)

        with chat_container:
            with st.chat_message("user"):
                st.markdown(human_message.content)

            with st.chat_message("assistant"):
                with st.spinner("Analisando os dados..."):
                    try:
                        response = agent.invoke({"messages": st.session_state.messages})

                        assistant_message = get_final_ai_message(response["messages"])
                        if assistant_message is None:
                            assistant_content = (
                                "Não foi possível obter uma resposta do assistente"
                            )
                        else:
                            assistant_content = assistant_message.content
                        st.markdown(assistant_content)

                        if assistant_message is not None:
                            st.session_state.messages.append(assistant_message)
                        else:
                            st.session_state.messages.append(
                                AIMessage(content=assistant_content)
                            )
                    except Exception as e:
                        error_msg = (
                            f"Ocorreu um erro ao consultar o assistente: {str(e)}"
                        )
                        st.error(error_msg)
                        st.session_state.messages.append(AIMessage(content=error_msg))

col1, col2 = st.columns(2)

col1.metric(
    label="Equipamento Total".upper(),
    value=total_equipment(filter_dict),
    delta="Equipamentos Monitorados",
    delta_color="off",
    format="localized",
    border=True,
    icon=":material/precision_manufacturing:",
)

col2.metric(
    label="Taxa SRS Ready (Real)".upper(),
    value=f"{get_srs_ready_pct(filter_dict)}%",
    delta="Equipamentos Monitorados",
    format="localized",
    border=True,
    icon=":material/check_circle:",
    help="Percentual de equipamentos que estão com o status `SRS READY`.",
)


col3, col4 = st.columns(2)

col3.metric(
    label="Faltam serviços ativos".upper(),
    value=get_connected_not_srs(filter_dict),
    delta="Oportunidade Imediata",
    delta_color="yellow",
    format="localized",
    border=True,
    icon=":material/restart_alt:",
    help="Conectado à rede, porém sem SRS",
)

col4.metric(
    label="Total desconectados".upper(),
    value=get_disconnected(filter_dict),
    delta="Requer Instalação de Infraestrutura",
    delta_color="red",
    format="localized",
    border=True,
    icon=":material/block:",
)

st.markdown("---")


st.markdown("### Distribuição por Regional de Serviço")
st.plotly_chart(
    service_distribution_viz(filter_dict),
    width="stretch",
    height="content",
    theme="streamlit",
    key=None,
    on_select="ignore",
    selection_mode=("points", "box", "lasso"),
    config=None,
)

st.markdown("### Adêrencia por tipo de equipamento")
st.plotly_chart(
    business_line_adherence_viz(filter_dict),
    width="stretch",
    height="content",
    theme="streamlit",
    key=None,
    on_select="ignore",
    selection_mode=("points", "box", "lasso"),
    config=None,
)

with st.container(
    horizontal=True,
    horizontal_alignment="left",
    vertical_alignment="top",
    gap="large",
):
    with st.container(horizontal=False, vertical_alignment="center", gap="small"):
        st.markdown("### Plano de Ação: Equipamentos para Ativação")
        st.markdown(
            "Lista de equipamentos com conexão ativa porém pendentes de ativação SRS"
        )
    st.download_button(
        label="📥 Baixar dados em Excel",
        data=excel_data,
        file_name=f"../data/equip_para_ativacao_remota_{datetime.now().strftime("%Y%m")}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.dataframe(equipment_for_srs_activation_viz(filter_dict))
