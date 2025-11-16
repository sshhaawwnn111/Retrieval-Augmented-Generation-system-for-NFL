from langchain_core.prompts import PromptTemplate

text2sql_prompt_str = """
You are an expert SQL query generator for NFL databases.

DATABASE SCHEMA:
{schema}

TASK: Convert the following natural language question into a precise SQL query: {query}

REQUIRED OUTPUT FORMAT:
```sql
-- Your SQL query here
SELECT ... FROM ... WHERE ...
"""