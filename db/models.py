import datetime
import enum
import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from flask_security import UserMixin, RoleMixin
from tortoise import fields
from tortoise.fields import SET_NULL
from tortoise.models import Model

from data.config import NEWLINE, BASE_PATH
from keyboards.inline.keyboards import object_keyboard
from utils.actions_type import ActionsEnum


class Developer(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(128)
    manager = fields.OneToOneField('models.TelegramUser', related_name='developer_manager')
    director = fields.OneToOneField('models.TelegramUser', related_name='developer_director')
    chat_id = fields.CharField(32)
    photo = fields.CharField(128)
    message = fields.TextField()
    rating = fields.FloatField(default=5., null=True)
    successful_orders = fields.IntField(null=True)


class TelegramUser(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(128, unique=True, null=True)
    lang = fields.CharField(4, default='en')

    experience = fields.BooleanField(null=True)
    bali_only = fields.BooleanField(null=True)
    features = fields.BooleanField(null=True)
    on_bali_now = fields.BooleanField(null=True)
    budget = fields.BigIntField(null=True)

    last_message = fields.DatetimeField()
    state = fields.CharField(16, default='start')

    def message(self, name: str) -> str:
        return Message._messages[name][self.lang]

    def button(self, name: str) -> str:
        return Button._buttons[name][self.lang]

    async def update_time(self):
        self.last_message = datetime.datetime.now()
        await self.save()


class Action(Model):
    id = fields.IntField(pk=True)
    type = fields.CharEnumField(ActionsEnum)
    developer = fields.ForeignKeyField('models.Developer', related_name='actions', index=True)
    user = fields.ForeignKeyField('models.TelegramUser', related_name='actions', index=True)
    object = fields.ForeignKeyField('models.Object', related_name='actions', index=True)


class Message(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(64, unique=True, index=True)
    ru = fields.TextField()
    en = fields.TextField()
    _messages: dict[str, dict[str, str]] = {}

    @classmethod
    async def from_name(cls, name: str, lang: str) -> str | None:
        return getattr(await cls.get_or_none(name=name), lang)

    @classmethod
    async def reload(cls):
        messages = await cls.all()
        for message in messages:
            cls._messages[message.name] = {'ru': message.ru}


class Button(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(64, unique=True, index=True)
    ru = fields.CharField(128)
    en = fields.CharField(128)
    _buttons: dict[str, dict[str, str]] = {}

    @classmethod
    async def from_name(cls, name: str, lang: str) -> str | None:
        return getattr(await cls.get_or_none(name=name), lang)

    @classmethod
    async def reload(cls):
        buttons = await cls.all()
        for button in buttons:
            cls._buttons[button.name] = {'ru': button.ru}


class District(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(128)


class Photo(Model):
    id = fields.IntField(pk=True)
    path = fields.CharField(128)
    object = fields.ForeignKeyField('models.Object', related_name='photos', index=True)


class File(Model):
    id = fields.IntField(pk=True)
    path = fields.CharField(128)
    object = fields.ForeignKeyField('models.Object', related_name='files', index=True)


class Object(Model):
    id = fields.IntField(pk=True)
    owner = fields.ForeignKeyField('models.Developer', related_name='objects', index=True)
    district = fields.ForeignKeyField('models.District', related_name='objects', index=True)
    price = fields.IntField()
    date = fields.DateField()
    roi = fields.IntField()
    presentation_path = fields.CharField(128, null=True)
    active = fields.BooleanField(default=True)
    sale = fields.BooleanField(default=False)

    async def preview_text(self, user: TelegramUser):
        text = user.message('object_preview').format(
            price=self.price, date=self.date, district=self.district, roi=self.roi, owner=(await self.owner).name
        )
        return text

    async def text(self, user: TelegramUser):
        rating_info = user.message('rating_text').format(
            rating=(await self.owner).rating
        )
        orders_info = user.message('successful_orders_text').format(
            rating=(await self.owner).rating
        )
        additional_text = rating_info + NEWLINE + orders_info
        text = user.message('object_text').format(
            price=self.price, date=self.date, district=self.district,
            roi=self.roi, owner=(await self.owner).name,
            additional=additional_text
        )
        return text

    async def send_message(self, user: TelegramUser, message: types.Message, state: FSMContext):
        if not (await Action.get(user=user, object=self, developer=await self.owner, type=ActionsEnum.open)):
            await Action.create(
                user=user, object=self, developer=await self.owner, type=ActionsEnum.open
            )
        with open(BASE_PATH + (await self.photos)[0].path, 'rb') as f:
            binary = f.read()
        text_message = await message.answer(
            await self.text(user)
        )
        await state.update_data(text_message=text_message.message_id)

        await message.answer_photo(
            io.BytesIO(binary),
            reply_markup=await object_keyboard(self, user, 0)
        )

        await message.delete()


    async def send_contact(self, user: TelegramUser, message: types.Message, contact: str):
        if contact == ''


class Order(Model):
    id = fields.IntField(pk=True)
    date = fields.ForeignKeyField('models.Date', related_name='orders', index=True, on_delete=SET_NULL, null=True)
    tour = fields.ForeignKeyField('models.Object', related_name='orders', index=True, on_delete=SET_NULL, null=True)
    promo = fields.ForeignKeyField('models.PromoCode', related_name='orders', on_delete=SET_NULL, null=True)
    customer = fields.ForeignKeyField('models.TelegramUser', related_name='orders',
                                      index=True, on_delete=SET_NULL, null=True)
    seller = fields.ForeignKeyField('models.Developer', related_name='orders',
                                    index=True, on_delete=SET_NULL, null=True)
    datetime = fields.DatetimeField()
    places = fields.SmallIntField()
    paid = fields.IntField()
    remainder = fields.IntField()
    tax = fields.IntField()
    state = fields.CharField(8)
    url = fields.CharField(256, null=True)


class Config(Model):
    id = fields.IntField(pk=True)
    support = fields.CharField(128)
    group = fields.CharField(128)
    tax = fields.IntField()


class ChatMessage(Model):
    id = fields.IntField(pk=True)
    chat = fields.ForeignKeyField('models.Chat', related_name='messages')
    text = fields.TextField()
    time = fields.DatetimeField()
    is_customer = fields.BooleanField()


class Chat(Model):
    id = fields.IntField(pk=True)
    customer = fields.ForeignKeyField('models.TelegramUser', related_name='chats', index=True)
    seller = fields.ForeignKeyField('models.Developer', related_name='chats', index=True)
    datetime = fields.DatetimeField()

    async def text(self, user: TelegramUser) -> str:
        operator = await self.seller
        if user == await operator.user:
            companion = user.message('customer')
            is_customer = False
        else:
            is_customer = True
            companion = operator.full_name

        messages_ = ''
        messages: list[ChatMessage] = await self.messages
        if messages:
            for mess in messages:
                messages_ += user.message('chat_message_form').format(
                    time=str(mess.time)[:19],
                    name=user.message('you') if mess.is_customer is is_customer else companion,
                    text=mess.text
                )
        else:
            messages_ = user.message('no_messages')
        text = user.message('chat_form').format(
            id_=self.id,
            messages=messages_
        )
        return text


# --------------------FLASK_SECURITY---------------------------


class User(Model, UserMixin):
    id = fields.IntField(pk=True)
    email = fields.CharField(255, unique=True)
    first_name = fields.CharField(255)
    password = fields.CharField(255)
    active = fields.BooleanField()
    roles = fields.ManyToManyField(
        'models.Role', related_name='users', through='roles_users'
    )


class Role(Model, RoleMixin):
    id = fields.IntField(pk=True)
    name = fields.CharField(80, unique=True)
    description = fields.CharField(255)

#
# class TourUser(Model, UserMixin):
#     id = fields.IntField(pk=True)
#     first_name = fields.CharField(255)
#     email = fields.CharField(255, unique=True)
#     password = fields.CharField(255)
#     active = fields.BooleanField()
#     roles = fields.ManyToManyField(
#         'models.TourRole', related_name='users', through='roles_users_tours'
#     )
#
#
# class TourRole(Model, RoleMixin):
#     id = fields.IntField(pk=True)
#     name = fields.CharField(80, unique=True)
#     description = fields.CharField(255)
