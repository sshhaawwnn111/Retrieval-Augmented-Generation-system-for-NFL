# backend/agents/coordinator.py
import sys
import os
from typing import Dict

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

class AgentCoordinator:
    def __init__(self, llm, agents: Dict):
        self.llm = llm
        self.agents = agents
    
    def route_query(self, query: str) -> Dict:
        """Simple query routing based on keywords"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['injury', 'hurt', 'recovery', 'hamstring', 'ankle']):
            return {"primary_agent": "injury", "supporting_agents": []}
        elif any(word in query_lower for word in ['performance', 'stats', 'metrics', 'analyze']):
            return {"primary_agent": "performance", "supporting_agents": []}
        elif any(word in query_lower for word in ['contract', 'salary', 'cap', 'money']):
            return {"primary_agent": "contract", "supporting_agents": []}
        elif any(word in query_lower for word in ['scout', 'draft', 'evaluate', 'talent']):
            return {"primary_agent": "scouting", "supporting_agents": []}
        elif any(word in query_lower for word in ['trade', 'free agency', 'move', 'transaction']):
            return {"primary_agent": "movement", "supporting_agents": []}
        else:
            return {"primary_agent": "performance", "supporting_agents": ["injury"]}
    
    def execute_agents(self, query: str, routing_plan: Dict) -> Dict:
        """Execute the query with the routed agents"""
        primary_agent_name = routing_plan["primary_agent"]
        supporting_agents = routing_plan["supporting_agents"]
        
        results = {}
        
        # Execute primary agent
        if primary_agent_name in self.agents and self.agents[primary_agent_name]:
            primary_agent = self.agents[primary_agent_name]
            try:
                if hasattr(primary_agent, 'analyze'):
                    results["primary"] = primary_agent.analyze(query)
                elif hasattr(primary_agent, 'analyze_injury'):
                    results["primary"] = primary_agent.analyze_injury(query)
                elif hasattr(primary_agent, 'analyze_performance'):
                    results["primary"] = primary_agent.analyze_performance(query)
                else:
                    results["primary"] = "Agent method not found"
            except Exception as e:
                results["primary"] = f"Error: {e}"
        
        # Execute supporting agents
        results["supporting"] = {}
        for agent_name in supporting_agents:
            if agent_name in self.agents and self.agents[agent_name]:
                agent = self.agents[agent_name]
                try:
                    if hasattr(agent, 'analyze'):
                        results["supporting"][agent_name] = agent.analyze(query)
                    elif hasattr(agent, 'analyze_injury'):
                        results["supporting"][agent_name] = agent.analyze_injury(query)
                    elif hasattr(agent, 'analyze_performance'):
                        results["supporting"][agent_name] = agent.analyze_performance(query)
                    else:
                        results["supporting"][agent_name] = "Agent method not found"
                except Exception as e:
                    results["supporting"][agent_name] = f"Error: {e}"
        
        return results