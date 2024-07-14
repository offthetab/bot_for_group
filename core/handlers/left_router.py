from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.filters.bot_filters import MemberTypeFilter

# DB
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User


left_router = Router()
left_router.message.filter(MemberTypeFilter(["left"]))


@left_router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    await session.merge(User(id=message.from_user.id,
                    name=message.from_user.first_name,
                    surname=message.from_user.last_name, 
                    username=message.from_user.username))
    await session.commit()
    
    await message.answer(
        text="Добро пожаловать, тут ты можешь узнать все самое интересное в мире автомобилей и получать приватную информацию!" + "\n" + "<b>Однако для этого необходимо подписаться на группу</b>" 
        + "\n" + "<a href='https://t.me/allaboutcars321'>Все о машинах🚘</a>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [InlineKeyboardButton(text='Подписаться в группу', url='https://t.me/allaboutcars321')],
                [InlineKeyboardButton(text='Проверить подписку', callback_data='check_subscription')]
            ]
        )
    )

# check if user subscribed to channel (not subscribed handler). Callback data check_subscription
@left_router.callback_query(F.data == "check_subscription")
async def send_post(callback: CallbackQuery):
    await callback.message.answer(text="<b>Для разблокировки полного функционала бота необходимо на группу</b>" 
        + "\n" + "<a href='https://t.me/allaboutcars321'>Все о машинах🚘</a>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [InlineKeyboardButton(text='Подписаться в группу', url='https://t.me/allaboutcars321')],
                [InlineKeyboardButton(text='Проверить подписку', callback_data='check_subscription')]
            ]
        )
    )