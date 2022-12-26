from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from data.config import TG_URL
from db.models import TelegramUser, Config, Object, Chat, Developer
from keyboards.inline.callbacks import language_callback, main_menu_callback, empty_callback, list_objects_callback, \
    open_object_callback, filter_district_callback, select_price_callback, \
    object_callback, object_photos_callback, delete_message_callback, form_callback, chat_callback, call_callback, \
    after_call_callback


def select_language_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=user.button('en'), callback_data=language_callback.new(
                    language='en'
                )),
                InlineKeyboardButton(text=user.button('ru'), callback_data=language_callback.new(
                    language='ru'
                )),
            ]
        ]
    )
    return keyboard


async def get_support_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=user.button('contact'),
                                     url=TG_URL.format(un=(await Config.get(id=1)).support)),

            ],
            [
                InlineKeyboardButton(text=user.button('main_menu'), callback_data=main_menu_callback.new(
                    _='_'
                )),
            ]
        ]
    )
    return keyboard


def get_list_objects_keyboard(user: TelegramUser,
                              estate: Object | None,
                              all_count: int,
                              page: int = 0) -> InlineKeyboardMarkup | None:
    empty = empty_callback.new(_='_')
    if estate:
        inline_keyboard = [
            [InlineKeyboardButton(text=user.button('open_object'), callback_data=open_object_callback.new(
                object_id=estate.id
            ))],
            [
                InlineKeyboardButton(
                    text=user.button('previous'),
                    callback_data=list_objects_callback.new(page=(page - 1) if page != 0 else (all_count - 1))
                ),
                InlineKeyboardButton(text=f'{page + 1}/{all_count}', callback_data=empty),
                InlineKeyboardButton(
                    text=user.button('next'),
                    callback_data=list_objects_callback.new(page=(page + 1) if page != all_count - 1 else 0)
                ),
            ],
            # [InlineKeyboardButton(text=user.button('filter_date'), callback_data=filter_date_callback.new(_='_'))],
            [InlineKeyboardButton(text=user.button('filter_price'),
                                  callback_data=select_price_callback.new(price='_'))],
            [InlineKeyboardButton(text=user.button('filter_district'),
                                  callback_data=filter_district_callback.new(page=0))],
            [
                InlineKeyboardButton(
                    text=user.button('main_menu'),
                    callback_data=main_menu_callback.new(
                        _='_'
                    )
                )
            ]

        ]
    else:
        inline_keyboard = [
            # [InlineKeyboardButton(text=user.button('filter_date'), callback_data=filter_date_callback.new(_='_'))],
            [InlineKeyboardButton(text=user.button('filter_price'),
                                  callback_data=select_price_callback.new(price='_'))],
            [InlineKeyboardButton(text=user.button('filter_district'),
                                  callback_data=filter_district_callback.new(_='_'))],
            [
                InlineKeyboardButton(
                    text=user.button('main_menu'),
                    callback_data=main_menu_callback.new(
                        _='_'
                    )
                )
            ]
        ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def object_keyboard(estate: Object, user: TelegramUser, photo_index: int) -> InlineKeyboardMarkup:
    photos = await estate.photos
    inline_keyboard = [
        [
            InlineKeyboardButton(text=user.button('previous'), callback_data=object_photos_callback.new(
                photo_index=(photo_index - 1) if photo_index != 0 else (len(photos) - 1),
                object_id=estate.id,
            )),
            InlineKeyboardButton(text=f'{photo_index + 1}/{len(photos)}', callback_data=empty_callback.new(_='_')),
            InlineKeyboardButton(text=user.button('next'), callback_data=object_photos_callback.new(
                photo_index=(photo_index + 1) if photo_index != (len(photos) - 1) else 0,
                object_id=estate.id,
            )),
        ],
        # [
        #     InlineKeyboardButton(text=user.button('en'), callback_data=object_callback.new(
        #         object_id=estate.id, action='presentation'
        #     )),
        # ],
        [
            InlineKeyboardButton(text=user.button('chat'), callback_data=object_callback.new(
                object_id=estate.id, action='chat'
            )),
        ],
        [
            InlineKeyboardButton(text=user.button('call'), callback_data=object_callback.new(
                object_id=estate.id, action='call'
            )),
        ],
        [
            InlineKeyboardButton(text=user.button('video'), callback_data=object_callback.new(
                object_id=estate.id, action='video'
            )),
        ],
        [
            InlineKeyboardButton(text=user.button('back'), callback_data=object_callback.new(
                action='back', object_id=estate.id
            )),
        ]
    ]
    if await estate.files:
        inline_keyboard.insert(
            1,
            [
                InlineKeyboardButton(text=user.button('files'), callback_data=object_callback.new(
                    action='files', object_id=estate.id
                )),
            ]
        )

    if estate.presentation_path:
        inline_keyboard.insert(
            1,
            [
                InlineKeyboardButton(text=user.button('get_presentation'), callback_data=object_callback.new(
                    action='presentation', object_id=estate.id
                )),
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def delete_message_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('close'),
                    callback_data=delete_message_callback.new(
                        _='_'
                    )
                )
            ]
        ]
    )
    return keyboard


