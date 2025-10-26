from .injury_agent import InjuryAgent
from .contract_agent import ContractAgent
from .scouting_agent import ScoutingAgent
from .performance_agent import PerformanceAgent
from .movement_agent import MovementAgent
from .text2sql_agent import TextToSQLAgent
from .verifier_agent import VerifierAgent
from .coordinator import AgentCoordinator

def initialize_agents(llm, databases):
    """Initialize all agents with their dependencies"""
    agents = {
        "injury": InjuryAgent(llm, databases.get('injury_db')),
        "contract": ContractAgent(llm, databases.get('contract_db')),
        "scouting": ScoutingAgent(llm, databases.get('scouting_db')),
        "performance": PerformanceAgent(llm, databases.get('performance_db')),
        "movement": MovementAgent(llm, databases.get('movement_db')),
        #"text2sql": TextToSQLAgent(llm, databases.get('main_db')),
        "verifier": VerifierAgent(llm, databases.get('verification_db'))
    }
    
    coordinator = AgentCoordinator(llm, agents)
    return coordinator, agents