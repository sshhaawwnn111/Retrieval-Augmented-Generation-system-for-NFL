import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from backend.agents.injury_agent import InjuryAgent
from backend.agents.db_connection import DatabaseConnection
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2", temperature=0.2)




def main():
    # Connect to DB
    db = DatabaseConnection(
        dbname="Rotowire_Data",
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432"
    )

    # Initialize LLM (or Mock if not available)
    #llm = ChatOllama(model="deepseek-r1:32b", temperature=0.2)

    # Create agent
    agent = InjuryAgent(llm, db)

    # Define a test query
    query = "What is the latest injury update on Joe Burrow?"

    print("🔍 Fetching Rotowire data...")
    data = agent.get_injury_data_from_query(query)
    print("✅ Retrieved context:", data)

    print("\n🧠 Sending to LLM...")
    result = agent.analyze_injury(query)
    print("\n=== LLM OUTPUT ===\n")
    print(result)

    db.close()

if __name__ == "__main__":
    main()
