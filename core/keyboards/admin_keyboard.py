from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from enum import Enum


admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Конфигуратор поста с кнопкой")],
        [KeyboardButton(text="Добавить файл в рассылку")],
        [KeyboardButton(text="Рассылка для пользователей")],
    ],
    resize_keyboard=True,
)

if_add_photo = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да✅", callback_data="add_photo")],
        [InlineKeyboardButton(text="Нет🚫", callback_data="no_photo")],
        [
            InlineKeyboardButton(
                text="Закрыть конфигуратор❌", callback_data="close_configurator"
            )
        ],
    ]
)

close_configurer = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Закрыть конфигуратор❌", callback_data="close_configurator"
            )
        ]
    ]
)


if_add_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да✅", callback_data="add_inline_btn")],
        [InlineKeyboardButton(text="Нет🚫", callback_data="no_inline_btn")],
        [
            InlineKeyboardButton(
                text="Закрыть конфигуратор❌", callback_data="close_configurator"
            )
        ],
    ]
)
