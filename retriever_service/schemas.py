from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class RetrieveRequest(BaseModel):
    query: str
    k: Optional[int] = 5
<<<<<<< HEAD
=======
    filters: Optional[Dict[str, str]] = None
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86


class RetrievedDocument(BaseModel):
    doc_id: int
<<<<<<< HEAD
    row_number: int
    player_name: Optional[str]
    headline: Optional[str]
    date: Optional[str]
    injury_status: Optional[str]
    injury_detail: Optional[str]
=======
    row_number: Optional[int] = None
    player_name: Optional[str] = None
    headline: Optional[str] = None
    date: Optional[str] = None
    injury_status: Optional[str] = None
    injury_detail: Optional[str] = None
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86
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
<<<<<<< HEAD
=======
    filters: Optional[Dict[str, str]] = None
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86


class RetrieveAndRerankResponse(BaseModel):
    documents: List[RetrievedDocument]
