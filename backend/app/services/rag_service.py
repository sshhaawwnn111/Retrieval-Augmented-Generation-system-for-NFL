"""
RAG (Retrieval-Augmented Generation) Service
Includes integrated agent classes for injury and performance analysis.
"""
import logging
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.vllm_client import llm_client
from app.core.config import settings

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------
# RAG SERVICE
# -----------------------------------------------------------------------------------

class RAGService:
    """RAG pipeline orchestration"""
    
    def __init__(self):
        self.reranker_url = f"{settings.RERANKER_SERVICE_URL}/rerank"
        self.top_k_retrieval = 20
        self.top_k_final = 5
        
    async def index_documents(
        self,
        documents: List[Dict[str, str]],
        source: str = "manual_upload"
    ) -> Dict[str, Any]:
        try:
            contents = [doc['content'] for doc in documents]
            logger.info(f"Generating embeddings for {len(contents)} documents...")
            embeddings = await embedding_service.embed_batch(contents)

            docs_to_insert = [
                {
                    'content': doc['content'],
                    'embedding': embeddings[i],
                    'metadata': doc.get('metadata', {}),
                    'source': source
                }
                for i, doc in enumerate(documents)
            ]
            logger.info(f"Inserting {len(docs_to_insert)} documents into vector store...")
            ids = await vector_store.insert_batch(docs_to_insert)
            
            return {'indexed_count': len(ids), 'source': source, 'document_ids': ids}
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    async def retrieve_and_rerank(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = await embedding_service.embed_text(query)
            logger.info(f"Retrieving top {self.top_k_retrieval} candidates...")
            candidates = await vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=self.top_k_retrieval,
                filters=filters
            )
            if not candidates:
                logger.warning("No candidates found for query")
                return []
            
            logger.info(f"Reranking {len(candidates)} documents...")
            reranked = await self._rerank_documents(query, candidates)
            final_k = top_k or self.top_k_final
            return reranked[:final_k]
            
        except Exception as e:
            logger.error(f"Error in retrieve_and_rerank: {e}")
            raise
    
    async def _rerank_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        try:
            rerank_docs = [
                {'content': doc['content'], 'source': doc.get('source'), 'metadata': doc.get('metadata')}
                for doc in documents
            ]
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.reranker_url,
                    json={'query': query, 'documents': rerank_docs, 'top_n': len(documents)}
                )
                response.raise_for_status()
                result = response.json()
            return result.get('reranked_documents', documents)
            
        except Exception as e:
            logger.warning(f"Reranking failed, returning original order: {e}")
            return documents
    
    async def generate_with_context(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        try:
            relevant_docs = await self.retrieve_and_rerank(query=query, filters=filters)
            if not relevant_docs:
                return {
                    'generated_text': "I don't have enough information to answer that question.",
                    'sources': [],
                    'context_used': False
                }
            
            context_parts = [
                f"[Source {i}] {doc['content']}\n(Source: {doc.get('source', 'unknown')})"
                for i, doc in enumerate(relevant_docs, 1)
            ]
            context = "\n\n".join(context_parts)
            
            augmented_prompt = f"""Based on the following context, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
            
            generated_text = await llm_client.generate_text(
                prompt=augmented_prompt,
                system_prompt=system_prompt or "You are a helpful NFL analytics assistant. Answer questions based on the provided context. If you're not sure, say so.",
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return {
                'generated_text': generated_text,
                'sources': [
                    {'content': doc['content'][:200] + '...', 'source': doc.get('source'), 'score': doc.get('score')}
                    for doc in relevant_docs
                ],
                'context_used': True
            }
            
        except Exception as e:
            logger.error(f"Error in RAG generation: {e}")
            raise


# Global instance
rag_service = RAGService()

# -----------------------------------------------------------------------------------
# INJURY AGENT
# -----------------------------------------------------------------------------------

from llm.prompts.injury_prompt import injury_prompt_template

class InjuryAgent:
    """Agent for analyzing player injuries using recent news data."""

    def __init__(self, llm, db):
        self.llm = llm
        self.db = db
        self.conn = self.db.conn
        self.cursor = self.conn.cursor()

    def get_injury_data_from_query(self, query):
        player_name = "Lamar Jackson"  # TODO: NLP-based name extraction
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
        return [
            {
                "player_name": r[0],
                "headline": r[1],
                "date": r[2].strftime("%Y-%m-%d %H:%M:%S"),
                "injury_status": r[3],
                "injury_detail": r[4],
            }
            for r in rows
        ]

    def analyze_injury(self, query):
        context_data = self.get_injury_data_from_query(query)
        if not context_data:
            context_text = "No recent news updates available."
        else:
            context_text = "\n".join(
                f"{item['date']}: {item['headline']} "
                f"(Status: {item['injury_status']}, Detail: {item['injury_detail']})"
                for item in context_data
            )

        prompt_text = injury_prompt_template.format(query=query, context=context_text)
        result = self.llm.invoke([HumanMessage(content=prompt_text)])
        return result.content


# -----------------------------------------------------------------------------------
# PERFORMANCE AGENT
# -----------------------------------------------------------------------------------

performance_prompt_str = """
You are a sports analytics expert for the Baltimore Ravens, focused on weekly player and team performance.

CONTEXT DATA:
{context}

TASK: Analyze the data and provide an in-depth performance summary for {query}.

REQUIRED OUTPUT FORMAT:
1. **Team Summary**: Overall team performance and key metrics (offense, defense, efficiency)
2. **Top Performers**: Highlight standout players and stats
3. **Areas for Improvement**: Notable weaknesses or risks
4. **Analyst Insights**: Data-driven commentary or suggestions
"""

performance_prompt_template = PromptTemplate(
    input_variables=["context", "query"],
    template=performance_prompt_str
)


class PerformanceAgent:
    """Agent for analyzing team and player performance."""

    def __init__(self, llm, database_connection=None, data_dir="data"):
        self.llm = llm
        self.db = database_connection
        self.chain = performance_prompt_template | llm
        self.data_dir = Path(data_dir)

    def _load_performance_data(self, filename="test_report.json"):
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Performance file not found: {path}")
        with open(path, "r") as f:
            return json.load(f)

    def _fetch_player_data(self, player_name=None):
        if not self.db:
            return None
        try:
            conn = self.db.conn if hasattr(self.db, "conn") else self.db
            cursor = conn.cursor()
            if player_name:
                cursor.execute(
                    """
                    SELECT name, position, team, stats
                    FROM ravens.players
                    WHERE name ILIKE %s;
                    """,
                    (player_name,),
                )
            else:
                cursor.execute("SELECT name, position, team, stats FROM ravens.players;")
            rows = cursor.fetchall()
            cursor.close()
            return [
                {"name": r[0], "position": r[1], "team": r[2], "stats": r[3]} for r in rows
            ]
        except Exception as e:
            print(f"Database fetch failed: {e}")
            return None

    def analyze_performance(self, query: str):
        report_data = self._load_performance_data()
        db_data = self._fetch_player_data()
        context = {
            "report_summary": report_data.get("summary"),
            "metrics": report_data.get("metrics"),
            "players": report_data.get("players"),
            "notes": report_data.get("notes"),
            "db_players": db_data,
        }
        context_str = json.dumps(context, indent=2)
        result = self.chain.invoke({"context": context_str, "query": query})
        return result