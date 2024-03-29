from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, ChatTypeFilter
from aiogram.types import ChatType
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE
from db.models import TelegramUser, Object, Action
from keyboards.default.keyboard import get_main_keyboard
from keyboards.inline.callbacks import language_callback
from keyboards.inline.keyboards import select_language_keyboard
from loader import dp
from states.states import FilterObjects
from utils.actions_type import ActionsEnum
from utils.set_bot_commands import set_commands


@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), CommandStart(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def bot_start(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    await state.finish()
    args = message.get_args()

    if user is None:
        user = await TelegramUser.create(telegram_id=message.from_user.id,
                                         username=message.from_user.username, lang='ru')

        await Action.create(
            user=user, object=None, developer=None, type=ActionsEnum.start
        )
        if 'object_' in args:
            try:
                estate = await Object.get_or_none(id=int(args.replace('object_', '')))
            except ValueError:
                await message.answer(
                    user.message('select_language'),
                    reply_markup=select_language_keyboard(user)
                )
            else:
                await message.answer(
                    user.message('select_language'),
                    reply_markup=select_language_keyboard(user, estate.id, start=True)
                )
        else:
            await message.answer(
                user.message('select_language'),
                reply_markup=select_language_keyboard(user)
            )
        return

    await user.update_time()

    if 'object_' in args:
        try:
            estate = await Object.get_or_none(id=int(args.replace('object_', '')))
        except ValueError:
            pass
        else:
            await FilterObjects.default.set()
            await estate.send_message(user, message, state)
            return

    await message.answer(
        user.message('main_menu_message'),
        reply_markup=get_main_keyboard(user)
    )


@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), language_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def language_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    lang = callback_data['language']
    object_id = callback_data['object_id']
    start = callback_data['start']

    user.lang = lang
    await user.save()
    await set_commands(user)

    if object_id != '_':
        try:
            estate = await Object.get(id=int(object_id))
        except (ValueError, DoesNotExist):
            await callback.message.answer(
                user.message('start_message'),
                reply_markup=get_main_keyboard(user)
            )
        else:
            await FilterObjects.default.set()
            await estate.send_message(user, callback.message, state)
            return
    elif start == '_':
        await callback.message.answer(
            user.message('main_menu_message'),
            reply_markup=get_main_keyboard(user)
        )
        await callback.message.delete()
    else:
        await callback.message.answer(
            user.message('start_message'),
            reply_markup=get_main_keyboard(user)
        )
        await callback.message.delete()
