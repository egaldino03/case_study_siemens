import re
from typing import List

import polars as pl
import pyspark.sql.functions as F
from matplotlib.pylab import str_
from pyspark.sql import DataFrame, SparkSession

try:
    from .helpers import apply_filters, format_title_with_srs, get_data
except ImportError:
    from src.components.helpers import apply_filters, format_title_with_srs, get_data

spark = SparkSession.builder.appName("Study Case Siemens").getOrCreate()

df_merged = get_data()


def total_equipment(filters: dict[str, list[str]] | None = None) -> int:
    """Retorna a contagem total de equipamentos."""
    query = df_merged

    if not filters:
        return query.select("equipment_serial_number").count()

    return apply_filters(query, filters).select("equipment_serial_number").count()


def get_srs_ready_pct(filters: dict[str, list[str]] | None) -> float:
    """Retorna a taxa de equipamentos com conexão SRS ativa."""
    srs_ready = F.col("level_of_connection") == "SRS READY"
    df = df_merged
    if not filters:
        return round((df.filter(srs_ready).count() / df.count()) * 100, 2)

    return round(
        (
            apply_filters(df_merged, filters).filter(srs_ready).count()
            / df_merged.count()
        )
        * 100,
        2,
    )


def get_connected_not_srs(filters: dict[str, list[str]]) -> int:
    """Retorna a quantidade de equipamentos conectados na rede mas que ainda não tem SRS"""
    connected_not_srs = (
        F.col("level_of_connection") == "CONNECTED BUT NOT SRS READY"
    ) & (F.col("current_connectivity_status") == "Connection OK")
    df = df_merged
    if not filters:
        return df_merged.filter(connected_not_srs).count()

    return apply_filters(df_merged, filters).filter(connected_not_srs).count()


def get_disconnected(filters: dict[str, list[str]]) -> int:
    disconnected = (F.col("level_of_connection") == "NOT CONNECTED") | (
        F.col("current_connectivity_status").startswith("Connection Expired")
    )
    if not filters:
        return df_merged.filter(disconnected).count()

    return apply_filters(df_merged, filters).filter(disconnected).count()
