from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HUB Aura API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "API para gestão e análise de Acordos de Cooperação Técnica"
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:rx1800@localhost:5433/hub_aura_db"
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:5173"]
    
    # NLP Model settings
    SPACY_MODEL: str = "pt_core_news_lg"
    
    class Config:
        case_sensitive = True

settings = Settings()