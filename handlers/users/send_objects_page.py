import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from tortoise.queryset import QuerySet

from data.config import BASE_PATH
from db.filter_objects import filter_objects
from db.models import TelegramUser
from keyboards.inline.keyboards import get_list_objects_keyboard
from states.states import FilterObjects


async def send_objects_page(message: types.Message, user: TelegramUser,
                            state: FSMContext, callback: types.CallbackQuery = None) -> bool:
    data = await state.get_data()

    date = data.get('date')
    districts_id_list = data.get('districts_id')
    sales = data.get('sales')
    price = data.get('price')
    page = data.get('page')
    if not page:
        page = 0

    queryset: QuerySet = filter_objects(sales, date, districts_id_list, price)
    objs = (await queryset.limit((page + 1) + 1))[page:]
    if not objs:
        if callback:
            await callback.answer(user.message('no_objects'), show_alert=True)
        else:
            await message.answer(
                user.message('no_objects')
            )
        return False
    elif callback:
        await callback.answer()
    all_count = len(await queryset.all())
    keyboard = get_list_objects_keyboard(user, objs[0], all_count, page)

    if objs[:1]:
        text = await objs[0].preview_text(user)

        with open(BASE_PATH + (await objs[0].photos)[0].path, 'rb') as f:
            binary = f.read()

        if message.from_user.id == message.chat.id or await state.get_state() != FilterObjects.default.state:
            await message.answer_photo(
                photo=io.BytesIO(binary), caption=text, reply_markup=keyboard
            )
            await message.delete()
        else:
            await message.edit_media(
                media=InputMediaPhoto(media=io.BytesIO(binary), caption=text),
                reply_markup=keyboard
        )
    else:
        if message.from_user.id == message.chat.id or await state.get_state() != FilterObjects.default.state:
            await message.answer(
                text=user.message('no_objects'), reply_markup=keyboard
            )
            await message.delete()

    await FilterObjects.default.set()
    return True

