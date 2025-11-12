import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from backend.agents.injury_agent import InjuryAgent
from backend.agents.db_connection import DatabaseConnection
from langchain_ollama import ChatOllama

# Initialize LLM
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

    # Create agent with LLM and DB
    agent = InjuryAgent(llm, db)

    # Query for Lamar Jackson
    query = "What info do you have on Lamar Jackson?"

    print("Fetching Rotowire data...")
    data = agent.get_injury_data_from_query(query)
    if not data:
        print("No recent news found for this player.")
    else:
        print("Retrieved context:")
        for item in data:
            print(f"- {item['date']}: {item['headline']} "
                  f"(Status: {item['injury_status']}, Detail: {item['injury_detail']})")

    print("\nSending to LLM...")
    result = agent.analyze_injury(query)
    print("\n=== LLM OUTPUT ===\n")
    print(result)

    db.close()

if __name__ == "__main__":
    main()
