from fastapi import APIRouter, Depends, HTTPException

from backend.controllers.query_controller import QueryController
from backend.models.schemas.query_schema import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest, query_controller: QueryController = Depends(QueryController)
):
    try:
        result = await query_controller.query_documents(request.query, request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
