import asyncio
import logging.config

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config
from data.config_logger import config as logger_config
from utils.supervisor import Supervisor

logging.config.dictConfig(logger_config)
logger = logging.getLogger('file_logger')

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.new_event_loop()
supervisor = Supervisor(loop)
