from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env files: prefer backend/.env, but fall back to repository root ../.env
cwd = os.path.dirname(__file__)
backend_env = os.path.join(cwd, "..", ".env")
root_env = os.path.join(cwd, "..", "..", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)
elif os.path.exists(root_env):
    load_dotenv(root_env)


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # MySQL settings
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: Optional[int] = 3306
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DB: Optional[str] = None

    # Groq model configuration
    GROQ_API_KEY: Optional[str] = None
    MODEL_NAME: str = "llama-3.3-70b-versatile"  # model to pass to Groq API

    # Security
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_UNAUTHENTICATED: int = 10  # per minute
    RATE_LIMIT_AUTHENTICATED: int = 100  # per minute

    class Config:
        # pydantic-settings will still read environment variables; we
        # proactively loaded a .env above if present.
        env_file = None
        env_file_encoding = "utf-8"

settings = Settings()
