from typing import Optional

from fastapi import Depends

from backend.usecases.query_usecase import QueryUsecase


class QueryController:
    def __init__(self, query_usecase: QueryUsecase = Depends(QueryUsecase)):
        self.query_usecase = query_usecase

    async def query_documents(
        self, request: str, session_id: Optional[str] = None, top_k: int = 5
    ):
        return await self.query_usecase.query_documents(request, session_id, top_k)
