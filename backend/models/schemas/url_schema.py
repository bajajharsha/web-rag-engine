from pydantic import BaseModel, HttpUrl


class UrlRequest(BaseModel):
    """Request model for URL ingestion"""

    url: HttpUrl
