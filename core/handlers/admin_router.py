from aiogram import Bot, Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError 

# importing admin keyboards
from core.keyboards.admin_keyboard import admin_main_kb, if_add_photo, close_configurer, if_add_inline
from sqlalchemy import update, select
from core.filters.bot_filters import MemberTypeFilter

# DB
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.models import User, Document
from asyncio import sleep

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
    await message.answer(text='Это конфигуратор поста в группу с кнопкой. Для начала укажите текст поста', reply_markup=close_configurer)

# getting post text
@admin_router.message(Form.post_text, F.text)
async def process_post_text(message: Message, state: FSMContext) -> None:

    await state.update_data(post_text=message.text)
    await state.set_state(Form.if_media)
    await message.answer(text='Добавить одно фото или видео к посту?', reply_markup=if_add_photo)

# getting post text (user send not text)
@admin_router.message(Form.post_text, ~F.text)
async def process_post_text(message: Message, state: FSMContext) -> None:
    await message.answer(text='Вам нужно прислать именно текст поста!', reply_markup=close_configurer)

# user wants to add photo/video
@admin_router.callback_query(F.data == 'add_photo', Form.if_media)
async def ask_for_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.photo_file_id)
    await callback.message.answer(text='Присылайте фотографию или видео', reply_markup=close_configurer)

# user does not want to add photo/video
@admin_router.callback_query(F.data == 'no_photo', Form.if_media)
async def ask_for_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.photo_file_id)
    await state.update_data(photo_file_id=None)
    await state.set_state(Form.button_text)
    await callback.message.answer(text='Введите текст, который будет отображаться на кнопке', reply_markup=close_configurer)

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
    await message.answer(text='Введите текст, который будет отображаться на кнопке', reply_markup=close_configurer)

# getting post video
@admin_router.message(Form.photo_file_id, F.video)
async def process_post_video(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_file_id=[message.video.file_id, 'video'])
    await state.set_state(Form.button_text)
    await message.answer(text='Введите текст, который будет отображаться на кнопке', reply_markup=close_configurer)

# user send neither photo nor video
@admin_router.message(Form.photo_file_id, ~(F.video | F.photo))
async def not_photo_video(message: Message, state: FSMContext) -> None:
    await message.answer(text='Пришлите фотографию или видео‼️', reply_markup=close_configurer)

# getting inline button text TODO support multiple btns 
@admin_router.message(Form.button_text, F.text)
async def process_button_text(message: Message, state: FSMContext) -> None:
    await state.update_data(button_text=message.text)
    await state.set_state(Form.button_url)
    await message.answer(text='Введите ссылку, на которую будет перекидывать кнопка (это может быть телеграмм бот, канал или любая сторонняя ссылка)', reply_markup=close_configurer)

# incorrect inline button text
@admin_router.message(Form.button_text, ~F.text)
async def process_button_text(message: Message, state: FSMContext) -> None:
    await message.answer(text='Введите текст кнопки‼️', reply_markup=close_configurer)    

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
    await message.answer(text='Неккоректная ссылка‼️', reply_markup=close_configurer)

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
async def get_file(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(input_file=message.document.file_id)
    input_data = await state.get_data()

    stmt = update(Document).where(Document.status == True).values(status=False)
    await session.execute(stmt)
    await session.merge(Document(file_id=input_data.get('input_file'), caption=message.caption, status=True))
    await session.commit()
    await message.answer(text='Файл в рассылке был обновлен')

    await state.clear()


# FSM for admin to mass mail all active users in bot
class MassMailing(StatesGroup):
    post_text = State()
    post_photo = State()
    button_text = State()
    button_url = State()
    if_start = State()

@admin_router.message(F.text.lower() == 'рассылка для пользователей')
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MassMailing.post_text)
    await message.answer(text='Конфигуратор рассылки пользователям бота. Введите текст поста или фотографию с текстом.', reply_markup=close_configurer)

# getting post text
@admin_router.message(MassMailing.post_text, F.text)
async def process_post_text(message: Message, state: FSMContext) -> None:
    await state.update_data(post_text=message.text)

    await state.set_state(MassMailing.post_photo)
    await state.update_data(post_photo=None)

    await message.answer(text=f"Текст поста был сохранен. Вы хотите добавить инлайн кнопку к рассылке?", reply_markup=if_add_inline)
    await state.set_state(MassMailing.button_text)


# getting post text with photo
@admin_router.message(MassMailing.post_text, F.photo)
async def process_photo_caption(message: Message, state: FSMContext) -> None:
    await state.update_data(post_text=message.caption)

    await state.set_state(MassMailing.post_photo)
    await state.update_data(post_photo=message.photo[-1].file_id) 

    await message.answer(text=f"Фотография с текстом были сохранены. Вы хотите добавить инлайн кнопку к рассылке? (можете сразу вводить текст на кнопке)", reply_markup=if_add_inline)
    await state.set_state(MassMailing.button_text)

