from pydantic import SecretStr, PostgresDsn, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    bot_token: SecretStr
    db_url: str
    admin: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    

settings = Settings()