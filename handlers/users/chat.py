from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE, tz
from db.models import TelegramUser, Chat, ChatMessage
from filters.filters import MainMenuExcludeFilter
from keyboards.inline.callbacks import chat_callback
from keyboards.inline.keyboards import get_chat_keyboard
from loader import dp, bot
from states.states import chat_state


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), chat_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def button_chat_chandler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    try:
        chat_id = int(callback_data['chat_id'])
        new_msg = int(callback_data['new_msg'])
        chat = await Chat.get(id=chat_id)
    except (ValueError, DoesNotExist):
        return

    data = await state.get_data()
    if await state.get_state() == chat_state.state and data.get('chat_id'):
        prev_state: str = data['prev_state']
        await callback.message.delete()
        if prev_state:
            await state.update_data(chat_id=None, chat_message_id=None, prev_state=None)
            await state.set_state(prev_state)
        else:
            await state.finish()
        return

    if new_msg:
        msg = await callback.message.answer(
            await chat.text(user),
            reply_markup=get_chat_keyboard(user, chat, True)
        )
    else:
        msg = callback.message
        await callback.message.edit_text(
            await chat.text(user),
            reply_markup=get_chat_keyboard(user, chat, True)
        )
    current_state = await state.get_state()
    await state.update_data(prev_state=current_state, chat_message_id=msg.message_id, chat_id=chat.id)
    await chat_state.set()
    return


@dp.message_handler(ChatTypeFilter([ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPER_GROUP, ChatType.SUPERGROUP]),
                    MainMenuExcludeFilter(), state=chat_state)
@dp.throttled(rate=FLOOD_RATE)
async def chat_handler(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return
    try:
        chat_id = (await state.get_data())['chat_id']
        message_id = (await state.get_data())['chat_message_id']
        chat = await Chat.get(id=chat_id)
    except (ValueError, DoesNotExist):
        return

    if await chat.customer == user:
        chat_id = await (await chat.seller).chat_id
        companion = await (await chat.seller).manager
        companion_name = (await chat.seller).name
        is_customer = True
    elif await (await chat.seller).manager == user:
        companion: TelegramUser = await chat.customer
        chat_id = companion.telegram_id
        companion_name = user.message('customer')
        is_customer = False
    else:
        return

    new_msg = await ChatMessage.create(
        chat=chat,
        text=message.text,
        time=datetime.now(tz),
        is_customer=is_customer
    )

    chat.datetime = datetime.now(tz)
    await chat.save()
    await message.delete()

    await bot.edit_message_text(
        await chat.text(user),
        user.telegram_id,
        message_id,
        reply_markup=get_chat_keyboard(user, chat, True)
    )

    companion_message = (await FSMContext(
        storage=dp.get_current().storage, chat=companion.telegram_id, user=companion.telegram_id
    ).get_data()).get('chat_message_id')

    if companion_message:
        await bot.edit_message_text(
            await chat.text(companion),
            chat_id,
            companion_message,
            reply_markup=get_chat_keyboard(user, chat, True)

        )
    else:
        await bot.send_message(
            chat_id,
            user.message('new_chat_message_form').format(
                time=new_msg.time,
                name=companion_name,
                text=new_msg.text,
                id_=chat.id
            ),
            reply_markup=get_chat_keyboard(user, chat, False)
        )


