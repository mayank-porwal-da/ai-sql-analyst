import re

from app_core.config import FORBIDDEN_SQL


def validate_sql(sql: str) -> bool:
    normalized = sql.strip()
    if not normalized:
        return False
    if not re.match(r"(?is)^(SELECT|WITH)\b", normalized):
        return False
    body = normalized[:-1] if normalized.endswith(";") else normalized
    if ";" in body:
        return False
    upper = body.upper()
    return not any(re.search(rf"\b{word}\b", upper) for word in FORBIDDEN_SQL)


def clean_sql(sql: str) -> str:
    cleaned = sql.replace("```sql", "").replace("```", "").strip()

    upper_cleaned = cleaned.upper()
    if upper_cleaned.startswith("UNSAFE:") or upper_cleaned.startswith("OUT_OF_SCOPE:"):
        return cleaned

    if upper_cleaned.startswith("SQL:"):
        cleaned = cleaned[4:].strip()

    match = re.search(r"(?is)\b(SELECT|WITH)\b.*", cleaned)
    if match:
        cleaned = match.group(0).strip()

    statements = [part.strip() for part in cleaned.split(";") if part.strip()]
    if statements:
        cleaned = statements[0]

    return cleaned

