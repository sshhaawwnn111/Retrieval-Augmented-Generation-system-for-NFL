# backend/tests/agent_test/demo_test.py
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Add the backend directory to Python path  
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

# Import from current directory
from test_runner import AgentTestRunner

def get_llm():
    """Get LLM with fallback options"""
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(model="deepseek-r1:32b", temperature=0.2)
    except ImportError:
        print("❌ langchain-ollama not available. Using mock LLM.")
        return MockLLM()

class MockLLM:
    """Mock LLM for testing when no real LLM is available"""
    def invoke(self, input_dict):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        query = input_dict.get("query", "")
        context = input_dict.get("context", "")
        
        if "injury" in query.lower():
            return MockResponse(f"Mock Injury Analysis: Based on {context}, this appears to be a significant injury affecting team performance.")
        elif "performance" in query.lower():
            return MockResponse(f"Mock Performance Analysis: Examining {context}, the player shows promising development.")
        else:
            return MockResponse(f"Mock Analysis: I've reviewed '{query}' and provide this assessment.")

def main():
    # Initialize LLM
    llm = get_llm()
    
    # Create test runner
    test_runner = AgentTestRunner(llm)
    
    # Sample report content
    sample_content = """
    # NFL Team Executive Summary Report

    ## Baltimore Ravens
    **Injured:** Lamar Jackson (QB – hamstring), Ronnie Stanley (OT – ankle)
    **Over Performers:** DeAndre Hopkins (WR)
    **Under Performers:** Lamar Jackson (sack issues)
    The Ravens are dealing with multiple injuries.

    ## Buffalo Bills
    **Injured:** Ed Oliver (DT), Matt Milano (LB)
    **Suspended:** Michael Hoecht (OB), Larry Ogunjobi (DT)
    **Over Performers:** Josh Allen (QB), James Cook (RB)
    The Bills are unbeaten but stretched thin.
    """
    
    # Process the sample content
    test_runner.sample_data = test_runner.processor.process_sample_report(sample_content)
    
    # Run all tests
    test_runner.run_all_tests()

if __name__ == "__main__":
    main()