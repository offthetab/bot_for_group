from aiogram import Bot
from aiogram.types import Message

# filtering events
from aiogram.filters import Filter


# filtering members
class MemberTypeFilter(Filter):
    def __init__(self, status: list[str]) -> None:
        self.status = status

    async def __call__(self, message: Message, bot: Bot) -> bool:
        chat_member = await bot.get_chat_member(chat_id='@allaboutcars321', user_id=message.from_user.id)
        member_status = chat_member.status.value
        return member_status in self.status