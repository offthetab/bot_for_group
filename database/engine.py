import asyncio
import asyncpg

from config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER


async def add_user(telegram_id, name, surname, username):
    async with asyncpg.create_pool(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB,
                                command_timeout=60) as pool:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (telegram_id, name, surname, username) VALUES ($1, $2, $3, $4) 
                ON CONFLICT (telegram_id) DO UPDATE SET name = $2, surname = $3, username = $4;
            ''', telegram_id, name, surname, username)

async def get_all_users():
    async with asyncpg.create_pool(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB,
                                command_timeout=60) as pool:
        async with pool.acquire() as conn:
            return await conn.fetch('SELECT telegram_id FROM users')
        
async def add_document(file_id, caption):
    async with asyncpg.create_pool(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB,
                                command_timeout=60) as pool:
        async with pool.acquire() as conn:
            await conn.execute('''UPDATE documents SET status=FALSE WHERE status=TRUE;''')
            await conn.execute('''INSERT INTO documents (file_id, caption) VALUES ($1, $2);''', file_id, caption)

async def get_active_document():
    async with asyncpg.create_pool(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DB,
                                command_timeout=60) as pool:
        async with pool.acquire() as conn:
            return await conn.fetchrow('''SELECT file_id, caption FROM documents WHERE status=TRUE;''')