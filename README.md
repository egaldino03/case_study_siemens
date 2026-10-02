# Siemens Study Case Dashboard

## English

### Overview

This project is an interactive Streamlit dashboard for monitoring equipment connectivity and SRS readiness. It loads the study-case workbook, prepares the data with Polars and Apache Spark, and presents:

- KPI cards for total equipment, connectivity, and SRS readiness.
- Filters for the main equipment and business dimensions.
- Interactive visualizations for service distribution, business-line adherence, and equipment requiring SRS activation.
- An optional executive assistant that answers questions about the loaded data using Spark SQL and LangChain.

The main application is [`src/app.py`](./src/app.py). The dashboard components are under [`src/components/`](./src/components/), and the assistant implementation is under [`src/agents/`](./src/agents/).

### Requirements

- Python 3.12 or newer.
- Java available on `PATH`, required by PySpark.
- [`uv`](https://docs.astral.sh/uv/) recommended for dependency and virtual-environment management.
- The source workbook in [`data/`](./data/).
- An OpenRouter API key only if the executive assistant is used.

### Run locally with `uv`

From the repository root:

```bash
uv sync
uv run streamlit run src/app.py
```

Before starting the assistant, create a local `.env` file with:

```dotenv
OPENROUTER_API_KEY=your-openrouter-api-key
```

Never commit `.env` or expose the API key in source code.

Open the URL printed by Streamlit, usually:

```text
http://localhost:8501
```

Run the command from the repository root. The application currently uses data paths relative to that directory.

### Run locally with an existing virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
streamlit run src/app.py
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### Data flow

1. [`src/components/helpers.py`](./src/components/helpers.py) reads the source workbook from `data/`.
2. Polars exports the workbook sheets to temporary CSV files.
3. Spark loads and transforms the CSV data into the dashboard dataset.
4. The component modules calculate KPIs and build Plotly visualizations.
5. The assistant tool in [`src/agents/tools/consulta_database.py`](./src/agents/tools/consulta_database.py) queries the Spark view with read-only `SELECT` statements.

The dashboard may create generated CSV files in `data/`. These are derived files and should not be treated as source data.

### Tests

Run the test suite from the repository root:

```bash
uv run pytest
```

Or, with an activated virtual environment:

```bash
pytest
```

### Troubleshooting

- **`ModuleNotFoundError`**: run Streamlit from the repository root using `streamlit run src/app.py`.
- **Workbook not found**: confirm that the source `.xlsx` file exists under `data/` and that the command was started from the repository root.
- **Spark or Java errors**: verify that Java is installed and available through `PATH`.
- **Assistant configuration errors**: verify `OPENROUTER_API_KEY` in the local `.env` file. The dashboard and visualizations do not require the assistant when no assistant request is made.

---

## Português (Brasil)

### Visão geral

Este projeto é um dashboard interativo em Streamlit para acompanhar a conectividade dos equipamentos e a situação de prontidão para SRS. O sistema lê a planilha do estudo de caso, prepara os dados com Polars e Apache Spark e apresenta:

- Cards de KPI para total de equipamentos, conectividade e prontidão para SRS.
- Filtros para os principais atributos dos equipamentos e das linhas de negócio.
- Visualizações interativas de distribuição de serviços, aderência por linha de negócio e equipamentos que precisam de ativação SRS.
- Um assistente executivo opcional que responde perguntas sobre os dados carregados usando Spark SQL e LangChain.

A aplicação principal está em [`src/app.py`](./src/app.py). Os componentes do dashboard estão em [`src/components/`](./src/components/), e a implementação do assistente está em [`src/agents/`](./src/agents/).

### Requisitos

- Python 3.12 ou superior.
- Java disponível no `PATH`, necessário para o PySpark.
- [`uv`](https://docs.astral.sh/uv/) recomendado para gerenciar dependências e ambiente virtual.
- A planilha de origem em [`data/`](./data/).
- Uma chave da API do OpenRouter somente se o assistente executivo for utilizado.

### Executar localmente com `uv`

Na raiz do repositório:

```bash
uv sync
uv run streamlit run src/app.py
```

Antes de iniciar o assistente, crie um arquivo `.env` local com:

```dotenv
OPENROUTER_API_KEY=sua-chave-da-api-do-openrouter
```

Nunca faça commit do arquivo `.env` nem exponha a chave da API no código-fonte.

Abra a URL exibida pelo Streamlit, normalmente:

```text
http://localhost:8501
```

Execute o comando a partir da raiz do repositório. Atualmente, a aplicação utiliza caminhos de dados relativos a esse diretório.

### Executar localmente com um ambiente virtual existente

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
streamlit run src/app.py
```

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

### Fluxo dos dados

1. [`src/components/helpers.py`](./src/components/helpers.py) lê a planilha de origem em `data/`.
2. O Polars exporta as abas da planilha para arquivos CSV temporários.
3. O Spark carrega e transforma os CSVs no conjunto de dados do dashboard.
4. Os módulos de componentes calculam os KPIs e constroem as visualizações com Plotly.
5. A ferramenta do assistente em [`src/agents/tools/consulta_database.py`](./src/agents/tools/consulta_database.py) consulta a view do Spark usando apenas comandos `SELECT`.

O dashboard pode criar arquivos CSV derivados em `data/`. Esses arquivos são resultados gerados e não devem ser tratados como dados de origem.

### Testes

Execute a suíte de testes a partir da raiz do repositório:

```bash
uv run pytest
```

Ou, com o ambiente virtual ativado:

```bash
pytest
```

### Solução de problemas

- **`ModuleNotFoundError`**: execute o Streamlit a partir da raiz do repositório com `streamlit run src/app.py`.
- **Planilha não encontrada**: confirme que o arquivo `.xlsx` de origem está em `data/` e que o comando foi iniciado na raiz do repositório.
- **Erros do Spark ou Java**: verifique se o Java está instalado e disponível no `PATH`.
- **Erros de configuração do assistente**: confirme `OPENROUTER_API_KEY` no arquivo `.env` local. O dashboard e as visualizações não dependem do assistente enquanto nenhuma solicitação ao assistente for feita.
