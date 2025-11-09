from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "TrendScout Supplier Connector"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Base URL for document links (set to your deployed URL)
    app_base_url: str = "http://localhost:8000"  # Change to GetCirclo webhook URL in production
    
    firecrawl_api_key: str
    getcirclo_api_key: str
    getcirclo_jwt_token: str = ""
    getcirclo_whatsapp_enabled: bool = True
    getcirclo_memory_enabled: bool = True
    
    openai_api_key: str = ""
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    llm_provider: str = "openrouter"  # "openai", "openrouter", or "gemini"
    llm_model: str = "google/gemini-2.0-flash-exp:free"  # Free OpenRouter model
    
    rapidapi_key: str
    lazada_api_host: str = "lazada-api.p.rapidapi.com"
    
    apify_api_key: str
    scraping_mode: str = "api"  # "api" (real scraping) or "dummy" (mock data for testing)
    
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    
    database_url: str = "sqlite:///./data/trendscout.db"
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 7200  # 2 hours in seconds
    
    max_retries: int = 3
    timeout_seconds: int = 120
    scraping_speed: int = 10
    cache_ttl_hours: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
