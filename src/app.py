from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import pyspark.sql.functions as F
import seaborn as sns
import streamlit as st
from pyspark.sql import DataFrame, SparkSession

try:
    from src.card_kpis import (
        get_connected_not_srs,
        get_disconnected,
        get_srs_ready_pct,
        total_equipment,
    )
except ModuleNotFoundError:
    from card_kpis import (  # type: ignore
        get_connected_not_srs,
        get_disconnected,
        get_srs_ready_pct,
        total_equipment,
    )

try:
    from src.sidebar import get_filters
except ModuleNotFoundError:
    from sidebar import get_filters

try:
    from src.viz import (
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
    delta="Requer Infra",
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
