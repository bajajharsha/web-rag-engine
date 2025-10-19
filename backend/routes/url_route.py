from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from backend.controllers.url_controller import UrlController
from backend.models.schemas.url_schema import UrlRequest

router = APIRouter()


@router.post("/ingest-url", status_code=status.HTTP_202_ACCEPTED)
async def ingest_url(
    url_request: UrlRequest,
    url_controller: UrlController = Depends(UrlController),
):
    """
    Ingest a URL for processing

    Returns:
        HTTP 202 Accepted - URL has been queued for processing
    """
    try:
        print(f"URL Route: {url_request.url}")
        result = await url_controller.ingest_url(url_request.url)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error occurred", "error": str(e)},
        )
