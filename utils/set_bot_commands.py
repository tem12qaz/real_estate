from aiogram import types
from aiogram.types import BotCommandScopeChat

from db.models import TelegramUser
from loader import bot


def user_scope(user: TelegramUser):
    return BotCommandScopeChat(user.telegram_id)


async def set_commands(user: TelegramUser):
    await bot.set_my_commands(
        [
            types.BotCommand("find", user.button('find')),
            types.BotCommand("sales", user.button('sales')),
            # types.BotCommand("chats", user.button('chats')),
            types.BotCommand("support", user.button('support')),
            types.BotCommand("language", user.button('language')),
        ],
        scope=user_scope(user)
    )
