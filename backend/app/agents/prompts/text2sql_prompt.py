TEXT2SQL_PROMPT = """
You are an expert SQL query generator for NFL databases.

DATABASE SCHEMA:
{schema}

TASK: Convert the following natural language question into a precise SQL query: {query}

REQUIRED OUTPUT FORMAT:
```sql
-- Your SQL query here
SELECT ... FROM ... WHERE ...
"""