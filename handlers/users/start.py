from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, ChatTypeFilter
from aiogram.types import ChatType

from data.config import FLOOD_RATE
from db.models import TelegramUser, Object
from keyboards.default.keyboard import get_main_keyboard
from loader import dp


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), CommandStart(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def bot_start(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    await state.finish()

    if user is None:
        args = message.get_args()
        user = await TelegramUser.create(telegram_id=message.from_user.id,
                                         username=message.from_user.username)

        if 'object_' in args:
            try:
                object_estate = await Object.get_or_none(telegram_id=int(args.replace('object_', '')))
            except ValueError:
                pass
            else:
                await send_tour_card(user, tour, message, None)
                return

    await message.answer(
        user.message('start_message'),
        reply_markup=get_main_keyboard(user)
    )
