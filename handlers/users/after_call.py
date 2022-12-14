from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE
from db.models import TelegramUser, Chat
from keyboards.inline.callbacks import call_callback, after_call_callback
from loader import dp, supervisor


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), after_call_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def after_call_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()
    await callback.answer()

    action = callback_data.get('action')
    try:
        chat_id = callback_data.get('chat_id')
        chat = await Chat.get(id=int(chat_id))
    except (ValueError, DoesNotExist):
        return

    if action == 'scheduled_a_call':
        await supervisor.after_call(chat, 86400)

    elif action in ('customer_declined', 'yes'):



    await callback.message.delete()
