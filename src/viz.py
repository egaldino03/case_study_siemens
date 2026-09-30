from datetime import datetime
from io import BytesIO
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyspark.sql.functions as F
from pyspark.sql import SparkSession

try:
    from .helpers import apply_filters, get_data
except ImportError:
    from helpers import apply_filters, get_data


spark = SparkSession.builder.appName("Study Case Siemens").getOrCreate()
df_merged = get_data()

##* DISTRIBUIÇÃO POR REGIONAL DE SERVIÇO


def service_distribution_viz(filters: Dict[Any, Any]):
    df_merged = get_data()
    if filters:
        df_merged = apply_filters(df_merged, filters)

    service_distribution = (
        df_merged.groupby(F.col("level_of_connection"), F.col("service_region"))
        .agg(F.count("*").alias("equipment_count"))
        .orderBy("level_of_connection")
        .withColumn(
            "service_region",
            F.when(
                F.col("service_region") == "SÃO PAULO INTERIOR", F.lit("SP INTERIOR")
            ).otherwise(F.col("service_region")),
        )
        .orderBy(F.col("equipment_count").desc())
    )

    service_distribution.show()

    color_map = {
        "SRS READY": "#009999",
        "CONNECTED BUT NOT SRS READY": "#ec6602",
        "NOT CONNECTED": "#D05353",
    }

    service_distribution_fig = px.bar(
        service_distribution,
        x="service_region",
        y="equipment_count",
        color="level_of_connection",
        # title="Distribuição por Regional de Serviço",
        color_discrete_map=color_map,
    )

    service_distribution_fig.update_yaxes(visible=False)

    service_distribution_fig.update_traces(texttemplate="%{y}", textposition="outside")

    service_distribution_fig.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.3,
            "xanchor": "center",
            "x": 0.5,
        }
    )

    return service_distribution_fig


##* ADERÊNCIA POR LINHA DE NEGÓCIO


def business_line_adherence_viz(filters: Dict[Any, Any]):
    df_merged = get_data()
    if filters:
        df_merged = apply_filters(df_merged, filters)
    business_line_adherence = (
        df_merged.groupby(
            F.col("business_line"),
            F.col("target_srs_ready"),
        )
        .agg(
            F.count("*").alias("total_count"),
            F.sum(
                F.when(F.col("level_of_connection") == "SRS READY", F.lit(1)).otherwise(
                    F.lit(0)
                )
            ).alias("srs_ready_count"),
        )
        .withColumn(
            "adherence_pct",
            F.round((F.col("srs_ready_count") / F.col("total_count") * 100)),
        )
    )
    business_line_adherence = business_line_adherence.withColumn(
        "target_srs_ready", F.round(F.col("target_srs_ready") * 100)
    ).orderBy(F.col("adherence_pct").desc())

    business_line_adherence.show()

    business_line_adherence_pd = business_line_adherence.toPandas()

    bar_colors = [
        "#009999" if row["adherence_pct"] >= row["target_srs_ready"] else "#D05353"
        for _, row in business_line_adherence_pd.iterrows()
    ]

    business_line_adherence_fig = go.Figure()

    business_line_adherence_fig.add_trace(
        go.Bar(
            x=business_line_adherence_pd.business_line,
            y=business_line_adherence_pd.adherence_pct,
            name="Aderente (%)",
            marker_color=bar_colors,  # Cor das barras
            texttemplate="%{y}",  # Exibe os números nas barras
            textposition="inside",
        )
    )

    business_line_adherence_fig.add_trace(
        go.Scatter(
            x=business_line_adherence_pd.business_line,
            y=business_line_adherence_pd.target_srs_ready,
            name="Target (%)",
            mode="lines+markers+text",
            line={"color": "#ec6602", "width": 3},
            texttemplate="%{y}%",
            textposition="middle right",
            marker={
                "symbol": "diamond-open",
                "size": 10,
                "color": "#ec6602",
                "line": {"width": 2},
            },
        )
    )

    business_line_adherence_fig.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.3,
            "xanchor": "center",
            "x": 0.5,
        }
    )

    return business_line_adherence_fig


##* DATAFRAME DISPLAY - EQUIPAMENTOS PARA ATIVAÇÃO
def equipment_for_srs_activation_viz(filters):
    df_merged = get_data()
    if filters:
        df_merged = apply_filters(df_merged, filters)
    return (
        df_merged.withColumn(
            "city/state", F.concat(F.col("city"), F.lit("/"), F.col("state"))
        )
        .filter(F.col("level_of_connection") == "CONNECTED BUT NOT SRS READY")
        .select(
            F.col("equipment_serial_number").alias("Serial Number"),
            F.col("t1.system_name").alias("System"),
            F.col("business_line").alias("Business Line"),
            F.col("city/state").alias("City/State"),
            F.col("service_region").alias("Service Region"),
            F.col("current_connectivity_status").alias("Status"),
        )
        .toPandas()
    )


output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    equipment_for_srs_activation_viz(filters={}).to_excel(
        writer, index=False, sheet_name="Ativação"
    )
excel_data = output.getvalue()

equipment_for_srs_activation_viz(filters={}).to_excel(
    f"data/equip_para_ativacao_remota_{datetime.now().strftime('%Y%m')}.xlsx",
    index=False,
    engine="openpyxl",
)
