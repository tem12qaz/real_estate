from aiohttp import web

from db.models import Button, Message


async def update_messages_handler(req: web.Request) -> web.Response:
    await Message.reload()
    print('messages_updated')
    return web.HTTPNotFound()


async def update_buttons_handler(req: web.Request) -> web.Response:
    await Button.reload()
    print('buttons_updated')
    return web.HTTPNotFound()
