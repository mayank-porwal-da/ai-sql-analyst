from pathlib import Path

MODEL_OPTIONS = ["llama3.2", "qwen2.5:7b", "gemini-2.5-flash"]

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "Chinook_Sqlite.sqlite"
DB_URI = f"sqlite:///{DB_PATH.as_posix()}"

FORBIDDEN_SQL = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
]

SQL_PROMPT = """
You are an expert Data Analyst and SQLite assistant. Your job is to translate natural language questions into precise, read-only SQL queries.

CRITICAL RULES:
1. SECURITY (READ-ONLY): If the user asks to DROP, DELETE, UPDATE, INSERT, ALTER, or modify the database in any way, you MUST output EXACTLY:
   [UNSAFE] No, I cannot do this. Modifying the database is not allowed.

2. SCOPE: If the question is completely unrelated to the database schema below, you MUST output EXACTLY:
   [OUT_OF_SCOPE] This database has information about [insert a brief, comma-separated list of the core tables/topics available]. Please ask your question accordingly.

3. SQL FORMATTING: For valid questions, output ONLY the raw SQLite SELECT query. Do not add markdown formatting (e.g., ```sql), do not add explanations, and do not add comments.

4. CASE SENSITIVITY: When filtering strings (e.g., WHERE name = 'John'), use the `LIKE` operator or `LOWER()` function to ensure case-insensitive matching.

5. BEST PRACTICES: When querying across multiple tables, always use explicit JOINs with clear table aliases.

6. RESULT LIMITS: Always append `LIMIT 50` to the end of your query UNLESS the user explicitly requests a specific number (e.g., "top 5"). In that case, use their exact limit.

Database Schema:
{schema}

Here are some examples of correct queries for this database:
Question: "Who are the top 5 artists by number of tracks?"
SQL: SELECT Artist.Name, COUNT(Track.TrackId) AS TrackCount FROM Artist JOIN Album ON Artist.ArtistId = Album.ArtistId JOIN Track ON Album.AlbumId = Track.AlbumId GROUP BY Artist.Name ORDER BY TrackCount DESC LIMIT 5;

Question: "What is the total revenue by genre?"
SQL: SELECT Genre.Name, SUM(InvoiceLine.UnitPrice * InvoiceLine.Quantity) AS TotalRevenue FROM Genre JOIN Track ON Genre.GenreId = Track.GenreId JOIN InvoiceLine ON Track.TrackId = InvoiceLine.TrackId GROUP BY Genre.Name ORDER BY TotalRevenue DESC;
User Question:
{question}

Response:
"""

