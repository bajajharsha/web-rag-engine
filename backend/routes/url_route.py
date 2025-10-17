from fastapi import APIRouter, Depends

from backend.controllers.url_controller import UrlController

router = APIRouter()


@router.post("/ingest-url")
async def ingest_url(
    url: str,
    url_controller: UrlController = Depends(UrlController),
):
    return await url_controller.ingest_url(url)
