from aiogram.dispatcher.filters.state import StatesGroup, State


class FilterObjects(StatesGroup):
    default = State()
    date = State()
    district = State()
    price = State()


class StartForm(StatesGroup):
    experience = State()
    bali_only = State()
    features = State()
    on_bali_now = State()
    budget = State()
