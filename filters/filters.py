from aiogram import types
from aiogram.dispatcher.filters import Filter, Command

from db.models import TelegramUser


class MainMenuExcludeFilter(Filter):
    def __init__(self):
        self.exclude = [
            "find",
            "sales",
            "about",
            "favorite",
            "settings",
            "operator",
            "referral",
            "support",
            "orders",
            "start"
        ]
        self.buttons = [
            'find_tours',
            'sales',
            'about_us',
            'favorite',
            'settings',
            'for_operator',
            'referral',
            'support',
            'orders',
        ]

    async def check(self, message: types.Message) -> bool:

        if message.text.startswith('/'):
            if message.text[1:] not in self.exclude:
                return True
        else:
            user = await TelegramUser.get_or_none(telegram_id=int(message.chat.id))
            messages = [user.button(name) for name in self.buttons]
            # print(messages)
            if user and message.text not in messages:
                return True
        return False
