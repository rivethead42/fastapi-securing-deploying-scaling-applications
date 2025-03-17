import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Widget API"
    
    # MongoDB settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = "widget_db"
    
    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-please-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings - we'll configure this in code instead of from env
    CORS_ORIGINS_STR: Optional[str] = None
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_MAX_AGE: int = 600
    
    # Rate limiting settings
    RATE_LIMIT_ANON_REQUESTS: int = Field(default=30)
    RATE_LIMIT_AUTH_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)
    
    # Configure settings behavior
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    @property
    def CORS_ALLOW_ORIGINS(self) -> List[str]:
        """Get CORS allowed origins from environment or default"""
        origins_str = self.CORS_ORIGINS_STR or os.getenv(
            "CORS_ALLOW_ORIGINS", 
            "http://localhost,http://localhost:3000"
        )
        return [origin.strip() for origin in origins_str.split(",")]

settings = Settings()