# backend/agents/coordinator_agent.py
from datetime import datetime

from app.agents.injury_agent import InjuryAgent

class CoordinatorAgent:
    """
    Coordinates all player injury analyses and produces a summarized
    team-wide injury report for a given week.
    """

    def __init__(self, llm, db):
        self.llm = llm
        self.db = db
        self.injury_agent = InjuryAgent(llm, db)

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

    def generate_weekly_report(self, week_number: int):
        """
        Generate a one-sentence injury summary for each starting player for the given week.
        Combines them into a single team report.
        """

        full_report = []
        for player in self.starting_players:
            query = f"{player} injury status week {week_number}"
            try:
                analysis = self.injury_agent.analyze_injury(query)
                summary_sentence = self.summarize_injury_sentence(player, analysis)
                full_report.append(summary_sentence)
            except Exception as e:
                full_report.append(f"{player}: Data unavailable ({str(e)})")

        # Combine into one full report
        report_text = "\n".join(full_report)

        # Save to DB for tracking historical reports
        # self.save_weekly_report_to_db(week_number, report_text)

        return report_text

    async def summarize_injury_sentence(self, player_name: str, analysis_text: str) -> str:
        """
        Summarize the LLM's injury analysis into one sentence per player.
        Uses the LLM to condense the analysis into a concise statement.
        """

        summarization_prompt = f"""
        Summarize the following injury analysis for {player_name} into one concise sentence.
        The summary should clearly state their current injury status, recovery outlook,
        and whether they are expected to play in the given week.

        Injury Analysis:
        {analysis_text}
        """

        result = await self.llm.generate_text(
            prompt=summarization_prompt,
            system_prompt="You are a professional NFL injury analyst.",
            temperature=0.7,
            max_tokens=512
        )
        return f"{player_name}: {result.content.strip()}"

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
