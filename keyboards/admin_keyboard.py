from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from enum import Enum


admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Конфигуратор поста с кнопкой")],
        [KeyboardButton(text="Добавить файл в рассылку")],
        [KeyboardButton(text="Рассылка для пользователей")]

    ],
    resize_keyboard=True
)