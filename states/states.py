from aiogram.dispatcher.filters.state import StatesGroup, State


class FilterObjects(StatesGroup):
    default = State()
    date = State()
    district = State()
    price = State()
