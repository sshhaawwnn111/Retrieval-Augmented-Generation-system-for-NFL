# backend/agents/injury_agent.py
import sys
import os

# Add the project root to Python path (go up from backend to RavensRotoWire)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from llm.prompts.injury_prompt import injury_prompt_template
    print("✅ Loaded injury prompt from llm module")
except ImportError as e:
    print(f"❌ Failed to import from llm module: {e}")
    print(f"🔍 Python path: {sys.path}")
    # Fallback: define the prompt directly
    from langchain_core.prompts import PromptTemplate
    injury_prompt_str = """
    You are a medical and sports analytics expert specializing in NFL player injuries.

    CONTEXT DATA:
    {context}

    TASK: Analyze injury data for: {query}

    OUTPUT FORMAT:
    1. **Current Status**: Injury designation and timeline
    2. **Medical Analysis**: Injury type and recovery period  
    3. **Impact Assessment**: Team performance implications

    CONTEXT: {context}
    QUERY: {query}
    """
    
    injury_prompt_template = PromptTemplate(
        input_variables=["query", "context"],
        template=injury_prompt_str
    )

class InjuryAgent:
    def __init__(self, llm, database_connection):
        self.llm = llm
        self.db = database_connection
        self.chain = injury_prompt_template | llm
    
    def get_injury_data(self, player_name, team):
        """Business logic to fetch actual injury data"""
        injury_data = {}
        
        # Database queries
        if self.db:
            try:
                injury_history = self.db.query(
                    "SELECT * FROM injuries WHERE player = ? AND team = ?", 
                    (player_name, team)
                )
                injury_data['history'] = injury_history
            except Exception as e:
                print(f"Database query failed: {e}")
        
        # Mock medical reports for testing
        medical_reports = self._fetch_medical_reports(player_name)
        injury_data['medical_reports'] = medical_reports
        
        return injury_data
    
    def _fetch_medical_reports(self, player_name):
        """Private method for data retrieval"""
        # Mock implementation for testing
        return {
            "injury_type": "Hamstring Strain",
            "severity": "Grade 2", 
            "estimated_recovery": "3-4 weeks"
        }
    
    def analyze_injury(self, query):
        """Orchestrates the entire analysis process"""
        # 1. Data gathering (business logic)
        context_data = self.get_injury_data_from_query(query)
        
        # 2. LLM call with enriched context
        result = self.chain.invoke({
            "query": query,
            "context": str(context_data)
        })
        
        return result.content
    
    def get_injury_data_from_query(self, query):
        """Extract and fetch injury data based on query"""
        player_name, team = self._extract_player_info(query)
        return self.get_injury_data(player_name, team)
    
    def _extract_player_info(self, query):
        """Extract player name and team from query"""
        # Simple extraction for testing
        if "lamar" in query.lower() or "jackson" in query.lower():
            return ("Lamar Jackson", "Baltimore Ravens")
        return ("Unknown Player", "Unknown Team")