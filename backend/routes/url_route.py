from fastapi import APIRouter, Depends, HTTPException

from backend.controllers.url_controller import UrlController
from backend.models.schemas.url_schema import UrlRequest

router = APIRouter()


@router.post("/ingest-url")
async def ingest_url(
    url_request: UrlRequest,
    url_controller: UrlController = Depends(UrlController),
):
    try:
        print(f"URL Route: {url_request.url}")
        result = await url_controller.ingest_url(url_request.url)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error occurred", "error": str(e)},
        )
