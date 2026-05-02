import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    DATABASE_URL: str
    REDIS_URL: str
    FAISS_INDEX_PATH: str = "faiss_index"

    class Config:
        env_file = ".env.docker"  # local fallback only

settings = Settings()