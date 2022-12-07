from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from db.models import TelegramUser


def get_main_keyboard(user: TelegramUser) -> ReplyKeyboardMarkup:
    main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    find = KeyboardButton(user.button('find'))
    sales = KeyboardButton(user.button('sales'))
    profile = KeyboardButton(user.button('chats'))
    support = KeyboardButton(user.button('support'))

    main_keyboard.add(find, sales, profile, support)

    return main_keyboard
