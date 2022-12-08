from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType

from admin.models import TelegramUser
from data.config import FLOOD_RATE, DISTRICTS_IN_COLUMN
from db.models import District
from handlers.users.send_objects_page import send_objects_page
from keyboards.inline.callbacks import filter_district_callback, districts_drop_callback, district_callback, \
    select_price_callback
from keyboards.inline.filter import get_list_districts_keyboard, get_price_keyboard
from loader import dp
from states.states import FilterObjects


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), filter_district_callback.filter(),
                           state=FilterObjects.all_states)
@dp.throttled(rate=FLOOD_RATE)
async def list_districts_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    if (await state.get_data()).get('districts_id') is None:
        await state.update_data(districts_id=[])

    await callback.answer()

    page = int(callback_data['page'])
    await state.update_data(page=page)
    districts = await District.all().limit(((page+1) * DISTRICTS_IN_COLUMN) + 1)
    districts = districts[page * DISTRICTS_IN_COLUMN:]
    all_count = await District.all().count()

    if await state.get_state() == FilterObjects.district.state:
        await callback.message.edit_text(
            user.message('select_districts'),
            reply_markup=await get_list_districts_keyboard(user, districts, all_count, page, state)
        )
    else:
        mess = await callback.message.answer(
            user.message('select_districts'),
            reply_markup=await get_list_districts_keyboard(user, districts, all_count, page, state)
        )
        await state.update_data(mess_id=mess.message_id)
        await callback.message.delete()
        await FilterObjects.district.set()


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), districts_drop_callback.filter(),
                           state=FilterObjects.district)
@dp.throttled(rate=FLOOD_RATE)
async def districts_drop_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await state.update_data(directions_id=[])
    page = 0
    districts = await District.all().limit(((page + 1) * DISTRICTS_IN_COLUMN) + 1)
    districts = districts[page * DISTRICTS_IN_COLUMN:]
    all_count = await District.all().count()

    await callback.answer()
    await callback.message.edit_text(
        user.message('select_districts'),
        reply_markup=await get_list_districts_keyboard(user, districts, all_count, page, state)
    )


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), district_callback.filter(), state=FilterObjects.district)
@dp.throttled(rate=FLOOD_RATE)
async def select_district_handler(callback: types.CallbackQuery, callback_data: dict,  state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    district_id = int(callback_data.get('district_id'))
    page = int(callback_data.get('page'))
    async with state.proxy() as data:
        if district_id in data['district_id']:
            data['district_id'].remove(district_id)
        else:
            data['district_id'].append(district_id)

    districts = (await District.all().limit(((page + 1) * DISTRICTS_IN_COLUMN) + 1))
    districts = districts[page * DISTRICTS_IN_COLUMN:]
    all_count = await District.all().count()

    if not await state.get_state():
        state = None
    await callback.message.edit_text(
        user.message('select_districts'),
        reply_markup=await get_list_districts_keyboard(user, districts, all_count, page, state)
    )


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), select_price_callback.filter(),
                           state=FilterObjects.all_states)
@dp.throttled(rate=FLOOD_RATE)
async def filter_price_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await callback.answer()
    price = callback_data['price']

    if price == '_':
        await callback.message.answer(
            user.message('select_price'),
            reply_markup=get_price_keyboard(user)
        )
    else:
        await state.update_data(price=price)
        await send_objects_page(callback.message, user, state)



