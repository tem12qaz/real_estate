import asyncio

from aiohttp import web


async def meet_redirect(req: web.Request) -> web.Response:
    await asyncio.sleep(1)
    meet = req.match_info['meet']
    return web.HTTPFound(f'https://meet.google.com/{meet}/')
