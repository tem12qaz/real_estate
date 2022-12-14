from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE
from db.models import TelegramUser, Chat
from keyboards.inline.after_call import after_call_success_keyboard, after_call_all_info_keyboard
from keyboards.inline.callbacks import call_callback, after_call_callback
from loader import dp, supervisor, bot
from states.states import AfterCall


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), after_call_callback.filter(), state=AfterCall.all_states)
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

    current_state = await state.get_state()
    if current_state == AfterCall.success.state:
        if action == 'yes':
            await state.update_data(success=True)
            await callback.message.edit_text(
                user.message('after_call_all_info'),
                reply_markup=after_call_all_info_keyboard(user, chat)
            )
            await AfterCall.next()
        elif action == 'no':
            await callback.message.edit_text(
                user.message('after_call_finish'),
                reply_markup=None
            )
            seller = await chat.seller
            manager = await seller.manager
            await bot.send_message(
                seller.chat_id,
                manager.message('unsuccessful_contact').format(un=user.username)
            )
    elif current_state == AfterCall.all.state:
        if action == 'yes':
            await state.update_data(all='yes', text='')
            await callback.message.edit_text(
                user.message('after_call_type'),
                reply_markup=after_call_all_info_keyboard(user, chat)
            )
            await AfterCall.type.set()

        elif action == 'no' or action == 'partially':
            await state.update_data(all=action, chat_id=chat.id)
            await AfterCall.next()

            await callback.message.edit_text(
                user.message('after_call_text'),
                reply_markup=None
            )
    elif current_state == AfterCall.type.state:
        data = await state.get_data()
        seller = await chat.seller
        manager = await seller.manager
        await bot.send_message(
            seller.chat_id,
            manager.message('successful_contact').format(
                all=manager.message(data['all']),
                additional=manager.message(data['text']),
                type=manager.message(action),
            )
        )
        await callback.message.edit_text(
            user.message('after_call_finish'),
            reply_markup=None
        )


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=AfterCall.additional)
@dp.throttled(rate=FLOOD_RATE)
async def after_call_text_handler(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return

    try:
        chat_id = (await state.get_data()).get('chat_id')
        chat = await Chat.get(id=int(chat_id))
    except (ValueError, DoesNotExist):
        return

    await user.update_time()
    await state.update_data(text=f'"{message.text}"')
    await message.answer(
        user.message('after_call_type'),
        reply_markup=after_call_all_info_keyboard(user, chat)
    )
    await AfterCall.type.set()


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

    elif action in ('customer_declined', 'success'):
        user = await chat.customer
        await bot.send_message(
            user.telegram_id,
            user.message('after_call_form').format(chat_id=chat_id),
            reply_markup=after_call_success_keyboard(user, chat)
        )

    await callback.message.delete()
