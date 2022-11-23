from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref

from admin.flask_app_init import db

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

favorite_tours = db.Table(
    'favorite_tours',
    db.Column('telegramuser_id', db.Integer(), db.ForeignKey('telegramuser.id')),
    db.Column('tour_id', db.Integer(), db.ForeignKey('tour.id'))
)


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
    operator = relationship("TourOperator", back_populates="admin_account")

    def __str__(self):
        return self.email


class TelegramUser(db.Model):
    __tablename__ = 'telegramuser'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=True)
    full_name = db.Column(db.String(256), unique=True, nullable=True)
    city = db.Column(db.String(128), unique=True, nullable=True)
    phone = db.Column(db.BigInteger(), nullable=True)
    birthday = db.Column(db.Date(), nullable=True)
    lang = db.Column(db.String(4), nullable=True, default='ru')
    # referrals = db.relationship('TelegramUser', back_populates='referer')
    # referer = db.relationship('TelegramUser', back_populates='referrals', remote_side=[id])
    referer_id = db.Column(db.Integer, db.ForeignKey('telegramuser.id', ondelete='SET NULL'), nullable=True)
    referrals = relationship("TelegramUser", backref=backref('referer', remote_side=[id]))
    operator = relationship("TourOperator", back_populates="user", cascade='delete')

    orders = relationship("Order", back_populates="customer")
    promos = relationship("PromoUses", back_populates="user", cascade='all,delete')
    chats = relationship("Chat", back_populates="customer", cascade='all,delete')

    favorite = db.relationship('Tour', secondary=favorite_tours,
                               backref=db.backref('in_favorite', lazy='dynamic'), cascade='delete')

    def __repr__(self):
        return str(self.telegram_id)


class TourOperator(db.Model):
    __tablename__ = 'touroperator'
    id = db.Column(db.Integer(), primary_key=True)
    prepayment = db.Column(db.Integer(), default=20, nullable=False)
    full_name = db.Column(db.String(256), nullable=False)
    about = db.Column(db.Text(), nullable=False)
    region = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    languages = db.Column(db.String(256), nullable=False)
    verified = db.Column(db.Boolean(), nullable=False)
    contact_fio = db.Column(db.String(128), nullable=False)
    experience = db.Column(db.Integer(), nullable=False)
    site = db.Column(db.String(256), nullable=False)
    photo = db.Column(db.String(128), nullable=False)
    moderate = db.Column(db.Boolean(), nullable=False)

    yookassa = db.Column(db.String(256), nullable=True)

    user_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='CASCADE'))
    user = relationship("TelegramUser", back_populates="operator", uselist=False)
    tours = relationship("Tour", back_populates="owner", cascade='all,delete')

    orders = relationship("Order", back_populates="seller")
    chats = relationship("Chat", back_populates="seller", cascade='all,delete')

    admin_account = relationship("User", back_populates="operator", uselist=False)
    admin_account_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete='SET NULL'), nullable=True)



    def __repr__(self):
        return str(self.full_name)


