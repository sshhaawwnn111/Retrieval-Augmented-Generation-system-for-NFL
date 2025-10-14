import requests
from llm.prompts.injury_prompt import injury_prompt_template

class InjuryAgent:
    def __init__(self, llm, database_connection):
        self.llm = llm
        self.db = database_connection
        self.chain = injury_prompt_template | llm
    
    def get_injury_data(self, player_name, team):
        """Business logic to fetch actual injury data"""
        # Database queries
        injury_history = self.db.query(
            "SELECT * FROM injuries WHERE player = ? AND team = ?", 
            (player_name, team)
        )
        
        # API calls to external services
        medical_reports = self._fetch_medical_reports(player_name)
        
        return {
            "injury_history": injury_history,
            "medical_reports": medical_reports
        }
    
    def _fetch_medical_reports(self, player_name):
        """Private method for data retrieval"""
        # Actual implementation logic
        response = requests.get(f"https://database_link/medical/{player_name}")
        return response.json()
    
    def analyze_injury(self, query):
        """Orchestrates the entire analysis process"""
        # 1. Data gathering (business logic)
        context_data = self.get_injury_data_from_query(query)
        
        # 2. LLM call with enriched context
        result = self.chain.invoke({
            "query": query,
            "context": context_data  # Adding real data to prompt
        })
        
        # 3. Post-processing (business logic)
        analysis = self._validate_medical_analysis(result.content)
        
        return analysis
    
    def _validate_medical_analysis(self, analysis):
        """Business logic to verify medical claims"""
        # Check for unrealistic recovery timelines
        # Validate against known medical data
        # Flag potential inconsistencies
        pass