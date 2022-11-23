import io

from aiogram import types
from aiogram.types import InputFile
from aiohttp import web
from tortoise.exceptions import DoesNotExist

from create_operator_admin import create_admin_account
from data.config import BASE_PATH
from db.models import Tour, TourOperator, User, Config, TelegramUser
from keyboards.inline.moderator import get_moderate_tour_keyboard
from keyboards.inline.operator import get_back_to_tour_operator_keyboard
from loader import bot


async def send_message_from_admin_handler(req: web.Request) -> web.Response:
    data = await req.json()
    action = data['action']
    print(req.remote)

    if 'tour' in action:
        try:
            tour_id = int(data['id'])
            tour = await Tour.get(id=tour_id)
            user = await (await tour.owner).user

        except DoesNotExist:
            if action == 'decline_tour':
                user = await TelegramUser.get(telegram_id=tour_id)
                await bot.send_message(
                    tour_id,
                    user.message('tour_declined')
                )
            return web.HTTPNotFound()

        except ValueError:
            return web.HTTPNotFound()

        if action == 'create_tour':
            if not tour.moderate:
                media = types.MediaGroup()
                for photo in await tour.photos:
                    with open(BASE_PATH + photo.path, 'rb') as f:
                        binary = f.read()
                        media.attach_photo(InputFile(io.BytesIO(binary)))
                await bot.send_media_group(
                    (await Config.get(id=1)).group,
                    media
                )

                await bot.send_message(
                    (await Config.get(id=1)).group,
                    text=user.message('moderate_tour').format(
                        direction=(await tour.direction).name,
                        name=tour.name,
                        description=tour.description,
                        included=tour.included,
                        terms=tour.terms,
                    ),
                    reply_markup=get_moderate_tour_keyboard(user, tour)
                )

        elif action == 'approve_tour':
            if tour.moderate:
                await bot.send_message(
                    user.telegram_id,
                    user.message('tour_accepted'),
                    reply_markup=get_back_to_tour_operator_keyboard(user, tour)
                )

    elif 'operator' in action:
        try:
            operator_id = int(data['id'])
            operator = await TourOperator.get(id=operator_id)
            user = await operator.user
        except DoesNotExist:
            if action == 'decline_operator':
                user = await TelegramUser.get(telegram_id=operator_id)
                await bot.send_message(
                    operator_id,
                    user.message('operator_declined')
                )
            return web.HTTPNotFound()

        except ValueError:
            return web.HTTPNotFound()

        if action == 'approve_operator':
            if operator.moderate:
                login, password = create_admin_account(operator)
                admin_account = await User.get(email=login)
                operator.admin_account = admin_account
                await operator.save()
                await bot.send_message(
                    user.telegram_id,
                    user.message('operator_accepted').format(
                        login=login, password=password
                    )
                )

    return web.HTTPNotFound()
