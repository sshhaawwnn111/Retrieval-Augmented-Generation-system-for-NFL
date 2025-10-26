import requests
from llm.prompts.contract_prompt import contract_prompt_template

class ContractAgent:
    def __init__(self, llm, database_connection):
        self.llm = llm
        self.db = database_connection
        self.chain = contract_prompt_template | llm
    
    def get_contract_data(self, player_name, team):
        """Business logic to fetch actual contract data"""
        # Database queries
        contract_details = self.db.query(
            "SELECT * FROM contracts WHERE player = ? AND team = ?", 
            (player_name, team)
        )
        
        # API calls to external services
        salary_cap_info = self._fetch_salary_cap_data(player_name, team)
        
        return {
            "contract_details": contract_details,
            "salary_cap_info": salary_cap_info
        }
    
    def _fetch_salary_cap_data(self, player_name, team):
        """Private method for data retrieval"""
        # Actual implementation logic
        response = requests.get(f"https://database_link/salary_cap/{team}/{player_name}")
        return response.json()
    
    def analyze_contract(self, query):
        """Orchestrates the entire analysis process"""
        # 1. Data gathering (business logic)
        context_data = self.get_contract_data_from_query(query)
        
        # 2. LLM call with enriched context
        result = self.chain.invoke({
            "query": query,
            "context": context_data  # Adding real data to prompt
        })
        
        # 3. Post-processing (business logic)
        analysis = self._validate_contract_analysis(result.content)
        
        return analysis
    
    def get_contract_data_from_query(self, query):
        """Extract and fetch contract data based on query"""
        player_name, team = self._extract_player_info(query)
        return self.get_contract_data(player_name, team)
    
    def _validate_contract_analysis(self, analysis):
        """Business logic to verify contract claims"""
        # Check for salary cap compliance
        # Validate against CBA rules
        # Flag potential calculation errors
        pass
    
    def _extract_player_info(self, query):
        """Extract player name and team from query"""
        # Simple extraction - could use NER in production
        teams = ["Ravens", "BAL", "Baltimore"]
        for team in teams:
            if team.lower() in query.lower():
                return ("Lamar Jackson", "BAL")  # Simplified
        return ("Unknown Player", "Unknown Team")