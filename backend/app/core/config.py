from functools import lru_cache
from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configurations. Reads from .env file or env variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="enterprise_rag")
    
    DATABASE_URL: Optional[str] = Field(default=None)
    
    # Qdrant Configuration
    QDRANT_URL: Optional[str] = Field(default=None)
    QDRANT_API_KEY: Optional[str] = Field(default=None)

    # Ollama Configuration
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="phi3:mini")
    
    # Security / Authentication Configuration
    SECRET_KEY: str = Field(default="placeholder_super_secret_key_for_jwt_signing_change_me_in_production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    DEFAULT_ADMIN_EMAIL: str = Field(default="admin@enterprise.com")
    DEFAULT_ADMIN_PASSWORD: str = Field(default="admin123")
    DEFAULT_SUPER_ADMIN_EMAIL: Optional[str] = Field(default=None)
    DEFAULT_SUPER_ADMIN_PASSWORD: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        """
        Builds the sync DATABASE_URL if it is not explicitly provided.
        """
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        import sys
        if "pytest" not in sys.modules:
            if not self.DEFAULT_SUPER_ADMIN_EMAIL or not self.DEFAULT_SUPER_ADMIN_PASSWORD:
                raise RuntimeError(
                    "Mandatory environment variables DEFAULT_SUPER_ADMIN_EMAIL and "
                    "DEFAULT_SUPER_ADMIN_PASSWORD must be configured."
                )
        return self

@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings class.
    """
    return Settings()

settings = get_settings()
