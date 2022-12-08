import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType, InputMediaPhoto
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE, BASE_PATH
from db.models import TelegramUser, Object
from handlers.users.send_objects_page import send_objects_page
from keyboards.inline.callbacks import open_object_callback, object_photos_callback, object_callback
from keyboards.inline.keyboards import object_keyboard
from loader import dp, bot
from states.states import FilterObjects


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           open_object_callback.filter(), state=[FilterObjects.default, None])
@dp.throttled(rate=FLOOD_RATE)
async def open_object_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return
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


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           object_callback.filter(),
                           state=[FilterObjects.default, None])
@dp.throttled(rate=FLOOD_RATE)
async def object_card_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    object_id = int(callback_data['object_id'])
    action = callback_data['action']
    data = await state.get_data()

    estate = await Object.get(id=object_id)

    if not estate.active and action != 'back':
        await callback.answer(user.message('object_not_available'), show_alert=True)
        return

    if action == 'back':
        text_message = data.get('text_message')
        await bot.delete_message(
            user.telegram_id,
            text_message
        )
        await send_objects_page(callback.message, user, state)
        await callback.message.delete()



