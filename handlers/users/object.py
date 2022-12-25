import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType, InputMediaPhoto, InputFile
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE, BASE_PATH
from db.models import TelegramUser, Object, Action
from handlers.users.send_objects_page import send_objects_page
from keyboards.inline.callbacks import open_object_callback, object_photos_callback, object_callback, \
    delete_message_callback
from keyboards.inline.keyboards import object_keyboard, delete_message_keyboard, bool_form_keyboard
from loader import dp, bot
from states.states import FilterObjects, StartForm
from utils.actions_type import ActionsEnum
from utils.supervisor import supervisor


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           open_object_callback.filter(), state=[FilterObjects.default, None])
@dp.throttled(rate=FLOOD_RATE)
async def open_object_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    obj_id = callback_data.get('object_id')
    try:
        estate = await Object.get(id=int(obj_id))
    except (DoesNotExist, ValueError):
        return
    await state.update_data(photo_index=0)

    await estate.send_message(user, callback.message, state)
    await FilterObjects.default.set()


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           object_photos_callback.filter(), state=[FilterObjects.default, None])
@dp.throttled(rate=FLOOD_RATE)
async def list_photos_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    photo_index = callback_data.get('photo_index')
    object_id = callback_data.get('object_id')
    try:
        estate = await Object.get(id=int(object_id))
    except (DoesNotExist, ValueError):
        return

    await state.update_data(photo_index=photo_index)

    with open(BASE_PATH + (await estate.photos)[int(photo_index)].path, 'rb') as f:
        binary = f.read()

    await callback.message.edit_media(
        InputMediaPhoto(io.BytesIO(binary)),
        reply_markup=await object_keyboard(estate, user, int(photo_index))
    )


@dp.callback_query_handler(delete_message_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def object_card_handler(callback: types.CallbackQuery):
    await callback.message.delete()


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           object_callback.filter(),
                           state=[FilterObjects.default, None])
@dp.throttled(rate=FLOOD_RATE)
async def object_card_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    object_id = int(callback_data['object_id'])
    action = callback_data['action']
    data = await state.get_data()

    estate = await Object.get(id=object_id)

    if not estate.active and action != 'back':
        await callback.answer(user.message('object_not_available'), show_alert=True)
        return

    if action == 'back':
        await callback.answer()
        text_message = data.get('text_message')
        await bot.delete_message(
            user.telegram_id,
            text_message
        )
        await send_objects_page(callback.message, user, state, callback)

    elif action == 'presentation':
        await callback.answer()

        if not (await Action.get_or_none(user=user, object=estate,
                                         developer=await estate.owner, type=ActionsEnum.presentation)):
            await Action.create(
                user=user, object=estate, developer=await estate.owner, type=ActionsEnum.presentation
            )
        await callback.message.answer_document(
            document=InputFile(BASE_PATH + estate.presentation_path),
            reply_markup=delete_message_keyboard(user)
        )

    elif action == 'files':
        await callback.answer()

        if not (await Action.get_or_none(user=user, object=estate,
                                         developer=await estate.owner, type=ActionsEnum.photo_video)):
            await Action.get_or_create(
                user=user, object=estate, developer=await estate.owner, type=ActionsEnum.photo_video
            )
        media = types.MediaGroup()
        i = 1
        files = await estate.files
        for file in files:
            if i == 10:
                await callback.message.answer_media_group(
                    media=media
                )
                media = types.MediaGroup()

            if file.path[-4:].lower() in ['.avi', '.mov', '.mkv', '.mp4', '.wmv']:
                with open(BASE_PATH + file.path, 'rb') as f:
                    media.attach_video(InputFile(io.BytesIO(f.read())))
            else:
                with open(BASE_PATH + file.path, 'rb') as f:
                    media.attach_photo(InputFile(io.BytesIO(f.read())))

            i += 1
            if file == files[-1]:
                await callback.message.answer_media_group(
                    media=media
                )

    elif action in ['chat', 'call', 'video']:
        await callback.answer()

        if not (await Action.get_or_none(user=user, object=estate,
                                         developer=await estate.owner, type=getattr(ActionsEnum, action))):
            await Action.create(
                user=user, object=estate, developer=await estate.owner, type=getattr(ActionsEnum, action)
            )

        if user.state != 'finish':
            user.state = 'form'
            await user.save()
            supervisor.form_notify(user)
            await StartForm.first()
            await state.update_data(contact=action, object_id=estate.id)
            text_message = data.get('text_message')
            await bot.delete_message(
                user.telegram_id,
                text_message
            )
            await callback.message.answer(
                user.message('experience'),
                reply_markup=bool_form_keyboard(user)
            )
            await callback.message.delete()
        else:
            await estate.send_contact(user, callback.message, action, state)
