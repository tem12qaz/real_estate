import asyncio
from datetime import datetime, timedelta
import datetime as dt

from tortoise.expressions import Q

from data.config import tz, SEND_TIME
from db.models import Chat, TelegramUser, Developer
from keyboards.inline.after_call import after_call_keyboard
from keyboards.inline.keyboards import support_keyboard, group_chats_keyboard
from loader import bot, loop


class Supervisor:
    # def __init__(self, loop: asyncio.AbstractEventLoop, sleep: int = 3600):
    #     self.loop = loop
    #     self.sleep = sleep

    def __new__(cls, loop: asyncio.AbstractEventLoop, sleep: int = 3600):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Supervisor, cls).__new__(cls)
            cls.instance.loop = loop
            cls.instance.sleep = sleep
            cls.send_time = cls.to_sec(dt.time(*SEND_TIME))

        return cls.instance

    @staticmethod
    async def send_message(user: TelegramUser):
        await bot.send_message(
            user.telegram_id,
            user.message('support_supervisor'),
            reply_markup=await support_keyboard(user)
        )

    def after_call(self, chat: Chat, delay: int = 2):
        async def notify(chat_: Chat):
            await asyncio.sleep(delay)
            await chat_.refresh_from_db()
            user: TelegramUser = await (await chat_.seller).manager
            await bot.send_message(
                user.telegram_id,
                user.message('after_call_notify').format(user=user.username, chat_id=chat.id,
                                                         estate=(await chat.object).name),
                reply_markup=after_call_keyboard(user, chat)

            )
        self.loop.create_task(notify(chat))

    def call_reject(self, chat: Chat):
        async def notify(chat_: Chat):
            await asyncio.sleep(10)
            await chat_.refresh_from_db()
            if chat_.call_rejected:
                await self.send_message(await chat_.customer)

        self.loop.create_task(notify(chat))

    async def active_users(self):
        now = datetime.now(tz)
        notify_time = now - timedelta(days=1)
        users = await TelegramUser.filter(
            last_message__lt=notify_time, state='start'
        )
        # print(users)
        for user in users:
            if await user.developer_manager:
                continue
            await self.send_message(user)
            await user.update_time()

    @classmethod
    async def wait(cls, now_time):
        wait_time = cls.send_time - now_time
        if wait_time < 0:
            wait_time = 86400 - now_time + cls.send_time
        print(wait_time)

        await asyncio.sleep(wait_time)

    @staticmethod
    def to_sec(t):
        seconds = (t.hour * 60 + t.minute) * 60 + t.second
        return seconds

    async def daily_chats(self):
        while True:
            now = datetime.now()
            await self.wait(self.to_sec(now))
            from_time = datetime.now() - timedelta(days=1)

            for developer in await Developer.all():
                chats = await Chat.filter(
                    Q(Q(developer=developer), Q(messages__time__gte=from_time))
                ).distinct()
                if chats:
                    await bot.send_message(
                        developer.chat_id,
                        (await developer.manager).message('daily_chats'),
                        reply_markup=await group_chats_keyboard(developer, 1, chats)
                    )

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
        self.loop.create_task(self.daily_chats())


supervisor = Supervisor(loop)





