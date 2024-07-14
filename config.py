import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = os.environ.get("TELEGRAM_BOT_ADMIN_ID")

POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")

url=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"