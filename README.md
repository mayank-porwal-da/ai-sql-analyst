# AI Data Assistant for Chinook Database

## Project Description
AI Data Assistant is a Streamlit application that combines an LLM-powered SQL chatbot with business intelligence dashboards for the Chinook sample database.

The app converts natural language questions into SQL queries, applies SQL safety guardrails, executes validated queries on SQLite, and returns tabular + chart-based insights. It also supports local LLM inference through Ollama models.

## Features
- Natural Language to SQL generation
- SQL guardrails for safe read-only querying
- Query history tracking in chat
- Multi-model support via Ollama (plus Gemini option)
- Store sales BI dashboard
- Database schema explorer dashboard
- Automatic chart generation for chatbot query results

## Architecture
`User -> Streamlit UI -> LLM Agent -> SQL Generation -> SQL Guardrails -> Database -> Results Visualization`

### Runtime Flow
1. User asks a question in the Chatbot tab.
2. The selected LLM generates SQL from the database schema context.
3. Guardrails validate SQL (read-only, single statement, safe keywords).
4. SQL executes against the Chinook SQLite database.
5. Results are shown as a dataframe and optional chart.

## Tech Stack
### Frontend
- Streamlit

### AI / LLM
- LangChain
- Ollama
- Llama / Qwen / Gemini models

### Database
- SQLite (Chinook)
- SQLAlchemy

### Data Processing
- Pandas

### Visualization
- Plotly Express

## Project Structure
```text
final_project/
├── app.py                     # Streamlit entrypoint (UI orchestration)
├── app_core/
│   ├── config.py              # Constants, DB paths, model list, SQL prompt
│   ├── llm.py                 # LLM loading + SQL generation chain
│   ├── sql_utils.py           # SQL cleaning + safety validation
│   ├── database.py            # DB resource loading + analytics queries
│   └── charts.py              # Chat/store chart rendering helpers
├── Chinook_Sqlite.sqlite
├── requirements.txt
└── README.md
```

## Installation
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables (in `.env`):

```env
GOOGLE_API_KEY=your_key_here
```

Note: `GOOGLE_API_KEY` is required only when using Gemini. Local Ollama models do not require it.

## Usage
Run from the `final_project` directory:

```bash
streamlit run app.py
```

### Tabs
- `Store Dashboard`: sales BI metrics and charts
- `Chatbot`: natural-language SQL assistant
- `Database Dashboard`: schema and table overview

## Future Improvements
- Automatic SQL correction / retry loop for invalid SQL
- Query explanation mode using LLM
- Multi-database support (PostgreSQL, MySQL, SQL Server)
- Vector-based schema retrieval for large databases
- Role-based access and query auditing
