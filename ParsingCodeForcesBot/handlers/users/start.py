from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Посмотреть задачи", callback_data="data", messages="one"))
    await message.answer(f"Привет, {message.from_user.full_name}!\n"
                         f"Этот тестовый Бот предназначен для парсинга информации\n"
                         f"о задачах из сайта codeforces.com", reply_markup=keyboard)