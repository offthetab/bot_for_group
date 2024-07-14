from aiogram import Bot, Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# importing admin keyboards
from core.keyboards.admin_keyboard import admin_main_kb
from core.filters.bot_filters import MemberTypeFilter

# DB
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User


admin_router = Router()
admin_router.message.filter(MemberTypeFilter(["creator", "admin"]))


@admin_router.message(Command("admin"))
async def cmd_start(message: Message, session: AsyncSession):
    await session.merge(User(id=message.from_user.id,
                    name=message.from_user.first_name,
                    surname=message.from_user.last_name, 
                    username=message.from_user.username))
    await session.commit()

    await message.answer(
        f"Добро пожаловать. Вы авторизовались как создатель или админ сообщества! Тут вы можете управлять вашим каналом.",
        reply_markup=admin_main_kb
    )

# FSM for admin post with inline button in channel configurator 
class Form(StatesGroup):
    post_text = State()
    if_media = State()
    photo_file_id = State()
    button_text = State()
    button_url = State()
    if_send = State()

@admin_router.message(F.text.lower() == 'конфигуратор поста с кнопкой')
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Form.post_text)
    await message.answer(text='Это конфигуратор поста в группу с кнопкой. Для начала укажите текст поста', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# getting post text
@admin_router.message(Form.post_text, F.text)
async def process_post_text(message: Message, state: FSMContext) -> None:

    await state.update_data(post_text=message.text)
    await state.set_state(Form.if_media)
    await message.answer(text='Добавить одно фото или видео к посту?', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Да✅', callback_data='add_photo')],
                                            [InlineKeyboardButton(text='Нет🚫', callback_data='no_photo')],
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')] # TODO cancel
                                        ]))

# getting post text (user send not text)
@admin_router.message(Form.post_text, ~F.text)
async def process_post_text(message: Message, state: FSMContext) -> None:
    await message.answer(text='Вам нужно прислать именно текст поста!', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# user wants to add photo/video
@admin_router.callback_query(F.data == 'add_photo', Form.if_media)
async def ask_for_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.photo_file_id)
    await callback.message.answer(text='Присылайте фотографию или видео')

# user does not want to add photo/video
@admin_router.callback_query(F.data == 'no_photo', Form.if_media)
async def ask_for_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.photo_file_id)
    await state.update_data(photo_file_id=None)
    await state.set_state(Form.button_text)
    await callback.message.answer(text='Введите текст, который будет отображаться на кнопке', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

@admin_router.message(Form.if_media)
async def skipped_buttons(message: Message, state: FSMContext):
    await message.answer(text='Добавить одно фото или видео к посту?', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Да✅', callback_data='add_photo')],
                                            [InlineKeyboardButton(text='Нет🚫', callback_data='no_photo')],
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))
    
# getting post image  
@admin_router.message(Form.photo_file_id, F.photo)
async def process_post_image(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_file_id=[message.photo[-1].file_id, 'photo'])
    await state.set_state(Form.button_text)
    await message.answer(text='Введите текст, который будет отображаться на кнопке', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# getting post video
@admin_router.message(Form.photo_file_id, F.video)
async def process_post_video(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_file_id=[message.video.file_id, 'video'])
    await state.set_state(Form.button_text)
    await message.answer(text='Введите текст, который будет отображаться на кнопке', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# user send neither photo nor video
@admin_router.message(Form.photo_file_id, ~(F.video | F.photo))
async def not_photo_video(message: Message, state: FSMContext) -> None:
    await message.answer(text='Пришлите фотографию или видео‼️', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# getting inline button text TODO support multiple btns 
@admin_router.message(Form.button_text, F.text)
async def process_button_text(message: Message, state: FSMContext) -> None:
    await state.update_data(button_text=message.text)
    await state.set_state(Form.button_url)
    await message.answer(text='Введите ссылку, на которую будет перекидывать кнопка (это может быть телеграмм бот, канал или любая сторонняя ссылка)', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# incorrect inline button text
@admin_router.message(Form.button_text, ~F.text)
async def process_button_text(message: Message, state: FSMContext) -> None:
    await message.answer(text='Введите текст кнопки‼️', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))    

# getting inline button link TODO support multiple btns 
@admin_router.message(Form.button_url, (F.text.contains('https://') | F.text.contains('http://')))
async def process_button_text(message: Message, state: FSMContext) -> None:
    await state.update_data(button_url=message.text)
    input_data = await state.get_data() 

    post_text = input_data.get('post_text')
    media_file = input_data.get('photo_file_id')
    button_text = input_data.get('button_text')
    button_url = input_data.get('button_url')

    btn_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])

    # preview of post in channel
    if media_file[-1] == 'photo':
        await message.answer_photo(photo=media_file[0], caption=post_text,
                                    reply_markup=btn_kb
                                    ) 
    elif media_file[-1] == 'video':
        await message.answer_video(video=media_file[0], 
                                    caption=post_text,
                                    reply_markup=btn_kb)
    else:
        await message.answer(text=post_text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text=button_text, url=button_url)]
                                ]))
    
    await state.set_state(Form.if_send)
    await message.answer(text='Отправляем в группу?',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text='Да', callback_data='send_post'),
                                    InlineKeyboardButton(text='Нет', callback_data='clear_post')
                                 ]
                              ]))

