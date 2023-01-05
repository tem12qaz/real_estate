import asyncio

from aiohttp import web
from tortoise.exceptions import DoesNotExist

from db.models import Chat, Action
from utils.actions_type import ActionsEnum


async def meet_redirect(req: web.Request) -> web.Response:
    await asyncio.sleep(1)
    meet = req.match_info['meet']

    try:
        chat_id = int(req.match_info['chat_id'])
        chat = await Chat.get(id=chat_id)
    except (ValueError, DoesNotExist):
        return web.HTTPFound(f'https://meet.google.com/{meet}/')

    object = await chat.object
    if not await Action.get_or_none(
        user=await chat.customer, object=object,
        developer=await object.owner, type=ActionsEnum.video_call, chat=chat
    ):
        await Action.create(
            user=await chat.customer, object=object,
            developer=await object.owner, type=ActionsEnum.video_call, chat=chat
        )

    return web.HTTPFound(f'https://meet.google.com/{meet}/')
