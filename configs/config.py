from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    OAUTH2_URL: str
    OAUTH2_TOKEN: str
    DB_CONFIG: str
    PROJECT_NAME: str
    UI_URL: str
    PUBSUB_SUFFIX: str
    TENANT_ID: str
    CLIENT_ID: str


settings = Settings()