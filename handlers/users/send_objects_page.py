import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from tortoise.queryset import QuerySet

from data.config import BASE_PATH
from db.filter_tours import filter_objects
from db.models import TelegramUser
from keyboards.inline.keyboards import get_list_objects_keyboard
from states.states import FilterObjects


def send_objects_page(message: types.Message, user: TelegramUser, state: FSMContext, page: int = 0) -> None:
    data = await state.get_data()

    date = data.get('date')
    districts_id_list = data.get('districts_id')
    sales = data.get('sales')
    price = data.get('price')

    queryset: QuerySet = filter_objects(sales, date, districts_id_list, price)
    objs = (await queryset.limit((page + 1) + 1))[page:]
    all_count = len(await queryset.all())

    if objs[:1]:
        text = await tours_message_text(user, objs, 0)

        keyboard = get_list_objects_keyboard(user, objs[0], all_count)
        with open(BASE_PATH + (await objs[0].photos)[0].path, 'rb') as f:
            binary = f.read()

        if message.from_user.id == message.chat.id and await state.get_state() != FilterObjects.default.state:
            await message.answer_photo(
                photo=io.BytesIO(binary), caption=text, reply_markup=keyboard
            )
            await message.delete()
        else:
            await message.edit_media(
                media=InputMediaPhoto(media=io.BytesIO(binary), caption=text),
                reply_markup=keyboard
        )
        await FilterObjects.default.set()
    else:
        await message.