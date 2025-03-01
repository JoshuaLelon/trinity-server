import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Server configuration settings."""
    # App configuration
    APP_NAME: str = "Trinity Journaling App"
    API_PREFIX: str = "/api/v1"
    
    # API Keys
    LANGCHAIN_API_KEY: str = Field(default="", env="LANGCHAIN_API_KEY")
    LANGSMITH_API_KEY: str = Field(default="", env="LANGSMITH_API_KEY")
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    NOTION_API_KEY: str = Field(default="", env="NOTION_API_KEY")
    
    # LangSmith configuration
    LANGCHAIN_TRACING_V2: bool = Field(default=True, env="LANGCHAIN_TRACING_V2")
    LANGSMITH_TRACING: bool = Field(default=True, env="LANGSMITH_TRACING")
    LANGCHAIN_PROJECT: str = Field(default="trinity-journal", env="LANGCHAIN_PROJECT")
    LANGSMITH_PROJECT: str = Field(default="trinity-journal", env="LANGSMITH_PROJECT")
    LANGSMITH_ENDPOINT: str = Field(default="https://api.smith.langchain.com", env="LANGSMITH_ENDPOINT")
    
    # Notion configuration
    NOTION_DATABASE_ID: str = Field(default="", env="NOTION_DATABASE_ID")

    # LLM Configuration
    LLM_MODEL: str = Field(default="gpt-4o", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.0, env="LLM_TEMPERATURE")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_langchain_api_key(self) -> str:
        """Get the LangChain API key, preferring LANGSMITH_API_KEY if available."""
        return self.LANGSMITH_API_KEY or self.LANGCHAIN_API_KEY


# Create settings instance
settings = Settings() 