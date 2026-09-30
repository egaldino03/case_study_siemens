from pyspark.sql import SparkSession

from src.helpers import apply_filters, format_title_with_srs, get_data

spark = SparkSession.builder.appName("Study Case Siemens").getOrCreate()

df_merged = get_data()


def test_format_title_with_srs():
    assert format_title_with_srs("srs automotivo") == "SRS Automotivo"
    assert format_title_with_srs("SISTEMA SRS") == "Sistema SRS"
    assert (
        format_title_with_srs("treinamento de srs operacional")
        == "Treinamento De SRS Operacional"
    )
    assert format_title_with_srs("SRS") == "SRS"


def test_apply_filters():
    filtered_df = {
        "level_of_connection": ["SRS READY"],
        "business_line": ["AXA"],
    }
    assert apply_filters(df_merged, filtered_df).count() == 161

    filtered_df = {
        "level_of_connection": ["SRS READY", "CONNECTED BUT NOT SRS READY"],
        "business_line": ["AXA"],
    }
    assert apply_filters(df_merged, filtered_df).count() == 175

    filtered_df = {}
    assert apply_filters(df_merged, filtered_df).count() == 2286


def test_get_data():
    assert get_data().count() == 2286
