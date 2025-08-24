# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AdrianaBrill AI Service"

    OPENAI_API_KEY: str
    
    HOST: str = "0.0.0.0"
    PORT: int = 8085
    
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    PRODUCT_API_BASE_URL: str = "https://fzjn9pz1-5101.inc1.devtunnels.ms/api/v1/products"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()