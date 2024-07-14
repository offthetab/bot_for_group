import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.admin_router import admin_router
from handlers.member_router import member_router
from handlers.left_router import left_router

# importing .env data 
from config import TOKEN, ADMIN_ID, url

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def on_startup(bot: Bot):
    await bot.send_message(chat_id=ADMIN_ID, text="Бот был успешно запущен")


# Запуск бота
async def main():
    engine = create_async_engine(url=url, echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.startup.register(on_startup)

    dp.include_routers(admin_router, member_router, left_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())