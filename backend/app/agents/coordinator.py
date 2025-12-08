# backend/agents/coordinator_agent.py
from datetime import datetime
import logging

from app.agents.injury_agent import InjuryAgent
from app.agents.waiver_agent import WaiverAgent
from app.agents.news_agent import NewsAgent
from app.agents.performance_agent import PerformanceAgent

logger = logging.getLogger(__name__)



logger = logging.getLogger(__name__)
class CoordinatorAgent:
    """
    Coordinates all player-focused analysis across injuries, waiver transactions,
    off-field news, and weekly performance. Produces unified team-wide summaries
    for weekly reporting.
    """

    def __init__(self, llm, retriever_client, db=None):
        self.llm = llm
        self.db = db

        # Sub-agents
        self.injury_agent = InjuryAgent(llm, retriever_client)
        self.waiver_agent = WaiverAgent(llm, retriever_client)
        self.news_agent = NewsAgent(llm, retriever_client)
        self.performance_agent = PerformanceAgent(llm, retriever_client)

        # Default starting lineup (can be dynamically updated)
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

    # -------------------------------------------------------------------------
    # MAIN WEEKLY REPORT
    # -------------------------------------------------------------------------

    async def generate_full_weekly_report(self, week_number: int):
        """
        Calls all sub-agents (injury, waiver, news, performance) and composes
        a unified weekly report for front-office use.
        """

        injuries = await self.injury_agent.generate_team_injury_report(self.starting_players)
        waivers = await self.waiver_agent.generate_waiver_report(self.starting_players)
        news_items = await self.news_agent.generate_news_report(self.starting_players)
        performance = await self.performance_agent.generate_performance_report(self.starting_players)

        report_prompt = f"""
        Produce a polished, executive-ready NFL team operations report for Week {week_number}.
        Structure the response in four sections:

        1. Injury Report:
           {injuries}

        2. Waiver & Contract Moves:
           {waivers}

        3. Off-Field News & Behavior:
           {news_items}

        4. Weekly Performance Assessment:
           {performance}

        Final output should be concise, professional, and ready for a GM or coaching staff briefing.
        """
        final_report = await self.llm.generate_text(
            prompt=report_prompt,
            system_prompt="You are a professional NFL team operations analyst.",
            temperature=0.3,
            max_tokens=512
        )

        if self.db:
            self.save_weekly_report_to_db(week_number, final_report)

        return final_report

    # -------------------------------------------------------------------------
    # DATABASE STORAGE
    # -------------------------------------------------------------------------

    def save_weekly_report_to_db(self, week_number: int, report_text: str):
        """
        Store the generated weekly report in table `team_reports`.
        Creates the table if it does not exist.
        """
        self.db.execute_query("""
            CREATE TABLE IF NOT EXISTS team_reports (
                id SERIAL PRIMARY KEY,
                week_number INTEGER,
                report_text TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        self.db.execute_query(
            """
            INSERT INTO team_reports (week_number, report_text, created_at)
            VALUES (%s, %s, %s)
            """,
            (week_number, report_text, datetime.now())
        )

    def get_past_report(self, week_number: int):
        """
        Retrieve the most recent weekly report from the database.
        """
        result = self.db.execute_query(
            """
            SELECT report_text
            FROM team_reports
            WHERE week_number = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (week_number,)
        )
        return result[0][0] if result else None
