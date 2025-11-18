# backend/agents/coordinator_agent.py
from datetime import datetime
import logging

from app.agents.injury_agent import InjuryAgent



logger = logging.getLogger(__name__)
class CoordinatorAgent:
    """
    Coordinates all player injury analyses and produces a summarized
    team-wide injury report for a given week.
    """

    def __init__(self, llm, retriever_client):
        self.llm = llm
        self.injury_agent = InjuryAgent(llm, retriever_client)

        # Default starting lineup (you can update dynamically)
        self.starting_players = [
            # Offense
            "Lamar Jackson", "Zay Flowers", "Mark Andrews", "Rashod Bateman",
            "Justice Hill", "Ronnie Stanley", "Kevin Zeitler", "Tyler Linderbaum",
            "Morgan Moses", "Patrick Mekari", "Isaiah Likely",
            # Defense
            "Roquan Smith", "Patrick Queen", "Kyle Hamilton", "Marlon Humphrey",
            "Marcus Williams", "Jadeveon Clowney", "Odafe Oweh", "Justin Madubuike",
            "Michael Pierce", "Brandon Stephens", "Arthur Maulet"
        ]





    def save_weekly_report_to_db(self, week_number: int, report_text: str):
        """
        Store the generated weekly report in a table `injury_reports`.
        Creates the table if it doesn't exist.
        """
        # Create table using db.execute_query()
        self.db.execute_query("""
            CREATE TABLE IF NOT EXISTS injury_reports (
                id SERIAL PRIMARY KEY,
                week_number INTEGER,
                report_text TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Insert report
        self.db.execute_query(
            """
            INSERT INTO injury_reports (week_number, report_text, created_at)
            VALUES (%s, %s, %s)
            """,
            (week_number, report_text, datetime.now())
        )

    def get_past_report(self, week_number: int):
        """
        Retrieve a previously generated weekly injury report from the database.
        """
        result = self.db.execute_query(
            "SELECT report_text FROM injury_reports WHERE week_number = %s ORDER BY created_at DESC LIMIT 1",
            (week_number,)
        )
        return result[0][0] if result else None
