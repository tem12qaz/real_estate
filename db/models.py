import enum

from flask_security import UserMixin, RoleMixin
from tortoise import fields
from tortoise.fields import SET_NULL
from tortoise.models import Model


class Developer(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(128)
    manager = fields.OneToOneField('models.TelegramUser', related_name='developer_manager')
    director = fields.OneToOneField('models.TelegramUser', related_name='developer_director')
    chat_id = fields.CharField(32)
    photo = fields.CharField(128)
    message = fields.TextField()
    rating = fields.FloatField(default=5.)


class TelegramUser(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(128, unique=True, null=True)
    lang = fields.CharField(4, default='en')

    def message(self, name: str) -> str:
        return Message._messages[name][self.lang]

    def button(self, name: str) -> str:
        return Button._buttons[name][self.lang]


class ActionsEnum(enum.Enum):
    open = 'open'
    presentation = 'presentation'
    photo_video = 'photo_video'
    message = 'message'
    link = 'link'
    video_call = 'video call'


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
    _buttons: dict[str, dict[str, str]] = {}

    @classmethod
    async def from_name(cls, name: str, lang: str) -> str | None:
        return getattr(await cls.get_or_none(name=name), lang)

    @classmethod
    async def reload(cls):
        buttons = await cls.all()
        for button in buttons:
            cls._buttons[button.name] = {'ru': button.ru}


class Photo(Model):
    id = fields.IntField(pk=True)
    path = fields.CharField(128)
    tour = fields.ForeignKeyField('models.Object', related_name='photos', index=True)


class Files(Model):
    id = fields.IntField(pk=True)
    path = fields.CharField(128)
    tour = fields.ForeignKeyField('models.Object', related_name='files', index=True)


class Object(Model):
    id = fields.IntField(pk=True)
    owner = fields.ForeignKeyField('models.Developer', related_name='tours', index=True)
    price = fields.IntField()
    district = fields.CharField(256)
    date = fields.DateField()
    roi = fields.IntField()
    presentation_path = fields.CharField(128)


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
    support_url = fields.CharField(128)
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
