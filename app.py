import asyncio

from aiogram.utils.executor import set_webhook
from aiohttp import web

from data.config import UPDATE_MESSAGE_PATH, UPDATE_BUTTON_PATH, BOT_TOKEN, HOST, SEND_MESSAGE_PATH
from db.db import db_init
from db.models import Message, Button
from routes.update_messages_and_buttons_handler import update_messages_handler, update_buttons_handler
from routes.send_message_from_admin_handlers import send_message_from_admin_handler
from utils.set_bot_commands import set_default_commands
from utils.supervisor import Supervisor


async def on_startup(dp):
    # import middlewares
    await dp.bot.set_webhook(HOST + '/' + BOT_TOKEN)
    await db_init()
    await Message.reload()
    await Button.reload()
    supervisor.start()
    # middlewares.setup(dp)
    await set_default_commands(dp)

if __name__ == '__main__':
    from loader import dp, logger
    import handlers

    loop = asyncio.new_event_loop()
    supervisor = Supervisor(loop)

    aiohttp_app = web.Application(logger=logger, loop=loop)

    aiohttp_app.add_routes([web.get(UPDATE_MESSAGE_PATH, update_messages_handler)])
    aiohttp_app.add_routes([web.get(UPDATE_BUTTON_PATH, update_buttons_handler)])
    aiohttp_app.add_routes([web.post(SEND_MESSAGE_PATH, send_message_from_admin_handler)])

    executor = set_webhook(
        dispatcher=dp,
        webhook_path='/' + BOT_TOKEN,
        loop=loop,
        on_startup=on_startup,
        web_app=aiohttp_app
    )
    executor.run_app(loop=loop)