# incorrect input text and photo
@admin_router.message(MassMailing.post_text, ~(F.text | F.photo))
async def process_incr_impt(message: Message, state: FSMContext) -> None:
    await message.answer(text='Вам нужно прислать именно текст поста или фотографию с текстом!', reply_markup=close_configurer)

# adding inline buttons
@admin_router.callback_query(MassMailing.button_text, F.data == 'add_inline_btn')
async def add_inline_btns(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text="Вводите текст кнопки", reply_markup=close_configurer)

# getting button text
@admin_router.message(MassMailing.button_text, F.text)
async def get_btn_text(message: Message, state: FSMContext) -> None:
    await state.update_data(button_text=message.text)
    await message.answer(text="Введите ссылку", reply_markup=close_configurer)
    await state.set_state(MassMailing.button_url)

# incorrect button text input
@admin_router.message(MassMailing.button_text, ~F.text)
async def incorrect_btn_text(message: Message, state: FSMContext) -> None:
    await message.answer(text="Некорректный ввод", reply_markup=close_configurer)
    
# getting button url
@admin_router.message(MassMailing.button_url, (F.text.contains('https://') | F.text.contains('http://')))
async def get_btn_url(message: Message, state: FSMContext) -> None:
    await state.update_data(button_url=message.text)

    data = await state.get_data()
    if data.get('post_photo') == None:
        await message.answer(text=data.get('post_text'), reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text=data.get('button_text'), url=data.get('button_url'))]
                                        ]))
    else:
        await message.answer_photo(photo=data.get('post_photo'), caption=data.get('post_text'), reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text=data.get('button_text'), url=data.get('button_url'))]
                                        ]))
        
    await message.answer(text="Начинаем рассылку?",  reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Да✅', callback_data='start_broadcast')],
                                            [InlineKeyboardButton(text='Нет🚫', callback_data='no_broadcast')],
                                        ]))
    await state.set_state(MassMailing.if_start)

# incorrect button url
@admin_router.message(MassMailing.button_url, ~(F.text.contains('https://') | F.text.contains('http://')))
async def get_btn_url(message: Message, state: FSMContext) -> None:
    await message.answer(text='Некорректная ссылка', reply_markup=close_configurer)

# no inline buttons. Post configured
@admin_router.callback_query(MassMailing.button_text, F.data == 'no_inline_btn')
async def no_inline_btns(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(button_text=None)
    await state.set_state(MassMailing.button_url)
    await state.update_data(button_url=None)
    data = await state.get_data()
    if data.get('post_photo') == None:
        await callback.message.answer(text=data.get('post_text'))
    else:
        await callback.message.answer_photo(photo=data.get('post_photo'), caption=data.get('post_text'))
    
    await callback.message.answer(text="Начинаем рассылку?",  reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [InlineKeyboardButton(text='Да✅', callback_data='start_broadcast')],
                                            [InlineKeyboardButton(text='Нет🚫', callback_data='no_broadcast')],
                                        ]))
        
    await state.set_state(MassMailing.if_start)

@admin_router.callback_query(MassMailing.if_start, F.data == 'start_broadcast') 
async def start_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession) -> None:
    await callback.message.edit_text(text='Рассылка запущена⚙️')

    data = await state.get_data()
    post_text = data.get('post_text')
    post_photo = data.get('post_photo')
    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=data.get('button_text'), url=data.get('button_url'))]]) if data.get('button_text') != None else None

    stmt = select(User.id).execution_options(stream_results=True, max_row_buffer=20)
    rows = await session.stream(statement=stmt)
    # TODO make Broadcast class in utils dir and add db integration
    if post_photo == None:
        async for row in rows:  
            try:
                await bot.send_message(chat_id=row.id, text=post_text, reply_markup=btn)
                await sleep(0.05)
            except TelegramForbiddenError as e:
                pass 
            except TelegramRetryAfter as e:
                sleep(e.retry_after)
    else:
        async for row in rows:  
            try:
                await bot.send_photo(chat_id=row.id, photo=post_photo,caption=post_text, reply_markup=btn)
                await sleep(0.05)
            except TelegramForbiddenError as e:
                pass 
            except TelegramRetryAfter as e:
                sleep(e.retry_after)
    
    await state.clear()

@admin_router.callback_query(MassMailing.if_start, F.data == 'no_broadcast')
async def no_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text('Рассылка отменена')
    await state.clear()