from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref

from admin.flask_app_init import db
from utils.actions_type import ActionsEnum

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

# favorite_tours = db.Table(
#     'favorite_tours',
#     db.Column('telegramuser_id', db.Integer(), db.ForeignKey('telegramuser.id')),
#     db.Column('tour_id', db.Integer(), db.ForeignKey('ob.id'))
# )


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


class TelegramUser(db.Model):
    __tablename__ = 'telegramuser'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=True)
    lang = db.Column(db.String(4), default='ru')
    mail = db.Column(db.Boolean(), nullable=False, default=True)

    experience = db.Column(db.Boolean(), nullable=True)
    bali_only = db.Column(db.Boolean(), nullable=True)
    features = db.Column(db.Boolean(), nullable=True)
    on_bali_now = db.Column(db.Boolean(), nullable=True)
    budget = db.Column(db.BigInteger(), nullable=True)

    last_message = db.Column(db.DateTime(), nullable=False)
    state = db.Column(db.String(16), nullable=False)

    object_manager = relationship("Object", back_populates="manager")
    developer_manager = relationship("Developer", back_populates="manager")
    main_manager = relationship("Config", back_populates="manager")

    chats = relationship("Chat", back_populates="customer", cascade='all,delete')
    actions = relationship("Action", back_populates="user", cascade='all,delete')


    # favorite = db.relationship('Tour', secondary=favorite_tours,
    #                            backref=db.backref('in_favorite', lazy='dynamic'), cascade='delete')

    def __repr__(self):
        return str(self.telegram_id) + ' ' + (self.username if self.username else '')


class Developer(db.Model):
    __tablename__ = 'developer'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    # chat_id = db.Column(db.String(32), nullable=False)
    photo = db.Column(db.String(128), nullable=False)
    # message = db.Column(db.Text(), nullable=False)
    rating = db.Column(db.Float(), nullable=True, default=5.)
    successful_orders = db.Column(db.Integer(), nullable=True)

    objects = relationship("Object", back_populates="owner", cascade='all,delete')
    actions = relationship("Action", back_populates="developer", cascade='all,delete')
    chats = relationship("Chat", back_populates="seller", cascade='all,delete')

    manager_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='SET NULL'), nullable=True)
    manager = relationship("TelegramUser", back_populates="developer_manager")

    def __repr__(self):
        return str(self.name)


class Message(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ru = db.Column(db.Text(), nullable=False)
    en = db.Column(db.Text(), nullable=True)


class Button(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ru = db.Column(db.String(128), nullable=False)
    en = db.Column(db.String(128), nullable=True)


class Photo(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    path = db.Column(db.String(128), nullable=False)
    object_id = db.Column(db.Integer(), db.ForeignKey("object.id", ondelete='CASCADE'), nullable=False)
    object = relationship("Object", back_populates="photos")


class File(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    path = db.Column(db.String(128), nullable=False)
    object_id = db.Column(db.Integer(), db.ForeignKey("object.id", ondelete='CASCADE'), nullable=False)
    object = relationship("Object", back_populates="files")


class Object(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    price = db.Column(db.Integer(), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    date = db.Column(db.Date(), nullable=False)
    roi = db.Column(db.Integer(), nullable=False)
    presentation_path = db.Column(db.String(128), nullable=True)
    active = db.Column(db.Boolean(), nullable=False, default=True)
    sale = db.Column(db.Boolean(), nullable=False, default=False)
    payback = db.Column(db.String(32), nullable=True)

    owner_id = db.Column(db.Integer(), db.ForeignKey("developer.id", ondelete='CASCADE'), nullable=False)
    owner = relationship("Developer", back_populates="objects")

    manager_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='SET NULL'), nullable=True)
    manager = relationship("TelegramUser", back_populates="object_manager")

    district_id = db.Column(db.Integer(), db.ForeignKey("district.id", ondelete='CASCADE'), nullable=False)
    district = relationship("District", back_populates="objects")

    photos = relationship("Photo", back_populates="object", cascade='all,delete')
    files = relationship("File", back_populates="object", cascade='all,delete')
    # orders = relationship("Order", back_populates="object")
    chats = relationship("Chat", back_populates="object")
    actions = relationship("Action", back_populates="object", cascade='all,delete')

    def __repr__(self):
        return self.name


class Action(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.Enum(ActionsEnum))

    developer_id = db.Column(db.Integer(), db.ForeignKey("developer.id", ondelete='CASCADE'), nullable=True)
    developer = relationship("Developer", back_populates="actions")

    user_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='CASCADE'), nullable=False)
    user = relationship("TelegramUser", back_populates="actions")

    object_id = db.Column(db.Integer(), db.ForeignKey("object.id", ondelete='CASCADE'), nullable=True)
    object = relationship("Object", back_populates="actions")

    chat_id = db.Column(db.Integer(), db.ForeignKey("chat.id", ondelete='CASCADE'), nullable=True)
    chat = relationship("Chat", back_populates="actions")


class Config(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    support = db.Column(db.String(128), nullable=False)
    presale_form = db.Column(db.Boolean(), default=True)
    group = db.Column(db.String(128), nullable=True)

    manager_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='SET NULL'))
    manager = relationship("TelegramUser", back_populates="main_manager", uselist=False)


class District(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    objects = relationship("Object", back_populates="district", cascade='all,delete')

    def __repr__(self):
        return self.name


class Chat(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    datetime = db.Column(db.DateTime(), nullable=False)

    customer_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='CASCADE'))
    customer = relationship("TelegramUser", back_populates="chats")

    seller_id = db.Column(db.Integer(), db.ForeignKey("developer.id", ondelete='CASCADE'))
    seller = relationship("Developer", back_populates="chats")

    object_id = db.Column(db.Integer(), db.ForeignKey("object.id", ondelete='CASCADE'), nullable=True)
    object = relationship("Object", back_populates="chats")

    messages = relationship("ChatMessage", back_populates="chat", cascade='all,delete')

    actions = relationship("Action", back_populates="chat", cascade='all,delete')

    call_rejected = db.Column(db.Boolean(), default=False)
    # contact_requested = db.Column(db.Boolean(), default=False)


class ChatMessage(db.Model):
    __tablename__ = 'chatmessage'
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    time = db.Column(db.DateTime(), nullable=False)

    chat_id = db.Column(db.Integer(), db.ForeignKey("chat.id", ondelete='CASCADE'))
    chat = relationship("Chat", back_populates="messages")
    is_customer = db.Column(db.Boolean())
