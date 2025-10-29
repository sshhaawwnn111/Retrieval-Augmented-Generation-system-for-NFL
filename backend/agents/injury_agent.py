# backend/agents/injury_agent.py
import sys
import os
from langchain_core.messages import HumanMessage

# Add the project root to Python path (go up from backend to RavensRotoWire)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from llm.prompts.injury_prompt import injury_prompt_template
    print("✅ Loaded injury prompt from llm module")
except ImportError as e:
    print(f"❌ Failed to import from llm module: {e}")
    print(f"🔍 Python path: {sys.path}")
    # Fallback: define the prompt directly
    from langchain_core.prompts import PromptTemplate
    injury_prompt_str = """
    You are a medical and sports analytics expert specializing in NFL player injuries.

    CONTEXT DATA:
    {context}

    TASK: Analyze injury data for: {query}

    OUTPUT FORMAT:
    1. **Current Status**: Injury designation and timeline
    2. **Medical Analysis**: Injury type and recovery period  
    3. **Impact Assessment**: Team performance implications

    CONTEXT: {context}
    QUERY: {query}
    """
    
    injury_prompt_template = PromptTemplate(
        input_variables=["query", "context"],
        template=injury_prompt_str
    )

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
        context_data = self.get_injury_data_from_query("Lamar Jackson")

        if not context_data:
            context_text = "No recent news updates available."
        else:
            context_text = ""
            for item in context_data:
                context_text += f"{item['date']}: {item['headline']} (Status: {item['injury_status']}, Detail: {item['injury_detail']})\n"

        prompt = f"""
        You are an NFL injury analyst.
        Here is the context about the player from Rotowire database:
        {context_text}

        Question: {query}
        Provide a detailed injury update based on the context.
        """

        # ✅ Simpler and correct
        result = self.llm.invoke([HumanMessage(content=prompt)])
        return result.content