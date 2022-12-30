from aiohttp import web

from admin.config import SECURITY_REQUEST_SALT
from data.config import BOT_TOKEN
from loader import bot
from utils.sha256 import sha256


async def send_message_from_admin_handler(req: web.Request) -> web.Response:
    data = await req.json()
    users = data['users']
    text = data['text']
    sha = data['sum']

    if sha == sha256(SECURITY_REQUEST_SALT + BOT_TOKEN):
        for user in users:
            try:
                await bot.send_message(
                    user, text
                )
            except Exception as e:
                print(e)
                pass

        return web.Response()

    else:
        return web.HTTPNotFound()