def form_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('back'),
                    callback_data=form_callback.new(
                        action='back'
                    )
                )
            ]
        ]
    )
    return keyboard


def bool_form_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user.button('yes'),
                    callback_data=form_callback.new(
                        action='yes'
                    )
                ),
                InlineKeyboardButton(
                    text=user.button('no'),
                    callback_data=form_callback.new(
                       action='no'
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text=user.button('back'),
                    callback_data=form_callback.new(
                        action='back'
                    )
                )
            ]
        ]
    )
    return keyboard


async def get_chat_keyboard(user: TelegramUser, chat: Chat, active: bool = False) -> InlineKeyboardMarkup:
    text = user.button('open_chat') if not active else user.button('close_chat')
    inline_keyboard = [
        [
            InlineKeyboardButton(text=text, callback_data=chat_callback.new(
                chat_id=chat.id, new_msg=0
            ))
        ]
    ]
    if active and user == await (await chat.seller).manager:
        inline_keyboard.insert(
            0,
            [
                InlineKeyboardButton(text=user.button('call_now'), callback_data=call_callback.new(
                    companion_id=(await chat.customer).telegram_id, chat_id=chat.id, action='call'
                ))
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def call_answer_keyboard(user: TelegramUser, chat: Chat) -> InlineKeyboardMarkup:
    companion = await (await chat.seller).manager
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=user.button('accept_call'), callback_data=call_callback.new(
                    companion_id=companion.telegram_id, chat_id=chat.id, action='accept'
                ))
            ],
            [
                InlineKeyboardButton(text=user.button('reject_call'), callback_data=call_callback.new(
                    companion_id=companion.telegram_id,chat_id=chat.id, action='reject'
                ))
            ]
        ]
    )
    return keyboard


async def support_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    config = await Config.get(id=1)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=user.button('contact'), url=TG_URL.format(un=config.support)),
            ]
        ]
    )
    return keyboard


def connect_meet(user: TelegramUser, url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=user.button('connect_meet'),
            web_app=WebAppInfo(url=url)
        )]]
    )
    return keyboard


async def call_chat_keyboard(user: TelegramUser, chat: Chat) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=user.button('call_now'), callback_data=call_callback.new(
                    companion_id=(await chat.customer).telegram_id, chat_id=chat.id, action='call'
                ))
            ],
            [
                InlineKeyboardButton(text=user.button('open_chat'), callback_data=chat_callback.new(
                    chat_id=chat.id, new_msg=0
                ))
            ]
        ]
    )
    return keyboard


async def chats_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for chat in await user.chats:
        seller = await chat.seller
        estate = await chat.object
        inline_keyboard.append(
            [
                InlineKeyboardButton(text=seller.name + ' ' + estate.name, callback_data=chat_callback.new(
                    chat_id=chat.id, new_msg=0
                ))
            ]
        )
    inline_keyboard.append(
        [
            InlineKeyboardButton(text=user.button('main_menu'), callback_data=main_menu_callback.new(
                _='_'
            )),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def group_chats_keyboard(developer: Developer) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for chat in await developer.chats:
        estate = await chat.object
        inline_keyboard.append(
            [
                InlineKeyboardButton(text='Chat id' + str(chat.id) + ' ' + estate.name, callback_data=chat_callback.new(
                    chat_id=chat.id, new_msg=0
                ))
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



