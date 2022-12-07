from aiogram import types
from aiogram.types import BotCommandScopeChat

from db.models import TelegramUser


def user_scope(user: TelegramUser):
    return BotCommandScopeChat(user.telegram_id)


async def set_commands(dp, user: TelegramUser):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("find", user.button('find')),
            types.BotCommand("sales", user.button('sales')),
            types.BotCommand("chats", user.button('chats')),
            types.BotCommand("support", user.button('support')),
        ],
        scope=user_scope(user)
    )