# incorrect button url =(
@admin_router.message(Form.button_url, ~(F.text.contains('https://') | F.text.contains('http://')))
async def process_button_text(message: Message, state: FSMContext) -> None:
    await message.answer(text='Неккоректная ссылка‼️', reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Закрыть конфигуратор❌', callback_data='close_configurator')]
                                        ]))

# get from user weather configured post to be send in channel
@admin_router.callback_query(Form.if_send, F.data == "send_post")
async def send_post(callback: CallbackQuery, state: FSMContext, bot: Bot):
    input_data = await state.get_data()

    post_text = input_data.get('post_text')
    media_file = input_data.get('photo_file_id')
    button_text = input_data.get('button_text')
    button_url = input_data.get('button_url')

    btn_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])

    # preview of post in channel
    if media_file[-1] == 'photo':
        await bot.send_photo(chat_id='@allaboutcars321', photo=media_file[0], caption=post_text,
                                    reply_markup=btn_kb
                                    ) 
    elif media_file[-1] == 'video':
        await bot.send_video(chat_id='@allaboutcars321', video=media_file[0], 
                                    caption=post_text,
                                    reply_markup=btn_kb)
    else:
        await bot.send_message(chat_id='@allaboutcars321', text=post_text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text=button_text, url=button_url)]
                                ]))

    await callback.message.answer(text='Пост был успешно отправлен в канал!✅')
    await state.clear()

@admin_router.callback_query(Form.if_send, F.data == "clear_post")
async def clear_post(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Пост не был отправлен!❌')
    await state.clear()

@admin_router.message(Form.if_send)
async def incorrect_button(message: Message, state: FSMContext):
    await message.answer(text='Отправляем пост в группу?',
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text='Да✅', callback_data='send_post'),
                                    InlineKeyboardButton(text='Нет❌', callback_data='clear_post')
                                 ]
                              ]))
    

# canceling post configure
@admin_router.callback_query(F.data == 'close_configurator')
async def cancel_configuring(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(text='Конфигуратор закрыт❌')
    await callback.message.delete()


# Добавить файл в рассылку
class FileDistribution(StatesGroup):
    input_file = State()

# ask for file
@admin_router.message(F.text.lower() == 'добавить файл в рассылку')
async def start_dist(message: Message, state: FSMContext):
    await state.set_state(FileDistribution.input_file)
    await message.answer(
        text='Отправьте файл, который должны получать пользователи. Также вы можете добавить описание к файлу, которое получат пользователи.',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                    [InlineKeyboardButton(text='Назад', callback_data='cancel_file_input')]
            ]
        )
    )

# admin rejects sending file
@admin_router.callback_query(FileDistribution.input_file, F.data == "cancel_file_input")
async def cancel_file_input(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Вы отменили добавление файла')
    await state.clear()

# admin sends file
@admin_router.message(FileDistribution.input_file, F.document)
async def get_file(message: Message, state: FSMContext):
    await state.update_data(input_file=message.document.file_id)

    input_data = await state.get_data()
    await message.answer(text='Файл в рассылке был обновлен')

    # await add_document(file_id=input_data.get('input_file'), caption=message.caption) # TODO adding docs
    await state.clear()


# FSM for admin to mass mail all active users in bot
class MassMailing(StatesGroup):
    post_text = State()
    button_text = State()
    button_url = State()

@admin_router.message(F.text.lower() == 'рассылка для пользователей')
async def start_dist(message: Message):
    # users_lst = await get_all_users() # TODO get all users
    # telegram_ids = [str(record['telegram_id']) for record in users_lst]
    # await message.answer(text=','.join(telegram_ids))
    await message.answer(text='123')
        