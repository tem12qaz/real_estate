from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType

from data.config import FLOOD_RATE
from db.models import TelegramUser
from handlers.users.send_objects_page import send_objects_page
from keyboards.inline.callbacks import list_objects_callback
from loader import dp
from states.states import FilterObjects


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           list_objects_callback.filter(), state=FilterObjects.all_states)
@dp.throttled(rate=FLOOD_RATE)
async def list_tours_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    page = callback_data['page']
    page = int(page)
    await state.update_data(page=page)

    await send_objects_page(callback.message, user, state)

