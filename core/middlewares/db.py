from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class AsyncSeesionMiddleware(BaseMiddleware):
    def __init__(self, async_session: async_sessionmaker[AsyncSession]) -> None:
        self.async_session = async_session

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        async with self.async_session() as session:
            data['session'] = session
            return await handler(event, data)