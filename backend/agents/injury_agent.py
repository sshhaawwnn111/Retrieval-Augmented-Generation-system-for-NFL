# backend/agents/injury_agent.py
import sys
import os
from langchain_core.messages import HumanMessage

# Add the project root to Python path (go up from backend to RavensRotoWire)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from llm.prompts.injury_prompt import injury_prompt_template

# backend/agents/injury_agent.py
class InjuryAgent:
    def __init__(self, llm, db):
        self.llm = llm
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

    
    def analyze_injury(self, query):
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
        prompt_text = injury_prompt_template.format(
            query=query,
            context=context_text
        )

        # Send to model
        result = self.llm.invoke([HumanMessage(content=prompt_text)])
        return result.content