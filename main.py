import logging
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import handlers
from backend import base_init
from settings import TOKEN


def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    memo = MemoryStorage()
    dp = Dispatcher(bot, storage=memo)
    handlers.reg_commands(dp)
    executor.start_polling(dp)


if __name__ == '__main__':
    base_init()
    main()
