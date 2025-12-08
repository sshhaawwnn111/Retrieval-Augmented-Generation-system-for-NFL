import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import torch

class PGVectorRetriever:
    def __init__(self, table: str = "nfl_news", embed_col: str = "embedding"):
        self.table = table
        self.embed_col = embed_col
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(
            os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2"),
            device=device
        )

    def embed(self, text: str) -> str:
        vec = self.model.encode(text, normalize_embeddings=True).tolist()
        return f"[{','.join(str(x) for x in vec)}]"

    def search(self, db, query: str, k: int = 20, filters: Optional[Dict] = None, sql_override: Optional[str] = None) -> List[Dict]:
        """
        Search using DatabaseConnection's execute_query method
        
        Args:
            db: DatabaseConnection instance
            query: Search query text
            k: Number of results to return
            filters: Optional dictionary of col:value pairs (e.g. {"player_name": "Lamar Jackson"})
            sql_override: Optional SQL query override
        """
        qvec = self.embed(query)

        if sql_override:
            sql_to_use = sql_override.strip()
            params = (qvec, k)
        else:
            # Build dynamic WHERE clause
            where_conditions = []
            filter_values = []
            if filters:
                for col, val in filters.items():
                    # Handle special date range filters mapping to the 'date' column
                    if col == "start_date":
                        where_conditions.append("date >= %s")
                        filter_values.append(val)
                    elif col == "end_date":
                        where_conditions.append("date <= %s")
                        filter_values.append(val)
                    else:
                        # Note: Ensure 'col' is a safe column name to prevent injection here if input is untrusted
                        # Simple validation to ensure col is just alphanumeric/underscores
                        if not col.replace("_", "").isalnum():
                            continue
                        where_conditions.append(f"{col} = %s")
                        filter_values.append(val)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            sql_to_use = self._default_query(where_clause)
            
            # Params order: vector, filter_values..., limit
            params = tuple([qvec] + filter_values + [k])

        # Use execute_query instead of raw cursor
        rows = db.execute_query(sql_to_use, params)

        results: List[Dict] = []
        for idx, r in enumerate(rows):
            doc_id = r[0]
            player = r[1] if len(r) > 1 else None
            headline = r[2] if len(r) > 2 else None
            date_val = r[3] if len(r) > 3 else None
            date = date_val.strftime("%Y-%m-%d %H:%M:%S") if date_val is not None else None
            notes = r[4] if len(r) > 4 else ""
            analysis = r[5] if len(r) > 5 else ""
            status = r[6] if len(r) > 6 else ""
            detail = r[7] if len(r) > 7 else ""
            row_num = r[9] if len(r) > 9 else idx + 1

            citation = f"[doc_{doc_id}]"

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
                    f"(Status: {status}, Detail: {detail}) "
                    f"\n\nNotes: {notes or ''}\nAnalysis: {analysis or ''}"
                )
            })

        return results
    
    def _default_query(self, where_clause: str = "") -> str:
        """Default SQL query for vector search"""
        return f"""
            WITH ranked AS (
                SELECT 
                    id, player_name, headline, date, notes, analysis,
                    injury_status, injury_detail,
                    {self.embed_col} <=> %s::vector AS distance
                FROM {self.table}
                {where_clause}
                ORDER BY distance
                LIMIT %s
            )
            SELECT *, ROW_NUMBER() OVER (ORDER BY distance) as row_num
            FROM ranked
        """