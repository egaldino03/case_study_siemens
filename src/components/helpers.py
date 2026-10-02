import re

import polars as pl
import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession


def get_data() -> DataFrame:
    spark = SparkSession.builder.appName("Study Case Siemens").getOrCreate()

    workbook_path = (
        "data/Study Case - Vaga de Estágio CS SO OPE_BRUNO SANTIAGO DA CO.xlsx"
    )
    overview_csv = "data/overview.csv"
    target_csv = "data/target.csv"

    pl.read_excel(workbook_path, sheet_name="Overview", engine="calamine").write_csv(
        overview_csv
    )
    pl.read_excel(workbook_path, sheet_name="Target", engine="calamine").write_csv(
        target_csv
    )

    df_overview = (
        spark.read.option("header", True).option("inferSchema", True).csv(overview_csv)
    )
    df_target = (
        spark.read.option("header", True).option("inferSchema", True).csv(target_csv)
    )

    def rename_cols(df: DataFrame) -> DataFrame:
        for col in df.columns:
            if col != "TARGET (SRS READY)":
                df = df.withColumnRenamed(col, col.replace(" ", "_").lower())
            else:
                df = df.withColumnRenamed(col, "target_srs_ready")

        return df

    df_overview = rename_cols(df_overview)
    df_target = rename_cols(df_target)

    df_merged = df_overview.alias("t1").join(
        df_target.alias("t2"),
        on=(F.col("t1.system_id") == F.col("t2.material_id")),
        how="left",
    )

    return df_merged


def format_title_with_srs(text: str) -> str:
    """Aplica title() mas garante que 'SRS' permaneça em maiúsculo."""
    if not text:
        return text
    # 1. Transforma em formato Title (ex: "srs automotivo" -> "Srs Automotivo")
    title_text = text.title()
    # 2. Substitui "Srs" (com limite de palavra) por "SRS"
    return re.sub(re.compile(r"\bSrs\b"), "SRS", title_text)


def apply_filters(df: DataFrame, filters: dict[str, list[str]]) -> DataFrame:
    for column, values in filters.items():
        if values:
            df = df.filter(F.col(column).isin([value.upper() for value in values]))

    return df
