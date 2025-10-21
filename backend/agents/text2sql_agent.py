import sys
import os
from langchain_core.prompts import PromptTemplate

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from llm.prompts.text2sql_prompt import text2sql_prompt_template
    print("✅ Loaded text2sql prompt from llm module")
except ImportError:
    # Fallback: define the prompt directly
    print("⚠️ llm module not found, using inline text2sql prompt")
    text2sql_prompt_str = """
    You are an expert SQL query generator for NFL databases.

    DATABASE SCHEMA:
    {schema}

    TASK: Convert the following natural language question into a precise SQL query: {query}

    REQUIRED OUTPUT FORMAT:
    ```sql
    -- Your SQL query here
    SELECT ... FROM ... WHERE ...
    ```

    RULES:
    - Output ONLY the SQL query, no explanations
    - Use proper JOINs and WHERE clauses for efficiency
    - Handle NULL values appropriately
    - Use team abbreviations and standard position codes from the schema
    - Include relevant date ranges and filters
    - Ensure the query is syntactically correct for SQL

    SCHEMA: {schema}
    QUESTION: {query}
    """
    
    text2sql_prompt_template = PromptTemplate(
        input_variables=["query", "schema"],
        template=text2sql_prompt_str
    )

class TextToSQLAgent:
    def __init__(self, llm, database_connection):
        self.llm = llm
        self.db = database_connection
        self.chain = text2sql_prompt_template | llm
    
    def get_schema_data(self, table_name=None):
        """Business logic to fetch database schema"""
        schema_info = {}
        
        if self.db:
            try:
                if table_name:
                    schema_info = self.db.query(
                        "SELECT * FROM information_schema.columns WHERE table_name = ?", 
                        (table_name,)
                    )
                else:
                    schema_info = self.db.query(
                        "SELECT * FROM information_schema.tables"
                    )
            except Exception as e:
                print(f"Database schema query failed: {e}")
        
        return {
            "schema_info": schema_info
        }
    
    def convert_query(self, natural_language_query):
        """Orchestrates the entire conversion process"""
        # 1. Data gathering (business logic)
        context_data = self.get_schema_data()
        
        # 2. LLM call with enriched context
        result = self.chain.invoke({
            "query": natural_language_query,
            "schema": str(context_data)
        })
        
        # 3. Post-processing (business logic)
        sql_query = self._validate_sql_query(result.content)
        
        return sql_query
    
    def _validate_sql_query(self, sql_query):
        """Business logic to verify SQL query"""
        # Extract SQL from markdown code blocks if present
        import re
        sql_match = re.search(r'```sql\s*(.*?)\s*```', sql_query, re.DOTALL)
        if sql_match:
            sql_query = sql_match.group(1).strip()
        
        # Basic SQL validation
        if not sql_query.upper().startswith(('SELECT', 'WITH')):
            return f"Error: Query must start with SELECT or WITH, got: {sql_query[:50]}..."
        
        # Check for common SQL injection patterns (basic)
        dangerous_patterns = ['DROP', 'DELETE', 'UPDATE', 'INSERT', ';--']
        for pattern in dangerous_patterns:
            if pattern in sql_query.upper():
                return f"Error: Query contains potentially dangerous operation: {pattern}"
        
        return sql_query.strip()