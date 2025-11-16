# import sys
# import os

# # Add project root to path
# project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(0, project_root)

# try:
#     from llm.prompts.text2sql_prompt import text2sql_prompt_template
#     print("Loaded text2sql prompt from llm module")
# except ImportError:
#     print("llm module not found")

# class TextToSQLAgent:
#     def __init__(self, llm, database_connection):
#         self.llm = llm
#         self.db = database_connection
#         self.chain = text2sql_prompt_template | llm
    
#     def get_schema_data(self, table_name=None):
#         """Business logic to fetch database schema"""
#         schema_info = {}
        
#         if self.db:
#             try:
#                 if table_name:
#                     schema_info = self.db.query(
#                         "SELECT * FROM information_schema.columns WHERE table_name = ?", 
#                         (table_name,)
#                     )
#                 else:
#                     schema_info = self.db.query(
#                         "SELECT * FROM information_schema.tables"
#                     )
#             except Exception as e:
#                 print(f"Database schema query failed: {e}")
        
#         return {
#             "schema_info": schema_info
#         }
    
#     def convert_query(self, natural_language_query):
#         """Orchestrates the entire conversion process"""
#         # 1. Data gathering (business logic)
#         context_data = self.get_schema_data()
        
#         # 2. LLM call with enriched context
#         result = self.chain.invoke({
#             "query": natural_language_query,
#             "schema": str(context_data)
#         })
        
#         # 3. Post-processing (business logic)
#         sql_query = self._validate_sql_query(result.content)
        
#         return sql_query
    
#     def _validate_sql_query(self, sql_query):
#         """Business logic to verify SQL query"""
#         # Extract SQL from markdown code blocks if present
#         import re
#         sql_match = re.search(r'```sql\s*(.*?)\s*```', sql_query, re.DOTALL)
#         if sql_match:
#             sql_query = sql_match.group(1).strip()
        
#         # Basic SQL validation
#         if not sql_query.upper().startswith(('SELECT', 'WITH')):
#             return f"Error: Query must start with SELECT or WITH, got: {sql_query[:50]}..."
        
#         # Check for common SQL injection patterns (basic)
#         dangerous_patterns = ['DROP', 'DELETE', 'UPDATE', 'INSERT', ';--']
#         for pattern in dangerous_patterns:
#             if pattern in sql_query.upper():
#                 return f"Error: Query contains potentially dangerous operation: {pattern}"
        
#         return sql_query.strip()