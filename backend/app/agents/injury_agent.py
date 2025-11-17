from app.agents.prompts.injury_prompt import INJURY_PROMPT


class InjuryAgent:
    def __init__(self, llm, db):
        self.llm = llm  # This is VLLMClient
        self.db = db
        self.conn = self.db.conn
        self.cursor = self.conn.cursor()

    def get_injury_data_from_query(self, query):
        # Extract player name from query (simplest approach)
        player_name = "Lamar Jackson"  # you can improve by NLP parsing the query
        
        self.cursor.execute(
            """
            SELECT player_name, headline, date, injury_status, injury_detail
            FROM nfl_news
            WHERE player_name ILIKE %s
            ORDER BY date DESC
            LIMIT 10
            """,
            (f"%{player_name}%",)
        )

        rows = self.cursor.fetchall()

        # Convert to list of dicts
        data = []
        for row in rows:
            data.append({
                "player_name": row[0],
                "headline": row[1],
                "date": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                "injury_status": row[3],
                "injury_detail": row[4]
            })

        return data

    async def analyze_injury(self, query):
        """
        Analyze injury using VLLMClient (async)
        """
        # Pull context from DB
        context_data = self.get_injury_data_from_query(query)

        if not context_data:
            context_text = "No recent news updates available."
        else:
            context_text = ""
            for item in context_data:
                context_text += (
                    f"{item['date']}: {item['headline']} "
                    f"(Status: {item['injury_status']}, Detail: {item['injury_detail']})\n"
                )

        # Use the PromptTemplate to build the prompt text
        prompt_text = INJURY_PROMPT.format(
            query=query,
            context=context_text
        )

        # Send to VLLMClient (using generate_text instead of invoke)
        result = await self.llm.generate_text(
            prompt=prompt_text,
            system_prompt="You are a professional NFL injury analyst.",
            temperature=0.7,
            max_tokens=512
        )
        
        return result