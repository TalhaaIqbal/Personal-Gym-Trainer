from pydantic_settings import BaseSettings
import urllib.parse

class Settings(BaseSettings):
    APP_NAME: str = "Personal Gym Trainer"

    MONGO_URL: str
    MONGO_DB_NAME: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def mongo_url_encoded(self):
        return urllib.parse.quote_plus(self.MONGO_URL)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

settings = Settings()