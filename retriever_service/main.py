import os
import logging
import torch
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from db_connection import DatabaseConnection
from contextlib import asynccontextmanager
from core.config import settings
from core.secrets import get_database_credentials

from schemas import (
    RetrievedDocument,
    Document,
    RetrieveRequest,
    RetrieveAndRerankRequest,
    RetrieveAndRerankResponse,
)
from retriever import PGVectorRetriever
from reranker import ModelReranker
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db(use_writer: bool = False):
    """
    Dependency to get database connection
    
    Args:
        use_writer: If True, returns writer connection for write operations
    """
    db = DatabaseConnection(use_writer=use_writer)
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting RavensRotoWire retriever...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    
    # Log GPU availability
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA device count: {torch.cuda.device_count()}")

    # Get database credentials - start with settings defaults
    db_password = settings.DATABASE_PASSWORD
    db_user = settings.DATABASE_USER
    db_host = settings.DATABASE_HOST
    db_reader_host = settings.DATABASE_READER_HOST
    
    if settings.USE_SECRETS_MANAGER:
        try:
            logger.info(f"Retrieving database credentials from Secrets Manager: {settings.DATABASE_SECRET_NAME}")
            credentials = get_database_credentials(
                secret_name=settings.DATABASE_SECRET_NAME,
                region=settings.AWS_REGION
            )
            
            # RDS-managed secrets only contain username and password
            db_user = credentials.get('username', db_user)
            db_password = credentials.get('password', db_password)
            
            logger.info(f"Successfully retrieved database credentials for user: {db_user}")
            
        except Exception as e:
            logger.error(f"Failed to retrieve secrets from Secrets Manager: {e}")
            logger.warning("Falling back to environment variables")
    # Initialize database connection pools
    try:
        DatabaseConnection.initialize_pools(
            dbname=settings.DATABASE_NAME,
            user=db_user,
            password=db_password,
            writer_host=db_host,  # Cluster/Writer endpoint
            reader_host=db_reader_host,  # Reader endpoint
            port=settings.DATABASE_PORT,
            min_conn=2,
            max_conn=10
        )
        logger.info("Database connection pools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pools: {e}")
        raise
    
    logger.info("Starting retriever_reranker service")
    try:
        app.state.retriever = PGVectorRetriever()
        app.state.reranker = ModelReranker(os.environ.get("RERANK_MODEL", "zeroentropy/zerank-1-small"))
        logger.info("Services initialized")
    except Exception as e:
        logger.exception("Failed to initialize service: %s", e)
        raise


    yield
    

    logger.info("Shutting down retriever_reranker service")
    try:
        if hasattr(app.state, "db") and app.state.db:
            app.state.db.close()
    except Exception:
        logger.exception("Error closing DB connection")
        
    # Shutdown
    logger.info("Shutting down RavensRotoWire Backend...")
    try:
        DatabaseConnection.close_all_connections()
        logger.info("Database connection pools closed successfully")
    except Exception as e:
        logger.error(f"Error closing database pools: {e}")


app = FastAPI(
    title="Retriever + Reranker Service",
    description="Service for retrieving and reranking documents using PGVector and a reranker model",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "retriever_reranker"}

@app.post("/retrieve", response_model=List[Document])
def retrieve(req: RetrieveRequest, db: DatabaseConnection = Depends(get_db) ):
    try:
        candidates = app.state.retriever.search(
            db,
            req.query,
            k=req.k,
        )

        docs_for_rerank: List[Document] = []
        for d in candidates:
            meta = {
                "doc_id": d.get("doc_id"),
                "headline": d.get("headline"),
                "date": d.get("date"),
                "citation": d.get("citation"),
            }
            docs_for_rerank.append(
                Document(content=d.get("context_text", ""), metadata=meta)
            )

        return docs_for_rerank

    except Exception as e:
        logger.exception("Retrieve failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rerank", response_model=List[RetrievedDocument])
def rerank(query_and_docs: dict):
    """
    Expected payload:
    {
        "query": "...",
        "documents": [ {content, metadata}, ... ],
        "top_n": 5
    }
    """
    try:
        query = query_and_docs["query"]
        docs = query_and_docs["documents"]
        top_n = query_and_docs.get("top_n", len(docs))

        # Convert input docs into Document objects
        docs_for_rerank = [
            Document(content=d["content"], metadata=d.get("metadata", {}))
            for d in docs
        ]

        reranked = app.state.reranker.rerank_documents(
            query,
            docs_for_rerank,
            top_n
        )

        response_docs: List[RetrievedDocument] = []
        for doc in reranked:
            meta = doc.metadata or {}
            response_docs.append(
                RetrievedDocument(
                    doc_id=meta.get("doc_id"),
                    row_number=meta.get("row_number"),
                    player_name=meta.get("player_name"),
                    headline=meta.get("headline"),
                    date=meta.get("date"),
                    citation=meta.get("citation") or "",
                    context_text=doc.content,
                )
            )

        return response_docs

    except Exception as e:
        logger.exception("Rerank failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve_and_rerank", response_model=RetrieveAndRerankResponse)
def retrieve_and_rerank(req: RetrieveAndRerankRequest, db: DatabaseConnection = Depends(get_db)):
    try:
        logger.info(f"Retrieve and rerank request - query: '{req.query[:100]}...', k={req.k}, top_n={req.top_n}")
        # 1. retrieval
        logger.info(f"Starting retrieval with k={req.k}")
        candidates = app.state.retriever.search(
            db, 
            req.query, 
            k=req.k,
        )
        logger.info(f"Retrieved {len(candidates)} candidates from database")

        docs_for_rerank: List[Document] = []
        for d in candidates:
            meta = {
                "doc_id": d.get("doc_id"),
                "row_number": d.get("row_number"),
                "player_name": d.get("player_name"),
                "headline": d.get("headline"),
                "date": d.get("date"),
                "citation": d.get("citation"),
                "injury_status": d.get("injury_status"),
                "injury_detail": d.get("injury_detail"),
            }
            docs_for_rerank.append(Document(content=d.get("context_text", ""), metadata=meta))

        logger.info(f"Prepared {len(docs_for_rerank)} documents for reranking")


        # 2. reranking
        top_n = req.top_n if req.top_n is not None else req.k
        reranked = app.state.reranker.rerank_documents(req.query, docs_for_rerank, top_n)
        logger.info(f"Reranking complete, returning {len(reranked)} documents")

        # 3. Marshal response
        response_docs: List[RetrievedDocument] = []
        for doc in reranked:
            meta = doc.metadata or {}
            response_docs.append(
                RetrievedDocument(
                    doc_id=meta.get("doc_id"),
                    row_number=meta.get("row_number"),
                    player_name=meta.get("player_name"),
                    headline=meta.get("headline"),
                    date=meta.get("date"),
                    injury_status=meta.get("injury_status"),
                    injury_detail=meta.get("injury_detail"),
                    citation=meta.get("citation") or "",
                    context_text=doc.content,
                )
            )

        logger.info(f"Successfully marshaled {len(response_docs)} response documents")
        return RetrieveAndRerankResponse(documents=response_docs)

    except Exception as e:
        logger.exception("Retrieve+Rerank failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False
    )
