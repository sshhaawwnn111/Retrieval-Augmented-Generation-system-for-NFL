import os
import logging
from typing import List

from fastapi import FastAPI, HTTPException
import psycopg2

from .schemas import (
    RetrieveRequest,
    RetrieveResponse,
    RetrievedDocument,
    RerankRequest,
    RerankResponse,
    Document,
    RetrieveAndRerankRequest,
    RetrieveAndRerankResponse,
)
from .retriever import PGVectorRetriever
from .reranker import ModelReranker
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Retriever + Reranker Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    params = {
        "dbname": os.environ.get("PGDATABASE", "postgres"),
        "user": os.environ.get("PGUSER", "postgres"),
        "password": os.environ.get("PGPASSWORD", ""),
        "host": os.environ.get("PGHOST", "localhost"),
        "port": os.environ.get("PGPORT", "5432"),
    }
    return psycopg2.connect(**params)


@app.on_event("startup")
def startup_event():
    logger.info("Starting retriever_reranker service")
    try:
        app.state.db = get_db_connection()
        app.state.retriever = PGVectorRetriever(app.state.db)
        app.state.reranker = ModelReranker(os.environ.get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L6-v2"))
        logger.info("Services initialized")
    except Exception as e:
        logger.exception("Failed to initialize service: %s", e)
        raise


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down retriever_reranker service")
    try:
        if hasattr(app.state, "db") and app.state.db:
            app.state.db.close()
    except Exception:
        logger.exception("Error closing DB connection")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "retriever_reranker"}


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(req: RetrieveRequest):
    try:
        docs = app.state.retriever.search(req.query, k=req.k, sql_override=req.sql)
        pdocs: List[RetrievedDocument] = [RetrievedDocument(**d) for d in docs]
        return RetrieveResponse(documents=pdocs)
    except Exception as e:
        logger.exception("Retrieve failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rerank", response_model=RerankResponse)
def rerank(req: RerankRequest):
    try:
        reranked = app.state.reranker.rerank_documents(req.query, [Document(**d.dict()) for d in req.documents], req.top_n or 3)
        return RerankResponse(reranked_documents=reranked)
    except Exception as e:
        logger.exception("Rerank failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve_and_rerank", response_model=RetrieveAndRerankResponse)
def retrieve_and_rerank(req: RetrieveAndRerankRequest):
    try:
        candidates = app.state.retriever.search(req.query, k=req.k, sql_override=req.sql)
        docs_for_rerank: List[Document] = []
        for d in candidates:
            meta = {
                "doc_id": d.get("doc_id"),
                "row_number": d.get("row_number"),
                "player_name": d.get("player_name"),
                "headline": d.get("headline"),
                "date": d.get("date"),
                "injury_status": d.get("injury_status"),
                "injury_detail": d.get("injury_detail"),
                "citation": d.get("citation"),
            }
            docs_for_rerank.append(Document(content=d.get("context_text", ""), metadata=meta))

        top_n = req.top_n if req.top_n is not None else req.k

        reranked = app.state.reranker.rerank_documents(req.query, docs_for_rerank, top_n)

        response_docs: List[RetrievedDocument] = []
        for doc in reranked:
            meta = doc.metadata or {}
            response_docs.append(RetrievedDocument(
                doc_id=meta.get("doc_id"),
                row_number=meta.get("row_number"),
                player_name=meta.get("player_name"),
                headline=meta.get("headline"),
                date=meta.get("date"),
                injury_status=meta.get("injury_status"),
                injury_detail=meta.get("injury_detail"),
                citation=meta.get("citation") or "",
                context_text=doc.content,
            ))

        return RetrieveAndRerankResponse(documents=response_docs)
    except Exception as e:
        logger.exception("Retrieve+Rerank failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    
# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host=settings.service_host,
#         port=settings.service_port,
#         log_level=settings.log_level.lower(),
#         reload=False
#     )

