import requests
from llm.prompts.performance_prompt import performance_prompt_template

class PerformanceAgent:
    def __init__(self, llm, database_connection):
        self.llm = llm
        self.db = database_connection
        self.chain = performance_prompt_template | llm
    
    def get_performance_data(self, player_name, team):
        """Business logic to fetch actual performance data"""
        # Database queries
        player_stats = self.db.query(
            "SELECT * FROM player_stats WHERE player = ? AND team = ?", 
            (player_name, team)
        )
        
        # API calls to external services
        advanced_metrics = self._fetch_advanced_metrics(player_name)
        
        return {
            "player_stats": player_stats,
            "advanced_metrics": advanced_metrics
        }
    
    def _fetch_advanced_metrics(self, player_name):
        """Private method for data retrieval"""
        # Actual implementation logic
        response = requests.get(f"https://database_link/advanced_metrics/{player_name}")
        return response.json()
    
    def analyze_performance(self, query):
        """Orchestrates the entire analysis process"""
        # 1. Data gathering (business logic)
        context_data = self.get_performance_data_from_query(query)
        
        # 2. LLM call with enriched context
        result = self.chain.invoke({
            "query": query,
            "context": context_data  # Adding real data to prompt
        })
        
        # 3. Post-processing (business logic)
        analysis = self._validate_performance_analysis(result.content)
        
        return analysis
    
    def get_performance_data_from_query(self, query):
        """Extract and fetch performance data based on query"""
        player_name, team = self._extract_player_info(query)
        return self.get_performance_data(player_name, team)
    
    def _validate_performance_analysis(self, analysis):
        """Business logic to verify performance claims"""
        # Check for statistical significance
        # Validate against historical data
        # Flag potential outliers or anomalies
        pass
    
    def _extract_player_info(self, query):
        """Extract player name and team from query"""
        # Simple extraction - could use NER in production
        teams = ["Ravens", "BAL", "Baltimore"]
        for team in teams:
            if team.lower() in query.lower():
                return ("Lamar Jackson", "BAL")  # Simplified
        return ("Unknown Player", "Unknown Team")