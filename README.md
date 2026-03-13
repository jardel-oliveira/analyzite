# Analyzite

Analyzite é uma aplicação para análise automática de pesquisas (surveys) usando Python, Streamlit e agentes de IA.

O sistema permite:

- Importar bases de respostas de pesquisas
- Interpretar a estrutura do questionário
- Gerar KPIs analíticos automaticamente
- Executar métricas com Python/Pandas
- Visualizar resultados em dashboards interativos

---

# Tecnologias utilizadas

## Backend

- Python 3.11+
- Pandas
- Pydantic
- SQLite
- Plotly

## Interface

- Streamlit
- CSS customizado

## Estrutura analítica

- Python/Pandas para cálculo de métricas
- JSON Schema para estrutura de surveys
- Analysis Plan gerado por agente de IA

## Gerenciamento de dependências

- uv (Python package manager)

---

# Requisitos

- Python 3.11 ou superior
- Git
- uv

Instalação do uv:

Linux / Mac:

```bash
pip install uv


analyzite
│
├─ app.py
├─ pyproject.toml
├─ README.md
│
├─ assets
│
├─ src
│  ├─ analysis
│  ├─ parsers
│  ├─ services
│  ├─ pages
│  ├─ ui
│  └─ utils


