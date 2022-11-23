import asyncio
from datetime import datetime, timedelta

from tortoise.expressions import Q

from data.config import tz
from db.models import Order, Date, Chat, PromoCode


class Supervisor:
    def __init__(self, loop: asyncio.AbstractEventLoop, sleep: int = 3600):
        self.loop = loop
        self.sleep = sleep
        self.tasks = [self.orders, self.dates, self.chats, self.promos]

    @staticmethod
    async def orders():
        print('orders_supervisor')

        now = datetime.now(tz)
        # delete_orders_time = now - timedelta(minutes=15) # YOOKASSA BLOCK WIDGET / RETURN PLACES TO DATE
        # orders_to_delete = await Order.filter(
        #     datetime__lt=delete_orders_time, state='created'
        # )
        # for order in orders_to_delete:
        #     await order.delete()

        orders_to_finish = await Order.filter(
            date__end__lt=now, state='payed'
        )
        for order in orders_to_finish:
            order.state = 'finish'
            await order.save()

    @staticmethod
    async def dates():
        print('date_supervisor')

        now = datetime.now(tz)
        dates_to_delete = await Date.filter(
            end__lt=now
        )
        for date in dates_to_delete:
            await date.delete()

    @staticmethod
    async def chats():
        print('chat_supervisor')

        now = datetime.now(tz)
        delete_chats_time = now - timedelta(days=1)
        chats_to_delete = await Chat.filter(
            datetime__lt=delete_chats_time
        )
        for chat in chats_to_delete:
            await chat.delete()

    @staticmethod
    async def promos():
        print('promos_supervisor')
        now = datetime.now(tz)
        promos_to_delete = await PromoCode.filter(
            Q(uses=0) | Q(end__lt=now)
        )
        for promo in promos_to_delete:
            await promo.delete()

    def get_task(self):
        task = self.tasks.pop(0)
        self.tasks.append(task)
        return task

    async def cycle(self):
        while True:
            task = self.get_task()
            await task()
            await asyncio.sleep(self.sleep)

    def start(self):
        self.loop.create_task(self.cycle())


