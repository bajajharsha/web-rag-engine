from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class SourceCitation(BaseModel):
    chunk_id: str
    url: str
    content: str
    score: float
    metadata: dict


class QueryResponse(BaseModel):
    answer: str
    sources: list
    query: str
