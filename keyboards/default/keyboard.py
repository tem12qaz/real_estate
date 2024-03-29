from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from db.models import TelegramUser


def get_main_keyboard(user: TelegramUser) -> ReplyKeyboardMarkup:
    main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    find = KeyboardButton(user.button('find'))
    sales = KeyboardButton(user.button('sales'))
    profile = KeyboardButton(user.button('chats'))
    support = KeyboardButton(user.button('support'))
    lang = KeyboardButton(user.button('language'))

    main_keyboard.add(find, sales, support, lang)

    return main_keyboard
