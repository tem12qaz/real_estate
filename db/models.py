import datetime
import enum
import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from flask_security import UserMixin, RoleMixin
from tortoise import fields
from tortoise.fields import SET_NULL
from tortoise.models import Model

from data.config import NEWLINE, BASE_PATH, tz
from loader import bot
from states.states import chat_state
from utils.actions_type import ActionsEnum
from utils.date_formatter import date_formatter


class Developer(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(128)
    manager = fields.OneToOneField('models.TelegramUser', related_name='developer_manager')
    # director = fields.OneToOneField('models.TelegramUser', related_name='developer_director')
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

    last_message = fields.DatetimeField(default=datetime.datetime.now())
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
    ru = fields.TextField(null=True)
    en = fields.TextField(null=True)
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
    ru = fields.CharField(128, null=True)
    en = fields.CharField(128,null=True)
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
    name = fields.CharField(128)
    active = fields.BooleanField(default=True)
    sale = fields.BooleanField(default=False)

    async def preview_text(self, user: TelegramUser):
        text = user.message('object_preview').format(
            name=self.name,
            price=self.price, date=date_formatter(self.date),
            district=(await self.district).name, roi=self.roi, owner=(await self.owner).name
        )
        return text

    async def text(self, user: TelegramUser):
        rating_info = user.message('rating_text').format(
            rating=(await self.owner).rating
        )
        orders_info = user.message('successful_orders_text').format(
            orders=(await self.owner).orders
        )
        additional_text = rating_info + NEWLINE + orders_info
        text = user.message('object_text').format(

            price=self.price, date=self.date, district=(await self.district).name,
            roi=self.roi, owner=(await self.owner).name,
            additional=additional_text, name=self.name
        )
        return text

    async def send_message(self, user: TelegramUser, message: types.Message, state: FSMContext):
        from keyboards.inline.keyboards import object_keyboard

        if not (await Action.get_or_none(user=user, object=self, developer=await self.owner, type=ActionsEnum.open)):
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

    async def send_contact(self, user: TelegramUser, message: types.Message, contact: str, state: FSMContext):
        seller = await self.owner
        companion = await seller.manager

        text_form = user.message('form_chat').format(
            experience=companion.button('yes') if user.experience else companion.button('no'),
            bali_only=companion.button('yes') if user.bali_only else companion.button('no'),
            features=companion.button('yes') if user.features else companion.button('no'),
            on_bali_now=companion.button('yes') if user.on_bali_now else companion.button('no'),
            budget=user.budget
        )

        if contact == 'chat':
            from keyboards.inline.keyboards import get_chat_keyboard

            chat = await Chat.get_or_none(customer=user, seller=seller, object=self)
            if not chat:
                chat = await Chat.create(
                    customer=user, seller=seller, object=self, datetime=datetime.datetime.now(tz)
                )

                await ChatMessage.create(
                    chat=chat, text=text_form, time=datetime.datetime.now(tz), is_customer=True
                )
                await ChatMessage.create(
                    chat=chat, text=seller.message, time=datetime.datetime.now(tz), is_customer=False
                )
                await bot.send_message(
                    seller.chat_id,
                    text_form,
                    reply_markup=await get_chat_keyboard(user, chat, False)
                )

            message = await message.answer(
                await chat.text(user),
                reply_markup=await get_chat_keyboard(user, chat, True)
            )
            await state.update_data(chat_message_id=message.message_id, chat_id=chat.id)
            await chat_state.set()

        elif contact == 'call':
            from keyboards.inline.keyboards import call_chat_keyboard

            chat = await Chat.get_or_none(customer=user, seller=seller, object=self)
            if not chat:
                chat = await Chat.create(
                    customer=user, seller=seller, object=self, datetime=datetime.datetime.now(tz)
                )

            await ChatMessage.create(
                chat=chat, text=text_form, time=datetime.datetime.now(tz), is_customer=True
            )
            await ChatMessage.create(
                chat=chat, text=seller.message, time=datetime.datetime.now(tz), is_customer=False
            )

            await message.answer(
                user.message('request_sent')
            )
            await bot.send_message(
                seller.chat_id,
                text_form,
                reply_markup=await call_chat_keyboard(companion, chat)
            )
        elif contact == 'video':
            pass


class Config(Model):
    id = fields.IntField(pk=True)
    support = fields.CharField(128)
    # group = fields.CharField(128)


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
    object = fields.ForeignKeyField('models.Object', related_name='chats', index=True)
    call_rejected = fields.BooleanField(default=False)
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
