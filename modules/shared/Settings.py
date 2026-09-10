from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    DATABASE_URL: str
    DATA_PATH: str

    CLIENT_ID: str
    CLIENT_SECRET: str
    REFRESH_TOKEN: str

    TOKEN_URL: str
    TRACKS_URL: str


settings = Settings()
