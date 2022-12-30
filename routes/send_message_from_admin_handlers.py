from aiohttp import web
from loader import bot


async def send_message_from_admin_handler(req: web.Request) -> web.Response:
    data = await req.json()
    users = data['users']
    text = data['text']
    print(req.remote)

    if True:
        for user in users:
            try:
                await bot.send_message(
                    user, text
                )
            except Exception as e:
                pass

            return web.Response()

    else:
        return web.HTTPNotFound()
