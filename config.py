from pydantic import SecretStr, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    db_url: str
    admin: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()
print(settings.db_url)
print(type(settings.db_url))