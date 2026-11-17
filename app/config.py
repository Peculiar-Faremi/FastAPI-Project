from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    TEST_DATABASE_URL: str | None = None
    REDIS_URL:str
    TEST_REDIS_URL:str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()