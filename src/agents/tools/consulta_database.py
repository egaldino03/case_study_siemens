import pyspark.sql.functions as F
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pyspark.sql import SparkSession

try:
    from src.components.helpers import get_data
except ImportError:
    from components.helpers import get_data


spark = (
    SparkSession.builder.appName("StreamlitSparkAgent")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)

df_merged = get_data().select(
    F.col("t1.*"),
    F.col("MOBILE_SYSTEM_OR_FIXED_SYSTEM?".lower()),
    F.col("target_srs_ready"),
)
df_merged.createOrReplaceTempView("df_merged")


@tool
def execute_spark_sql(query: str) -> str:
    """
    Executa uma consulta SQL SELECT na tabela `df_merged`.

    SCHEMA EXATO:

    equipment_serial_number
    level_of_connection
    system_id
    system_name
    business_line
    city
    state
    service_region
    current_connectivity_status
    equipment_installation_date
    material_id
    mobile_system_or_fixed_system?
    target_srs_ready

    DEFINIÇÕES:

    SRS READY:
        level_of_connection = 'SRS READY'

    TAXA SRS:
        quantidade SRS READY / quantidade total

    PROBLEMA SRS:
        level_of_connection != 'SRS READY'

    REGIÃO:
        service_region

    LINHA DE EQUIPAMENTO:
        business_line

    TARGET SRS:
        target_srs_ready

    IMPORTANTE:

    `pais`, `country`, `problema_conectividade_srs`,
    `taxa_conectividade_srs` e `linha_equipamento`
    NÃO são colunas existentes.

    Esses conceitos devem ser derivados das colunas existentes.
    """

    try:
        normalized_query = query.strip().lower()

        if not normalized_query.startswith("select"):
            return "ERRO: somente consultas SELECT são permitidas."

        # Prevent multiple SQL statements
        if ";" in normalized_query[:-1]:
            return "ERRO: múltiplas instruções SQL não são permitidas."

        result = spark.sql(query)

        local_result = result.limit(20).toPandas()

        if local_result.empty:
            return "Nenhum dado encontrado."

        return local_result.to_json(orient="records", force_ascii=False)

    except Exception as e:
        return f"SQL_ERROR: {str(e)}"
