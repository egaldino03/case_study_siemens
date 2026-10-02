from typing import List

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

try:
    from .helpers import format_title_with_srs, get_data
except ImportError:
    from src.components.helpers import format_title_with_srs, get_data

spark = SparkSession.builder.appName("Study Case Siemens").getOrCreate()

df_merged = get_data()


def get_filters(col: str) -> List[str]:
    """Retorna as categorias para filtragem vindas da base de dados"""
    if col == "business_line":
        return df_merged.select(F.collect_set(col)).first()[0]  # type: ignore

    return [format_title_with_srs(option) for option in df_merged.select(F.collect_set(col)).first()[0]]  # type: ignore
