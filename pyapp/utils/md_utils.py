import re

def strip_sql_markdown(text: str) -> str:
    return re.sub(r"^```sql\s*|^```\s*|```$", "", text.strip(), flags=re.MULTILINE).strip()
