import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# Import backend modules
from backend.agents.performance_agent import PerformanceAgent
from backend.agents.db_connection import DatabaseConnection
from langchain_ollama import ChatOllama


def main():
    # === LLM SETUP ===
    llm = ChatOllama(model="llama3.2", temperature=0.2)

    # === DATABASE CONNECTION ===
    db = DatabaseConnection(
        dbname="Rotowire_Data",
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432"
    )

    # === INITIALIZE AGENT ===
    data_dir = Path(project_root) / "backend" / "data"
    agent = PerformanceAgent(llm, db, data_dir=data_dir)

    # === DEFINE QUERY ===
    query = "Generate a summary of weekly player and team performance for the Ravens."

    print("Loading performance report and database data...")
    try:
        result = agent.analyze_performance(query)
        print("\n=== PERFORMANCE ANALYSIS REPORT ===\n")
        print(result)
    except Exception as e:
        print(f"Error generating performance report: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
