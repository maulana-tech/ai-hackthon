from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "TrendScout Supplier Connector"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    firecrawl_api_key: str
    getcirclo_api_key: str
    getcirclo_jwt_token: str = ""
    getcirclo_whatsapp_enabled: bool = True
    getcirclo_memory_enabled: bool = True
    
    openai_api_key: str
    
    rapidapi_key: str
    lazada_api_host: str = "lazada-api.p.rapidapi.com"
    
    apify_api_key: str
    
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
