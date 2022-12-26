# Create dummy secrey key so we can use sessions
SECRET_KEY = 'ygtfc867f97gbhnbjk'


PG_HOST = 'localhost'
PG_PASSWORD = 'H816gxC4bS9RzpIRShRI'
PG_USER = 'myuser'
PG_DATABASE = 'estate'


HOST = 'https://turutur.ru'
WEBHOOK_PATH = ''
WEBHOOK_URL = HOST + WEBHOOK_PATH

UPDATE_MESSAGE_URL = HOST + '/vgKzr3JPWqOTVRiugLivVAV0iDbqSQCv'
UPDATE_BUTTON_URL = HOST + '/H1vWYrEvefiqmspvUrvfsEaNsXFAMYFN'
SEND_MESSAGE_URL = HOST + '/UZuq7Ftdmcov6HnSdvT33iX5MFaKepI3'
MODERATE_TOUR_URL = HOST + '/admin/tour/moderate'

XLSX_PATH = '/root/code/real_estate/admin/xlsx/'

PROXY = ('45.10.250.252', 8000, 'RsxBk6', 'VvyECT')


SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}'
SQLALCHEMY_ECHO = True

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "ATt87_jinvfweHA_341ELKigfn_6578_CFghaerGdfb_JAEGj"

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_RECOVERABLE = False
SECURITY_CONFIRMABLE = False
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
