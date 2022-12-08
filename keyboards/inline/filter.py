from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import DISTRICTS_IN_COLUMN
from db.models import TelegramUser, District
from keyboards.inline.callbacks import empty_callback, district_callback, filter_district_callback, \
    list_objects_callback, districts_drop_callback, price_drop_callback, select_price_callback
from utils.price_buttons import PriceButtons


async def get_list_districts_keyboard(user: TelegramUser,
                                      districts: list[District],
                                      all_count: int,
                                      page: int = 0,
                                      state: FSMContext = None) -> InlineKeyboardMarkup:
    inline_keyboard = []
    if state:
        districts_id = (await state.get_data()).get('districts_id')
        if not districts_id:
            districts_id = []
    else:
        districts_id = []

    selected = user.button('selected')

    districts = districts[:DISTRICTS_IN_COLUMN]
    for i in range(0, len(districts), 2):
        if i != len(districts) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=districts[i].name + (selected if districts[i].id in districts_id else ''),
                        callback_data=district_callback.new(
                            district_id=districts[i].id, page=page
                        )
                    ),
                    InlineKeyboardButton(
                        text=districts[i + 1].name + (selected if districts[i + 1].id in districts_id else ''),
                        callback_data=district_callback.new(
                            district_id=districts[i + 1].id, page=page
                        )
                    )
                ],
            )
        else:
            InlineKeyboardButton(
                text=districts[i].name + (selected if districts[i].id in districts_id else ''),
                callback_data=district_callback.new(
                    district_id=districts[i].id, page=page
                )
            ),

    empty = empty_callback.new(_='_')
    pages_count = all_count // DISTRICTS_IN_COLUMN + 1 if all_count % DISTRICTS_IN_COLUMN != 0 else 0
    row = [
        InlineKeyboardButton(
            text=user.button('previous'),
            callback_data=filter_district_callback.new(page=(page - 1) if page != 0 else pages_count - 1)
        ),
        InlineKeyboardButton(
            text=f'{page + 1}/{pages_count}',
            callback_data=empty
        ),
        InlineKeyboardButton(
            text=user.button('next'),
            callback_data=filter_district_callback.new(page=(page + 1) if (page + 1) != pages_count else 0)
        ),
    ]
    inline_keyboard.append(row)

    inline_keyboard.append(
        [InlineKeyboardButton(text=user.button('apply'), callback_data=list_objects_callback.new(
            page=0
        ))]
    )

    # inline_keyboard.append(
    #     [InlineKeyboardButton(text=user.button('inline_search'), switch_inline_query_current_chat='')]
    # )

    inline_keyboard.append(
        [InlineKeyboardButton(text=user.button('drop_filter'), callback_data=districts_drop_callback.new(
            _='_'
        ))]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_price_keyboard(user: TelegramUser) -> InlineKeyboardMarkup:
    buttons = PriceButtons.buttons
    inline_keyboard = [
        [
            InlineKeyboardButton(text=user.button(buttons[0][0]), callback_data=select_price_callback.new(
                price=buttons[0][0]
            )),
            InlineKeyboardButton(text=user.button(buttons[1][0]), callback_data=select_price_callback.new(
                price=buttons[1][0]
            ))
         ],
        [
            InlineKeyboardButton(text=user.button(buttons[2][0]), callback_data=select_price_callback.new(
                price=buttons[2][0]
            )),
            InlineKeyboardButton(text=user.button(buttons[3][0]), callback_data=select_price_callback.new(
                price=buttons[3][0]
            ))
        ],
        [
            InlineKeyboardButton(text=user.button('drop_filter'), callback_data=price_drop_callback.new(
                _='_'
            ))
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
