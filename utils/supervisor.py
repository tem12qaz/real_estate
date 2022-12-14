import asyncio
from datetime import datetime, timedelta

from data.config import tz
from db.models import Chat, TelegramUser
from keyboards.inline.keyboards import support_keyboard
from loader import bot


class Supervisor:
    def __init__(self, loop: asyncio.AbstractEventLoop, sleep: int = 3600):
        self.loop = loop
        self.sleep = sleep

    @staticmethod
    async def send_message(user: TelegramUser):
        await bot.send_message(
            user.telegram_id,
            user.message('support_supervisor'),
            reply_markup=await support_keyboard(user)
        )

    def after_call(self, chat: Chat):
        async def notify(chat_: Chat):
            await asyncio.sleep(7200)
            await chat_.refresh_from_db()
            user: TelegramUser = await (await chat_.seller).manager
            await bot.send_message(
                user.telegram_id,
                user.message('after_call_notify').format(user=user.username, chat_id=chat_.id),

            )

    def call_reject(self, chat: Chat):
        async def notify(chat_: Chat):
            await asyncio.sleep(600)
            await chat_.refresh_from_db()
            if chat_.call_rejected:
                await self.send_message(await chat_.customer)

        self.loop.create_task(notify(chat))

    async def active_users(self):
        now = datetime.now(tz)
        notify_time = now - timedelta(days=1)
        users = await TelegramUser.filter(
            last_message_lt=notify_time, state='start'
        )
        for user in users:
            await self.send_message(user)
            await user.update_time()

    def form_notify(self, user: TelegramUser):
        async def notify(user_: TelegramUser):
            await asyncio.sleep(600)
            await user_.refresh_from_db()
            if user_.state == 'form':
                await self.send_message(user_)

        self.loop.create_task(notify(user))

    async def cycle(self):
        while True:
            await self.active_users()
            await asyncio.sleep(self.sleep)

    def start(self):
        self.loop.create_task(self.cycle())





