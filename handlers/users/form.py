from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE
from db.models import TelegramUser, Object
from keyboards.inline.callbacks import open_object_callback, form_callback
from keyboards.inline.keyboards import bool_form_keyboard
from loader import dp
from states.states import FilterObjects, StartForm


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE),
                           form_callback.filter(), state=StartForm.all_states)
@dp.throttled(rate=FLOOD_RATE)
async def form_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    action = callback_data['action']
    current_state = await state.get_state()
    data = await state.get_data()
    object_id = data['object_id']

    try:
        estate = await Object.get(id=int(object_id))
    except (ValueError, DoesNotExist):
        await callback.answer('object_not_available')
        await callback.message.delete()
        return

    await callback.answer()

    if action == 'back':
        if current_state == StartForm.experience.state:
            await estate.send_message(user, callback.message, state)
            # await callback.message.delete()
            return

        else:
            await StartForm.previous()

    else:
        await state.update_data(
            {
                current_state.split(':')[1]: (True if action == 'yes' else False)
            }
        )
        await StartForm.next()

    await callback.message.edit_text(
        user.message((await state.get_state()).split(':')[1]),
        reply_markup=bool_form_keyboard(user)
    )


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=StartForm.budget)
@dp.throttled(rate=FLOOD_RATE)
async def budget_handler(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return

    await user.update_time()

    data = await state.get_data()
    contact = data['contact']

    try:
        estate = await Object.get(id=int(data['object_id']))
        budget = int(message.text)
        if budget <= 0 or budget > 1000000000000:
            raise ValueError

    except (ValueError, DoesNotExist):
        await message.delete()
        return

    user.experience = data['experience']
    user.bali_only = data['bali_only']
    user.features = data['features']
    user.on_bali_now = data['on_bali_now']
    user.budget = budget
    user.state = 'finish'
    await user.save()

