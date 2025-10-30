import psycopg2
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

class PGVectorRetriever:
    def __init__(self, db_conn, table: str = "nfl_news", embed_col: str = "embedding"):
        self.conn = db_conn
        self.table = table
        self.embed_col = embed_col
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> str:
        vec = self.model.encode(text, normalize_embeddings=True).tolist()
        return f"[{','.join(str(x) for x in vec)}]"

    def extract_player_name(self, query: str) -> Optional[str]:
        """
        Extract player name by finding 2 consecutive capitalized words
        e.g. 'Lamar Jackson'
        """
        tokens = query.split()
        for i in range(len(tokens) - 1):
            if tokens[i][0].isupper() and tokens[i+1][0].isupper():
                return f"{tokens[i]} {tokens[i+1]}"
        return None

    def search(self, query: str, k: int = 5) -> List[Dict]:
        qvec = self.embed(query)

        # Try detecting player name
        player_name = self.extract_player_name(query)
        player_filter = f"%{player_name}%" if player_name else ""

        # Retrieve more candidates first → better recall
        fetch_k = max(k * 4, 20)

        sql = f"""
        WITH candidate_docs AS (
            SELECT
                id,
                player_name,
                headline,
                date,
                COALESCE(injury_status, '') AS injury_status,
                COALESCE(injury_detail, '') AS injury_detail,
                (embedding <-> %s::vector) AS distance,
                ROW_NUMBER() OVER (ORDER BY date DESC) AS row_num
            FROM {self.table}
            WHERE date > NOW() - INTERVAL '365 days'
              AND (%s = '' OR player_name ILIKE %s)
            ORDER BY embedding <-> %s::vector
            LIMIT %s
        )
        SELECT *
        FROM candidate_docs
        ORDER BY distance
        LIMIT %s;
        """

        with self.conn.cursor() as cur:
            cur.execute(
                sql,
                (qvec, player_name or "", player_filter, qvec, fetch_k, k)
            )
            rows = cur.fetchall()

        results = []
        for idx, r in enumerate(rows):
            doc_id = r[0]
            player = r[1]
            headline = r[2]
            date = r[3].strftime("%Y-%m-%d %H:%M:%S")
            status = r[4]
            detail = r[5]
            row_num = r[7]  # extracted row number from SQL

            citation = f"[ref_{idx+1} doc_{doc_id} row_{row_num}]"

            results.append({
                "doc_id": doc_id,
                "row_number": row_num,
                "player_name": player,
                "headline": headline,
                "date": date,
                "injury_status": status,
                "injury_detail": detail,
                "citation": citation,
                "context_text": (
                    f"{citation} {player}: {headline} on {date} "
                    f"(Status: {status}, Detail: {detail})"
                )
            })

        return results
