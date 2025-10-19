from fastapi import APIRouter, Depends, HTTPException

from backend.controllers.query_controller import QueryController

router = APIRouter()


@router.post("/query")
async def query_documents(
    request: str, query_controller: QueryController = Depends(QueryController)
):
    try:
        return await query_controller.query_documents(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
