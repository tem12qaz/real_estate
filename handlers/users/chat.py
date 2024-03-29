from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import ChatType
from tortoise.exceptions import DoesNotExist

from data.config import FLOOD_RATE, tz, MEET_REDIRECT_PATH, HOST
from db.models import TelegramUser, Chat, ChatMessage
from filters.filters import MainMenuExcludeFilter
from keyboards.inline.callbacks import chat_callback, call_callback
from keyboards.inline.keyboards import get_chat_keyboard, call_answer_keyboard, connect_meet
from loader import dp, bot
from states.states import chat_state
from utils.google_meet import get_meet_url
from utils.supervisor import supervisor


@dp.callback_query_handler(ChatTypeFilter([ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP]), call_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def call_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    try:
        companion_id = int(callback_data['companion_id'])
        chat_id = int(callback_data['chat_id'])
        companion = await TelegramUser.get(telegram_id=companion_id)
        chat = await Chat.get(id=chat_id)
    except (ValueError, DoesNotExist):
        await callback.answer()
        return

    if user == await chat.customer:
        chat_id = (await chat.seller).chat_id
        is_customer = True
    else:
        chat_id = (await chat.customer).telegram_id
        is_customer = False

    action = callback_data['action']

    if action == 'call' and int(user.telegram_id) in map(lambda x: x.user.id, await bot.get_chat_administrators((await chat.seller).chat_id)):
        await callback.answer(user.message('wait_answer'), show_alert=True)
        await bot.send_message(
            companion.telegram_id,
            companion.message('call_answer').format(object=(await chat.object).name),
            reply_markup=await call_answer_keyboard(user, chat)
        )
    elif action == 'accept':
        supervisor.after_call(chat)
        chat.call_rejected = False
        await chat.save()
        url_ = get_meet_url()[-12:]
        url = HOST + MEET_REDIRECT_PATH.format(chat_id=chat.id, meet=url_)
        await callback.message.edit_text(
            user.message('connect_meet').format(url=url),
            reply_markup=connect_meet(user, url)
        )
        # await bot.send_message(
        #     (await(await chat.seller).manager).telegram_id,
        #     # chat_id,
        #     companion.message('connect_meet').format(url=url),
        #     reply_markup=connect_meet(companion, url)
        # )
        url = f'https://meet.google.com/{url_}/'
        await bot.send_message(
            chat_id,
            companion.message('connect_meet').format(url=url),
            reply_markup=connect_meet(companion, url)
        )
        # await bot.send_message(
        #     (await(await chat.seller).manager).telegram_id,
        #     companion.message('connect_meet').format(url=url),
        #     reply_markup=connect_meet(companion, url)
        # )

    elif action == 'reject':
        await callback.message.delete()
        chat.call_rejected = True
        await chat.save()
        supervisor.call_reject(chat)

        new_msg = await ChatMessage.create(
            chat=chat,
            text=f'<i>{companion.message("call_rejected")}</i>',
            time=datetime.now(tz),
            is_customer=is_customer
        )

        companion_message = (await FSMContext(
            storage=dp.get_current().storage, chat=chat_id, user=companion.telegram_id
        ).get_data()).get('chat_message_id')

        if companion_message:
            await bot.edit_message_text(
                await chat.text(companion),
                chat_id,
                companion_message,
                reply_markup=await get_chat_keyboard(user, chat, True, callback.message)

            )
        else:
            await bot.send_message(
                chat_id,
                user.message('new_chat_message_form').format(
                    time=new_msg.time,
                    name=user.message('customer'),
                    text=new_msg.text,
                    id_=chat.id,
                    estate=(await chat.object).name
                ),
                reply_markup=await get_chat_keyboard(user, chat, False, callback.message)
            )


@dp.callback_query_handler(ChatTypeFilter([ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP]), chat_callback.filter(), state='*')
@dp.throttled(rate=FLOOD_RATE)
async def button_chat_handler(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    await user.update_time()

    try:
        chat_id = int(callback_data['chat_id'])
        new_msg = int(callback_data['new_msg'])
        chat = await Chat.get(id=chat_id)
    except (ValueError, DoesNotExist):
        return

    data = await state.get_data()
    if await state.get_state() == chat_state.state and data.get('chat_id') and data.get('chat_id') == chat_id:
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
            reply_markup=await get_chat_keyboard(user, chat, True, callback.message)
        )
    else:
        msg = callback.message
        await callback.message.edit_text(
            await chat.text(user),
            reply_markup=await get_chat_keyboard(user, chat, True, callback.message)
        )
    current_state = await state.get_state()
    await state.update_data(prev_state=current_state, chat_message_id=msg.message_id, chat_id=chat.id)
    await chat_state.set()
    return


@dp.message_handler(ChatTypeFilter([ChatType.GROUP, ChatType.SUPERGROUP, ChatType.PRIVATE]),
                    MainMenuExcludeFilter(), state=chat_state)
@dp.throttled(rate=FLOOD_RATE)
async def chat_handler(message: types.Message, state: FSMContext):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return
    print('chat')

    await user.update_time()

    try:
        chat_id = (await state.get_data())['chat_id']
        message_id = (await state.get_data())['chat_message_id']
        chat = await Chat.get(id=chat_id)
    except (ValueError, DoesNotExist):
        return

    if await chat.customer == user:
        seller = await chat.seller
        chat_id = seller.chat_id
        companion = await seller.manager
        companion_name = user.message('customer')
        is_customer = True
    elif int(user.telegram_id) in map(lambda x: x.user.id, await bot.get_chat_administrators((await chat.seller).chat_id)):
        companion: TelegramUser = await chat.customer
        chat_id = companion.telegram_id
        companion_name = (await chat.seller).name

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
        message.chat.id,
        message_id,
        reply_markup=await get_chat_keyboard(user, chat, True, message)
    )

    companion_message = (await FSMContext(
        storage=dp.get_current().storage, chat=chat_id, user=companion.telegram_id
    ).get_data()).get('chat_message_id')

    if companion_message:
        await bot.edit_message_text(
            await chat.text(companion),
            chat_id,
            companion_message,
            reply_markup=await get_chat_keyboard(companion, chat, True, message)

        )
    else:
        await bot.send_message(
            chat_id,
            user.message('new_chat_message_form').format(
                time=new_msg.time,
                name=companion_name,
                text=new_msg.text,
                id_=chat.id,
                estate=(await chat.object).name
            ),
            reply_markup=await get_chat_keyboard(companion, chat, False, message)
        )
