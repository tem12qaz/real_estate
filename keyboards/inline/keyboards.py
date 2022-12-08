from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import TG_URL
from db.models import TelegramUser, Config, Object
from keyboards.inline.callbacks import language_callback, main_menu_callback, empty_callback, list_objects_callback, \
    open_object_callback, filter_date_callback, filter_price_callback, filter_district_callback, select_price_callback


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
                tour_id=estate.id
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
            [InlineKeyboardButton(text=user.button('filter_date'), callback_data=filter_date_callback.new(_='_'))],
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
            [InlineKeyboardButton(text=user.button('filter_date'), callback_data=filter_date_callback.new(_='_'))],
            [InlineKeyboardButton(text=user.button('filter_price'), callback_data=filter_price_callback.new(_='_'))],
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
