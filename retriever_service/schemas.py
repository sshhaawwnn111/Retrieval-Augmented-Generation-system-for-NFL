from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RetrieveRequest(BaseModel):
    query: str
    k: Optional[int] = 5


class RetrievedDocument(BaseModel):
    doc_id: int
    row_number: Optional[int] = None
    player_name: Optional[str] = None
    headline: Optional[str] = None
    date: Optional[str] = None
    injury_status: Optional[str] = None
    injury_detail: Optional[str] = None
    citation: str
    context_text: str


class RetrieveResponse(BaseModel):
    documents: List[RetrievedDocument]


class Document(BaseModel):
    content: str
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RerankRequest(BaseModel):
    query: str
    documents: List[Document]
    top_n: Optional[int] = 3


class RerankResponse(BaseModel):
    reranked_documents: List[Document]


class RetrieveAndRerankRequest(BaseModel):
    query: str
    k: Optional[int] = 20
    sql: Optional[str] = None
    top_n: Optional[int] = 5


class RetrieveAndRerankResponse(BaseModel):
    documents: List[RetrievedDocument]
