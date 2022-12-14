from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType

from data.config import FLOOD_RATE
from db.models import TelegramUser
from keyboards.inline.callbacks import call_callback, after_call_callback
from loader import dp


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), after_call_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def after_call_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    action = callback_data.get('action')
    chat_id = callback_data.get('chat_id')
