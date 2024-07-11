from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from enum import Enum


# main keyboard builder with callback factory
class Category(str, Enum):    #TODO 
    get_guide = "Получить гайд🔐"
    get_services = "Список услуг📋"
    get_socials = "Социальные сети🌐"
    back_to_menu = 'Назад🔙'

class UserAction(CallbackData, prefix="user"):
    category: Category
    level: int = 0

# main keyboardbuilder for user 
def main_user_keyboard():
    builder = InlineKeyboardBuilder()
    for category in Category:
        builder.button(
            text=category.value,
            callback_data=UserAction(category=category, level=1),
        )
    return builder.adjust(1, repeat=True)

def back_btn(category: Category.back_to_menu, level: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=category.value,
        callback_data=UserAction(category=category, level=level - 1))

