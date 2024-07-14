from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart, IS_MEMBER, IS_NOT_MEMBER

# importing filters
from core.filters.bot_filters import MemberTypeFilter
from core.keyboards.member_keyboard import main_user_keyboard, back_btn
from core.keyboards.member_keyboard import UserAction, Category


member_router = Router()
member_router.message.filter(MemberTypeFilter(["member", "creator", "admin"]))


@member_router.message(CommandStart())
async def cmd_start(message: Message):
    # await add_user(telegram_id=message.from_user.id, 
    #                name=message.from_user.first_name, 
    #                surname=message.from_user.last_name, 
    #                username=message.from_user.username)
    
    await message.answer(
        f"Добро пожаловать. Тут ты узнаешь о самом интересном в мире автомобилей 🚘.",
        reply_markup=main_user_keyboard().as_markup()
    )

# check if user subscribed to channel (subscribed handler). Callback data check_subscription from left_router file line 24
@member_router.callback_query(F.data == "check_subscription", MemberTypeFilter(["member"]))
async def send_post(callback: CallbackQuery):
    await callback.message.answer(text="Вы подписаны на группу, вы можете пользоваться ботом.",
        reply_markup=main_user_keyboard().as_markup()
    )


@member_router.callback_query(UserAction.filter(F.category == Category.get_guide))
async def get_guide(callback: CallbackQuery, callback_data: UserAction):
    # querry = await get_active_document()
    # try:
    #     document = querry['file_id']
    #     caption = querry['caption']
    #     await callback.message.delete()
    #     await callback.message.answer_document(document, caption=caption, reply_markup=back_btn(level=callback_data.level).as_markup()) # TODO add button back to menu        
    # except TypeError:
    #     await callback.message.answer(text='<b>На данный момент нет файла.😔</b>')
    # except:
    #     await callback.message.answer(text='<b>Что-то пошло не так.😔</b>')

    await callback.message.answer(text='<b>Что-то пошло не так.😔</b>')  
  

@member_router.callback_query(UserAction.filter(F.category == Category.get_services))
async def get_services(callback: CallbackQuery):
    await callback.message.edit_text(text='Актуальный список услуг')


@member_router.callback_query(UserAction.filter(F.category == Category.get_socials))
async def get_socials(callback: CallbackQuery, callback_data: UserAction):
    await callback.message.edit_text(text='Список соц сетей')