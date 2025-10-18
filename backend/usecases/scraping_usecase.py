import json

from backend.config.settings import settings
from backend.services.api_service import ApiService


class ScrapingUsecase:
    def __init__(self):
        self.api_service = ApiService()

    async def scrape_url(self, url: str):
        # Use firecrawl to scrape the url
        print("***************************************")
        print(f"Scraping URL: {url}")
        try:
            response = await self.api_service.post(
                url=settings.FIRECRAWL_API_URL,
                headers={"Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}"},
                data={"url": url, "formats": ["markdown", "html"]},
            )
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return None

        with open("response.json", "w") as f:
            json.dump(response, f)
        return response.get("data").get("markdown")
