import requests
from app.agents.prompts.movement_prompt import MOVEMENT_PROMPT

class MovementAgent:
    def __init__(self, llm, database_connection):
        self.llm = llm
        self.db = database_connection
        self.chain = MOVEMENT_PROMPT | llm
    
    def get_movement_data(self, player_name, team):
        """Business logic to fetch actual player movement data"""
        # Database queries
        transaction_history = self.db.query(
            "SELECT * FROM transactions WHERE player = ? AND team = ?", 
            (player_name, team)
        )
        
        # API calls to external services
        market_analysis = self._fetch_market_data(player_name)
        
        return {
            "transaction_history": transaction_history,
            "market_analysis": market_analysis
        }
    
    def _fetch_market_data(self, player_name):
        """Private method for data retrieval"""
        # Actual implementation logic
        response = requests.get(f"https://database_link/market_analysis/{player_name}")
        return response.json()
    
    def analyze_movement(self, query):
        """Orchestrates the entire analysis process"""
        # 1. Data gathering (business logic)
        context_data = self.get_movement_data_from_query(query)
        
        # 2. LLM call with enriched context
        result = self.chain.invoke({
            "query": query,
            "context": context_data  # Adding real data to prompt
        })
        
        # 3. Post-processing (business logic)
        analysis = self._validate_movement_analysis(result.content)
        
        return analysis
    
    def get_movement_data_from_query(self, query):
        """Extract and fetch movement data based on query"""
        player_name, team = self._extract_player_info(query)
        return self.get_movement_data(player_name, team)
    
    def _validate_movement_analysis(self, analysis):
        """Business logic to verify movement claims"""
        # Check for CBA rule compliance
        # Validate against transaction history
        # Flag potential timing or procedural issues
        pass
    
    def _extract_player_info(self, query):
        """Extract player name and team from query"""
        # Simple extraction - could use NER in production
        teams = ["Ravens", "BAL", "Baltimore"]
        for team in teams:
            if team.lower() in query.lower():
                return ("Lamar Jackson", "BAL")  # Simplified
        return ("Unknown Player", "Unknown Team")