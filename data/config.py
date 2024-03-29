import pathlib

import pytz

IP = 'localhost'
PG_PASSWORD = ''
PG_USER = ''
PG_DATABASE = 'estate'
database_uri = f'postgres://{PG_USER}:{PG_PASSWORD}@{IP}/{PG_DATABASE}'

aiogram_redis = {
    'host': IP,
}

redis = {
    'address': (IP, 6379),
    'encoding': 'utf8'
}

BOT_TOKEN = ''
SECRET_PATTERN = ''

HOST = ''
WEBHOOK_PATH = ''
WEBHOOK_URL = HOST + WEBHOOK_PATH


YOOKASSA_CLIENT_ID = ''
YOOKASSA_CLIENT_SECRET = ''


UPDATE_MESSAGE_PATH = '/'
UPDATE_BUTTON_PATH = '/'
MEET_PATH = '/meet_redirect_{meet}'
MEET_REDIRECT_PATH = '/meet_redirect_{meet}_{chat_id}'
SEND_MESSAGE_PATH = '/UZuq7Ftdmcov6HnSdvT33iX5MFaKepI3'
YOOKASSA_WEBHOOK_HANDLER_PATH = '/webhook_operator_{operator_id}'
YOOKASSA_AUTH_HANDLER_PATH = '/yookassa'
YOOKASSA_REDIRECT_URL = \
    'https://yookassa.ru/oauth/v2/authorize?response_type=code&client_id={client_id}&state={state}'.format(
        client_id=YOOKASSA_CLIENT_ID, state='{state}'
    )

YOOKASSA_OAUTH_URL = 'https://yookassa.ru/oauth/v2/token'

SEND_TIME = (20, 0, 0)


CRYPTO_SALT = ''


FLOOD_RATE = 0.06

TG_URL = 'https://t.me/{un}'

REFERRAL_URL = 'https://t.me/{bot_username}?start=reff_{telegram_id}'

NEWLINE = '''
'''

# BASE_PATH = str(
#     pathlib.Path(__file__).parent.resolve().parent.resolve().joinpath('admin').joinpath('static')
# ) + '/'

BASE_PATH = '/root/code/real_estate/admin/static/'

DISTRICTS_IN_COLUMN = 10

tz = pytz.timezone('Europe/Moscow')

