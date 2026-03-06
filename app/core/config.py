from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    LOG_LEVEL: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    class Config:
        env_file = ".env"

settings = Settings()
