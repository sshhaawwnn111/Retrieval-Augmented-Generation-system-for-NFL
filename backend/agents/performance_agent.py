import json
from pathlib import Path
from langchain_core.prompts import PromptTemplate

# Define a structured prompt for analyzing team performance
performance_prompt_str = """
You are a sports analytics expert for the Baltimore Ravens, focused on weekly player and team performance.

CONTEXT DATA:
{context}

TASK: Analyze the data and provide an in-depth performance summary for {query}.

REQUIRED OUTPUT FORMAT:
1. **Team Summary**: Overall team performance and key metrics (offense, defense, efficiency)
2. **Top Performers**: Highlight standout players and stats
3. **Areas for Improvement**: Notable weaknesses or risks
4. **Analyst Insights**: Data-driven commentary or suggestions
"""

performance_prompt_template = PromptTemplate(
    input_variables=["context", "query"],
    template=performance_prompt_str
)


class PerformanceAgent:
    """
    PerformanceAgent handles player and team analytics based on JSON reports or database data.
    It connects the Ravens database and contextual data files to generate analytical summaries.
    """

    def __init__(self, llm, database_connection=None, data_dir="data"):
        self.llm = llm
        self.db = database_connection
        self.chain = performance_prompt_template | llm
        self.data_dir = Path(data_dir)

    def _load_performance_data(self, filename="test_report.json"):
        """
        Load local performance report data from the data directory.
        """
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Performance file not found: {path}")
        with open(path, "r") as f:
            return json.load(f)

    def _fetch_player_data(self, player_name=None):
        """
        Optionally fetch detailed player stats from the database.
        Works even if DatabaseConnection doesn't define a .query() method.
        """
        if not self.db:
            return None

        try:
            conn = self.db.conn if hasattr(self.db, "conn") else self.db
            cursor = conn.cursor()

            if player_name:
                query = """
                    SELECT name, position, team, stats
                    FROM ravens.players
                    WHERE name ILIKE %s;
                """
                cursor.execute(query, (player_name,))
            else:
                cursor.execute("SELECT name, position, team, stats FROM ravens.players;")

            rows = cursor.fetchall()
            players = [
                {
                    "name": r[0],
                    "position": r[1],
                    "team": r[2],
                    "stats": r[3]
                } for r in rows
            ]
            cursor.close()
            return players

        except Exception as e:
            print(f"⚠️  Database fetch failed: {e}")
            return None


    def analyze_performance(self, query: str):
        """
        Combine contextual data and LLM reasoning for detailed analysis.
        """
        # Load context from local report
        report_data = self._load_performance_data()

        # Optional DB enrichment
        db_data = self._fetch_player_data()

        context = {
            "report_summary": report_data.get("summary"),
            "metrics": report_data.get("metrics"),
            "players": report_data.get("players"),
            "notes": report_data.get("notes"),
            "db_players": db_data
        }

        context_str = json.dumps(context, indent=2)

        # Run through LLM chain
        result = self.chain.invoke({
            "context": context_str,
            "query": query
        })

        return result
