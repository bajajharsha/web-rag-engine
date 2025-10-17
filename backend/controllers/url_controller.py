from typing import Any, Dict

from fastapi import Depends, HTTPException
from pydantic import HttpUrl

from backend.usecases.url_usecase import UrlUsecase


class UrlController:
    """Controller for handling url-related requests"""

    def __init__(self, url_usecase: UrlUsecase = Depends(UrlUsecase)):
        self.url_usecase = url_usecase

    async def ingest_url(self, url: HttpUrl) -> Dict[str, Any]:
        try:
            print(f"URL Controller: {url}")
            result = await self.url_usecase.ingest_url(url)
            return {"status": "success", "data": result}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Internal server error during URL processing",
                    "error": str(e),
                },
            )
