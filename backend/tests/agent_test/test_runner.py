# backend/tests/agent_test/test_runner.py
import sys
import os

# Add the project root to Python path (RavensRotoWire folder)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

print(f"🔍 Project root: {project_root}")
print(f"🔍 Backend dir: {backend_dir}")

# Import from current directory
from test_data_processor import TestDataProcessor
from mock_database import MockDatabase

class AgentTestRunner:
    def __init__(self, llm, sample_report_path=None):
        self.llm = llm
        self.processor = TestDataProcessor()
        self.sample_data = None
        
        if sample_report_path:
            self.load_sample_data(sample_report_path)
    
    def load_sample_data(self, file_path: str):
        """Load and process sample report data"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        self.sample_data = self.processor.process_sample_report(content)
        print(f"✅ Loaded data for {len(self.sample_data)} teams")
    
    def test_injury_agent(self):
        """Test the Injury Agent with sample data"""
        print("\n" + "="*50)
        print("TESTING INJURY AGENT")
        print("="*50)
        
        # Import with full path from backend
        from agents.injury_agent import InjuryAgent
        
        # Use mock database for testing
        mock_db = MockDatabase(self.sample_data)
        injury_agent = InjuryAgent(self.llm, mock_db)
        
        # Test with Baltimore Ravens injuries
        ravens_injuries = self.sample_data['Baltimore Ravens']['injuries']
        
        for injury in ravens_injuries[:2]:  # Test first 2 injuries
            query = f"What is the impact of {injury['player']}'s {injury['injury']} on the Baltimore Ravens?"
            
            print(f"\n🔍 Testing: {query}")
            try:
                # Use the agent's analyze method
                result = injury_agent.analyze_injury(query)
                print(f"✅ Response: {result[:200]}...")
            except Exception as e:
                print(f"❌ Error in analyze_injury: {e}")
                # Fallback: test the chain directly
                try:
                    context_data = {
                        'player': injury['player'],
                        'injury': injury['injury'],
                        'position': injury['position'],
                        'team': injury['team']
                    }
                    result = injury_agent.chain.invoke({
                        "query": query,
                        "context": str(context_data)
                    })
                    print(f"✅ Fallback Response: {result.content[:200]}...")
                except Exception as e2:
                    print(f"❌ Fallback also failed: {e2}")
    
    def test_performance_agent(self):
        """Test the Performance Agent with sample data"""
        print("\n" + "="*50)
        print("TESTING PERFORMANCE AGENT")
        print("="*50)
        
        from agents.performance_agent import PerformanceAgent
        
        mock_db = MockDatabase(self.sample_data)
        performance_agent = PerformanceAgent(self.llm, mock_db)
        
        # Test with over/under performers
        for team_name, team_data in self.sample_data.items():
            performers = team_data['over_performers'] + team_data['under_performers']
            
            for performer in performers[:1]:  # Test first performer per team
                query = f"Analyze {performer['player']}'s performance for the {team_name}"
                
                print(f"\n🔍 Testing: {query}")
                try:
                    result = performance_agent.analyze_performance(query)
                    print(f"✅ Response: {result[:200]}...")
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    def run_all_tests(self):
        """Run all agent tests"""
        if not self.sample_data:
            print("❌ No sample data loaded. Please load sample data first.")
            return
        
        self.test_injury_agent()
        self.test_performance_agent()