from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "web-rag-engine"

    class Config:
        env_file = ".env"


settings = Settings()
