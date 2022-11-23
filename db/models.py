from flask_security import UserMixin, RoleMixin
from tortoise import fields
from tortoise.fields import SET_NULL
from tortoise.models import Model


class TourOperator(Model):
    id = fields.IntField(pk=True)
    prepayment = fields.IntField(default=20)
    user = fields.OneToOneField('models.TelegramUser', related_name='operator')
    photo = fields.CharField(128)
    full_name = fields.CharField(256)
    about = fields.TextField()
    region = fields.CharField(64)
    city = fields.CharField(64)
    languages = fields.CharField(256)
    verified = fields.BooleanField(default=False)

    contact_fio = fields.CharField(128)
    experience = fields.SmallIntField()
    site = fields.CharField(256)

    moderate = fields.BooleanField(default=False)
    yookassa = fields.CharField(256, null=True)
    admin_account = fields.OneToOneField('models.User', related_name='operator', null=True, on_delete="SET NULL")

    # ukassa_data


class TelegramUser(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(128, unique=True, null=True)
    full_name = fields.CharField(256, null=True)
    phone = fields.BigIntField(null=True)
    city = fields.CharField(128, null=True)
    birthday = fields.DateField(null=True)
    lang = fields.CharField(4, default='ru')
    referer = fields.ForeignKeyField('models.TelegramUser', related_name='referrals',
                                     index=True, on_delete=SET_NULL, null=True)
    favorite = fields.ManyToManyField(
        'models.Tour', related_name='in_favorite', through='favorite_tours', on_delete=SET_NULL
    )

    def message(self, name: str) -> str:
        return Message._messages[name][self.lang]

    def button(self, name: str) -> str:
        return Button._buttons[name][self.lang]


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
    tour = fields.ForeignKeyField('models.Tour', related_name='photos', index=True)


class Direction(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(64)


class Tour(Model):
    id = fields.IntField(pk=True)
    owner = fields.ForeignKeyField('models.TourOperator', related_name='tours', index=True)
    direction = fields.ForeignKeyField('models.Direction', related_name='tours',
                                       index=True, on_delete=SET_NULL, null=True)
    name = fields.CharField(256)
    description = fields.TextField()
    included = fields.TextField()
    terms = fields.TextField()
    active = fields.BooleanField(default=True)
    moderate = fields.BooleanField(default=False)


class Date(Model):
    id = fields.IntField(pk=True)
    start = fields.DateField()
    end = fields.DateField()
    tour = fields.ForeignKeyField('models.Tour', related_name='dates', index=True)
    places = fields.SmallIntField()
    price = fields.IntField()
    sale = fields.IntField(default=0)


class Order(Model):
    id = fields.IntField(pk=True)
    date = fields.ForeignKeyField('models.Date', related_name='orders', index=True, on_delete=SET_NULL, null=True)
    tour = fields.ForeignKeyField('models.Tour', related_name='orders', index=True, on_delete=SET_NULL, null=True)
    promo = fields.ForeignKeyField('models.PromoCode', related_name='orders', on_delete=SET_NULL, null=True)
    customer = fields.ForeignKeyField('models.TelegramUser', related_name='orders',
                                  index=True, on_delete=SET_NULL, null=True)
    seller = fields.ForeignKeyField('models.TourOperator', related_name='orders',
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


class PromoCode(Model):
    id = fields.IntField(pk=True)
    percent = fields.SmallIntField()
    text = fields.CharField(32, unique=True)
    uses = fields.SmallIntField(null=True)
    uses_for_one = fields.SmallIntField(null=True)
    end = fields.DateField(null=True)


class PromoUses(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.TelegramUser', related_name='promos', index=True)
    promo_code = fields.ForeignKeyField('models.PromoCode', related_name='used', index=True)
    count = fields.SmallIntField(default=1)


class ChatMessage(Model):
    id = fields.IntField(pk=True)
    chat = fields.ForeignKeyField('models.Chat', related_name='messages')
    text = fields.TextField()
    time = fields.DatetimeField()
    is_customer = fields.BooleanField()


class Chat(Model):
    id = fields.IntField(pk=True)
    customer = fields.ForeignKeyField('models.TelegramUser', related_name='chats', index=True)
    seller = fields.ForeignKeyField('models.TourOperator', related_name='chats', index=True)
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
