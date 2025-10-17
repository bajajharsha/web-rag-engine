from fastapi import Depends

from backend.usecases.url_usecase import UrlUsecase


class UrlController:
    """Controller for handling url-related requests"""

    def __init__(self, url_usecase: UrlUsecase = Depends(UrlUsecase)):
        self.url_usecase = url_usecase

    async def ingest_url(self, url: str):
        return await self.url_usecase.ingest_url(url)
