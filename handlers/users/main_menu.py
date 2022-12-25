import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType, InputFile, InputMediaPhoto
from tortoise.queryset import QuerySet

from data.config import FLOOD_RATE, BASE_PATH
from db.filter_objects import filter_objects
from db.models import TelegramUser, Object
from handlers.users.send_objects_page import send_objects_page
from keyboards.default.keyboard import get_main_keyboard
from keyboards.inline.callbacks import main_menu_callback
from keyboards.inline.keyboards import get_support_keyboard, get_list_objects_keyboard, chats_keyboard, \
    select_language_keyboard
from loader import dp
from states.states import FilterObjects


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def main_menu_handler(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return

    await user.update_time()

    if message.text == user.button('find') or message.text == user.button('sales') or \
            message.text == '/find' or message.text == '/sales':
        await state.finish()
        await FilterObjects.first()
        if message.text == user.button('find') or message.text == '/find':
            sales = False
        else:
            sales = True

        await state.update_data(sales=sales, page=0)
        await send_objects_page(message, user, state)
        return

    elif message.text == user.button('chats') or message.text == '/chats':
        await state.finish()

        text = user.message('chats')
        keyboard = await chats_keyboard(user)

    elif message.text == user.button('support') or message.text == '/support':
        keyboard = await get_support_keyboard(user)
        text = user.message('support')

    elif message.text == user.button('language') or message.text == '/language':
        keyboard = select_language_keyboard(user)
        text = user.message('select_language')

    else:
        return

    await message.answer(
        text,
        reply_markup=keyboard
    )


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), main_menu_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def go_to_main_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    await state.finish()
    await callback.answer()
    await callback.message.answer(
        text=user.message('start_message'),
        reply_markup=get_main_keyboard(user)
    )
    await callback.message.delete()
