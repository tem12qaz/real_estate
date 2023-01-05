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


class AfterCall(StatesGroup):
    success = State()
    all = State()
    additional = State()
    call = State()
    type = State()


chat_state = State('chat_state')
