import time

import schedule
from aiogram import executor

import database
from database import check
from loader import dp
import middlewares, handlers
from utils.notify_admins import on_startup_notify


async def on_startup(dispatcher):
    # Уведомляет про запуск
    await on_startup_notify(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
