import pathlib

import pytz

IP = 'localhost'
PG_PASSWORD = 'hvg32hiu_6f5vgi_tf7'
PG_USER = 'gift'
PG_DATABASE = 'gift'
database_uri = f'postgres://{PG_USER}:{PG_PASSWORD}@{IP}/{PG_DATABASE}'

aiogram_redis = {
    'host': IP,
}

redis = {
    'address': (IP, 6379),
    'encoding': 'utf8'
}

BOT_TOKEN = ''
SECRET_PATTERN = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_='

HOST = ''
WEBHOOK_PATH = ''
WEBHOOK_URL = HOST + WEBHOOK_PATH


YOOKASSA_CLIENT_ID = '17q83n30igo1ub142pdh9o9c1hoqguje'
YOOKASSA_CLIENT_SECRET = 'DOOk_GNvT9ZRQncVLFeWej1qEOyIs_HaNUM_ajkS1hLunGAm06-arr_aKfugeqVJ'


UPDATE_MESSAGE_PATH = '/vgKzr3JPWqOTVRiugLivVAV0iDbqSQCv'
UPDATE_BUTTON_PATH = '/H1vWYrEvefiqmspvUrvfsEaNsXFAMYFN'
SEND_MESSAGE_PATH = '/UZuq7Ftdmcov6HnSdvT33iX5MFaKepI3'
YOOKASSA_WEBHOOK_HANDLER_PATH = '/webhook_operator_{operator_id}'
YOOKASSA_AUTH_HANDLER_PATH = '/yookassa'
YOOKASSA_REDIRECT_URL = \
    'https://yookassa.ru/oauth/v2/authorize?response_type=code&client_id={client_id}&state={state}'.format(
        client_id=YOOKASSA_CLIENT_ID, state='{state}'
    )

YOOKASSA_OAUTH_URL = 'https://yookassa.ru/oauth/v2/token'



CRYPTO_SALT = '1UAarqi0IoshqEree9rjOsfl5A6YajX1WSjsufud'


FLOOD_RATE = 0.06

TG_URL = 'https://t.me/{un}'

REFERRAL_URL = 'https://t.me/{bot_username}?start=reff_{telegram_id}'

NEWLINE = '''
'''

# BASE_PATH = str(
#     pathlib.Path(__file__).parent.resolve().parent.resolve().joinpath('admin').joinpath('static')
# ) + '/'

BASE_PATH = '/root/code/tur2/admin/static/'

DISTRICTS_IN_COLUMN = 10

tz = pytz.timezone('Europe/Moscow')