class Message(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ru = db.Column(db.Text(), nullable=False)


class Button(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    ru = db.Column(db.String(128), nullable=False)


class Photo(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    path = db.Column(db.String(128), nullable=False)
    tour_id = db.Column(db.Integer(), db.ForeignKey("tour.id", ondelete='CASCADE'), nullable=False)
    tour = relationship("Tour", back_populates="photos")


class Direction(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tours = relationship("Tour", back_populates="direction")

    def __repr__(self):
        return self.name


class Tour(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    included = db.Column(db.Text(), nullable=False)
    terms = db.Column(db.Text(), nullable=False)

    active = db.Column(db.Boolean(), nullable=False, default=True)
    moderate = db.Column(db.Boolean(), nullable=False, default=False)

    owner_id = db.Column(db.Integer(), db.ForeignKey("touroperator.id", ondelete='CASCADE'), nullable=False)
    owner = relationship("TourOperator", back_populates="tours")

    direction_id = db.Column(db.Integer(), db.ForeignKey("direction.id", ondelete='SET NULL'), nullable=False)
    direction = relationship("Direction", back_populates="tours")

    photos = relationship("Photo", back_populates="tour", cascade='all,delete')
    dates = relationship("Date", back_populates="tour", cascade='all,delete')

    orders = relationship("Order", back_populates="tour")

    def __repr__(self):
        return self.name


class Date(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    places = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    sale = db.Column(db.Integer(), nullable=False, default=0)
    start = db.Column(db.Date(), nullable=False)
    end = db.Column(db.Date(), nullable=False)

    tour_id = db.Column(db.Integer(), db.ForeignKey("tour.id", ondelete='CASCADE'), nullable=False)
    tour = relationship("Tour", back_populates="dates")

    orders = relationship("Order", back_populates="date")

    def __repr__(self):
        return f'{self.start} - {self.end}'


class Order(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    remainder = db.Column(db.Integer(), nullable=False)
    paid = db.Column(db.Integer(), nullable=False)
    tax = db.Column(db.Integer(), nullable=False)
    places = db.Column(db.Integer(), nullable=False)
    state = db.Column(db.String(8), nullable=False)
    url = db.Column(db.String(256), nullable=True)
    datetime = db.Column(db.DateTime(), nullable=False)

    tour_id = db.Column(db.Integer(), db.ForeignKey("tour.id", ondelete='SET NULL'))
    tour = relationship("Tour", back_populates="orders")

    date_id = db.Column(db.Integer(), db.ForeignKey("date.id", ondelete='SET NULL'))
    date = relationship("Date", back_populates="orders")

    promo_id = db.Column(db.Integer(), db.ForeignKey("promocode.id", ondelete='SET NULL'))
    promo = relationship("PromoCode", back_populates="orders")

    customer_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='SET NULL'))
    customer = relationship("TelegramUser", back_populates="orders")

    seller_id = db.Column(db.Integer(), db.ForeignKey("touroperator.id", ondelete='SET NULL'))
    seller = relationship("TourOperator", back_populates="orders")

    def __repr__(self):
        return f'Order id{self.id}'


class Config(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    support_url = db.Column(db.String(64), nullable=False)
    group = db.Column(db.String(64), nullable=False)
    tax = db.Column(db.Integer(), nullable=False)


class PromoCode(db.Model):
    __tablename__ = 'promocode'

    id = db.Column(db.Integer(), primary_key=True)
    percent = db.Column(db.SmallInteger(), nullable=False)
    text = db.Column(db.String(32), nullable=False)
    uses = db.Column(db.SmallInteger(), nullable=False)
    uses_for_one = db.Column(db.SmallInteger(), nullable=False)
    end = db.Column(db.Date(), nullable=False)

    orders = relationship("Order", back_populates="promo")
    used = relationship("PromoUses", back_populates="promo_code", cascade='all,delete')

    def __repr__(self):
        return self.text


class PromoUses(db.Model):
    __tablename__ = 'promouses'

    id = db.Column(db.Integer(), primary_key=True)
    count = db.Column(db.SmallInteger(), nullable=False, default=1)

    promo_code_id = db.Column(db.Integer(), db.ForeignKey("promocode.id", ondelete='CASCADE'))
    promo_code = relationship("PromoCode", back_populates="used")

    user_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='CASCADE'))
    user = relationship("TelegramUser", back_populates="promos")


class Chat(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    datetime = db.Column(db.DateTime(), nullable=False)

    customer_id = db.Column(db.Integer(), db.ForeignKey("telegramuser.id", ondelete='CASCADE'))
    customer = relationship("TelegramUser", back_populates="chats")

    seller_id = db.Column(db.Integer(), db.ForeignKey("touroperator.id", ondelete='CASCADE'))
    seller = relationship("TourOperator", back_populates="chats")

    messages = relationship("ChatMessage", back_populates="chat", cascade='all,delete')


class ChatMessage(db.Model):
    __tablename__ = 'chatmessage'
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    time = db.Column(db.DateTime(), nullable=False)

    chat_id = db.Column(db.Integer(), db.ForeignKey("chat.id", ondelete='CASCADE'))
    chat = relationship("Chat", back_populates="messages")
    is_customer = db.Column(db.Boolean())
