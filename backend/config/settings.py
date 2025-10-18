from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "web-rag-engine"
    MONGODB_URLS_COLLECTION: str = "urls"

    # Redis settings
    REDIS_URL: str = "redis://default:pS2UuGNOEjxjBHNSDAS1lAtT5Abaicol@redis-13543.c232.us-east-1-2.ec2.redns.redis-cloud.com:13543"
    REDIS_DB: int = 0
    REDIS_QUEUE_NAME: str = "url_processing_queue"

    # Firecrawl settings
    FIRECRAWL_API_URL: str = "https://api.firecrawl.dev/v2/scrape"
    FIRECRAWL_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
