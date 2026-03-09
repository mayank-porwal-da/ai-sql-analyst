# AI SQL Analyst

This project is a Streamlit web application that acts as an AI-powered data analyst. It leverages the power of Large Language Models (LLMs) through LangChain and Google Gemini to convert natural language questions into SQL queries. The application then executes these queries against a SQLite database (Chinook) and visualizes the results as dataframes and charts.

This project serves as a foundational step in exploring AI Agents, focusing on tool use (SQL execution) and LLM integration.

## 🚀 Try It Online

**Live Demo: ** [https://ai-sql-analyst-chinook-db.streamlit.app/](https://ai-sql-analyst-chinook-db.streamlit.app/)

No installation needed! Click the link above to start asking questions about the Chinook database powered by AI.

## Features

- **Natural Language to SQL**: Ask questions in plain English and get SQL queries as answers.
- **Interactive Chat Interface**: A user-friendly chat interface to interact with the AI analyst.
- **Automatic Chart Generation**: The application automatically generates bar or line charts based on the query results.
- **SQL Query Validation**: A security measure to prevent unsafe SQL operations like `DROP`, `DELETE`, `UPDATE`, `INSERT`, and `ALTER`.
- **Display Generated SQL**: The generated SQL query is displayed to the user for transparency and learning purposes.

## Getting Started

### Prerequisites

- Python 3.7+
- pip
- A Google API key with the Gemini API enabled.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/mayank-porwal-da/ai-sql-analyst.git
    cd ai-sql-analyst
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**

    A `requirements.txt` file is provided in the project. So install the packages by running:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the environment variables:**

    Create a `.env` file in the root directory of the project and add your Google API key:

    ```
    GOOGLE_API_KEY="your-google-api-key"
    ```

## Usage

To run the Streamlit application, use the following command:

```bash
streamlit run app.py
```

This will open the application in your web browser. You can then start asking data-related questions in the chat input.

## Project Structure

```
.
├── app.py              # The main Streamlit application file.
├── Chinook_Sqlite.sqlite # The SQLite database file.
├── .env                # The file to store the Google API key.
└── .streamlit/
    └── secrets.toml    # Streamlit secrets file (can also be used for API keys).
```

## Acknowledgements

This project is powered by the following amazing technologies:

- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [Google Gemini](https://deepmind.google/technologies/gemini/)
- [Plotly](https://plotly.com/)
- [Pandas](https://pandas.pydata.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
