from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.models import TelegramUser, Chat
from keyboards.inline.callbacks import after_call_callback


def after_call_keyboard(user: TelegramUser, chat: Chat) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('yes'),
                    callback_data=after_call_callback.new(
                        action='success', chat_id=chat.id
                    )
                ),
                InlineKeyboardButton(
                    text=user.button('scheduled_a_call'),
                    callback_data=after_call_callback.new(
                       action='scheduled_a_call', chat_id=chat.id
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text=user.button('customer_declined'),
                    callback_data=after_call_callback.new(
                        action='customer_declined', chat_id=chat.id
                    )
                )
            ]
        ]
    )
    return keyboard


def after_call_success_keyboard(user: TelegramUser, chat: Chat) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('yes'),
                    callback_data=after_call_callback.new(
                        action='yes', chat_id=chat.id
                    )
                ),
                InlineKeyboardButton(
                    text=user.button('no'),
                    callback_data=after_call_callback.new(
                       action='no', chat_id=chat.id
                    )
                )
            ]
        ]
    )
    return keyboard


def after_call_all_info_keyboard(user: TelegramUser, chat: Chat) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('yes'),
                    callback_data=after_call_callback.new(
                        action='yes', chat_id=chat.id
                    )
                ),
                InlineKeyboardButton(
                    text=user.button('no'),
                    callback_data=after_call_callback.new(
                       action='no', chat_id=chat.id
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text=user.button('partially'),
                    callback_data=after_call_callback.new(
                        action='partially', chat_id=chat.id
                    )
                )
            ]
        ]
    )
    return keyboard


def after_call_type_keyboard(user: TelegramUser, chat: Chat) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('meet'),
                    callback_data=after_call_callback.new(
                        action='meet', chat_id=chat.id
                    )
                ),
                InlineKeyboardButton(
                    text=user.button('presentation'),
                    callback_data=after_call_callback.new(
                       action='presentation', chat_id=chat.id
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text=user.button('no'),
                    callback_data=after_call_callback.new(
                        action='no', chat_id=chat.id
                    )
                )
            ]
        ]
    )
    return keyboard
