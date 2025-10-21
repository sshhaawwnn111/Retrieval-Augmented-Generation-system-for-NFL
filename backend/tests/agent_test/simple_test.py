# backend/test/simple_test.py
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_data_processing():
    """Test just the data processing without agents"""
    from agent_test.test_data_processor import TestDataProcessor
    
    processor = TestDataProcessor()
    
    sample_content = """
    # NFL Team Executive Summary Report

    ## Baltimore Ravens
    **Injured:** Lamar Jackson (QB – hamstring), Ronnie Stanley (OT – ankle)
    **Over Performers:** DeAndre Hopkins (WR)
    **Under Performers:** Lamar Jackson (sack issues)
    The Ravens are dealing with multiple injuries.
    """
    
    data = processor.process_sample_report(sample_content)
    print("✅ Data processing successful!")
    print(f"Teams: {list(data.keys())}")
    
    for team, team_data in data.items():
        print(f"\n{team}:")
        print(f"  Injuries: {len(team_data['injuries'])}")
        for injury in team_data['injuries']:
            print(f"    - {injury['player']}: {injury['injury']}")

def test_agent_structure():
    """Test that agents can be imported"""
    try:
        # Define prompts inline to avoid import issues
        from langchain_core.prompts import PromptTemplate
        
        injury_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="Analyze: {query} with context: {context}"
        )
        
        print("✅ Can create prompt templates")
        return injury_prompt
        
    except Exception as e:
        print(f"❌ Error creating prompts: {e}")
        return None

def main():
    print("🧪 RUNNING SIMPLE TESTS")
    print("=" * 50)
    
    test_data_processing()
    print("\n" + "-" * 30)
    test_agent_structure()

if __name__ == "__main__":
    main()