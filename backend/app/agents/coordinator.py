# backend/app/agents/coordinator_agent.py
from datetime import datetime
from app.agents.injury_agent import InjuryAgent

class CoordinatorAgent:
    """
    Coordinates all player injury analyses and produces a summarized
    team-wide injury report for a given week.
    """

    def __init__(self, llm, db, retriever, reranker):
        self.llm = llm
        self.db = db
        self.injury_agent = InjuryAgent(llm, db, retriever, reranker)

        # Default starting lineup (customize as needed)
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

    async def generate_weekly_report(self, week_number: int):
        """
        Run injury analysis for all starting players for a given week.
        """

        report_lines = []

        for player in self.starting_players:
            query = f"{player} injury status week {week_number}"
            try:
                analysis = await self.injury_agent.analyze_injury(query)
                summary = await self.summarize_injury_sentence(player, analysis)
                report_lines.append(summary)
            except Exception as e:
                report_lines.append(f"{player}: Error fetching data ({str(e)})")

        return "\n".join(report_lines)

    async def summarize_injury_sentence(self, player_name: str, analysis_text: str) -> str:
        """
        Summarize detailed analysis into one concise sentence.
        """

        summarization_prompt = f"""
        Summarize the following injury analysis for {player_name} into one concise sentence.
        Include status, expected availability, and recovery outlook.

        Injury Analysis:
        {analysis_text}
        """

        result = await self.llm.generate_text(
            prompt=summarization_prompt,
            system_prompt="You are a professional NFL injury analyst.",
            temperature=0.3,
            max_tokens=128
        )

        return f"{player_name}: {result.content.strip()}"

    def save_weekly_report_to_db(self, week_number: int, report_text: str):
        self.db.execute_query("""
            CREATE TABLE IF NOT EXISTS injury_reports (
                id SERIAL PRIMARY KEY,
                week_number INTEGER,
                report_text TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        self.db.execute_query(
            """
            INSERT INTO injury_reports (week_number, report_text, created_at)
            VALUES (%s, %s, %s)
            """,
            (week_number, report_text, datetime.now())
        )

    def get_past_report(self, week_number: int):
        result = self.db.execute_query(
            "SELECT report_text FROM injury_reports WHERE week_number = %s ORDER BY created_at DESC LIMIT 1",
            (week_number,)
        )
        return result[0][0] if result else None
