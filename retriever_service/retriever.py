import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer


class PGVectorRetriever:
    def __init__(self, table: str = "nfl_news", embed_col: str = "embedding"):
        self.table = table
        self.embed_col = embed_col
        self.model = SentenceTransformer(os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2"))

    def embed(self, text: str) -> str:
        vec = self.model.encode(text, normalize_embeddings=True).tolist()
        return f"[{','.join(str(x) for x in vec)}]"

    def search(self, db, query: str, k: int = 20, sql_override: Optional[str] = None) -> List[Dict]:
        """
        Search using DatabaseConnection's execute_query method
        
        Args:
            db: DatabaseConnection instance
            query: Search query text
            k: Number of results to return
            sql_override: Optional SQL query override
        """
        qvec = self.embed(query)

        sql_to_use = self._default_query() if not sql_override else sql_override.strip()
        params = (qvec, k)

        # Use execute_query instead of raw cursor
        rows = db.execute_query(sql_to_use, params)

        results: List[Dict] = []
        for idx, r in enumerate(rows):
            doc_id = r[0]
            player = r[1] if len(r) > 1 else None
            headline = r[2] if len(r) > 2 else None
            date_val = r[3] if len(r) > 3 else None
            date = date_val.strftime("%Y-%m-%d %H:%M:%S") if date_val is not None else None
            status = r[4] if len(r) > 4 else ""
            detail = r[5] if len(r) > 5 else ""
            row_num = r[7] if len(r) > 7 else idx + 1

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
                    f"{citation} {player or ''}: {headline or ''} on {date or ''} "
                    f"(Status: {status}, Detail: {detail})"
                )
            })

        return results
    
    def _default_query(self) -> str:
        """Default SQL query for vector search"""
        return f"""
            WITH ranked AS (
                SELECT 
                    id, player_name, headline, date, 
                    injury_status, injury_detail,
                    {self.embed_col} <=> %s::vector AS distance
                FROM {self.table}
                ORDER BY distance
                LIMIT %s
            )
            SELECT *, ROW_NUMBER() OVER (ORDER BY distance) as row_num
            FROM ranked
        """