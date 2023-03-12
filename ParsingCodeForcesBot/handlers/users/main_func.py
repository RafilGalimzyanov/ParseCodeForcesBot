from aiogram import types
from aiogram.dispatcher import FSMContext

from database import PostgreSQL
from loader import dp, bot
from states.Search import Search

page_num = 0
page_range = 0


@dp.callback_query_handler(text="data", state=None)
async def go_ord(query: types.CallbackQuery):
    global page_num, page_range
    page_num += 1
    db = PostgreSQL()
    db_data_all = db.select_data()
    page_range = len(db_data_all) // 50
    try:
        db_data = db_data_all[50 * (page_num - 1):50 * page_num]
    except:
        db_data = ""
        pass
    db.connect.close()
    user_id = query.message.chat.id
    await bot.delete_message(user_id, query.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    if page_num == 1:
        keyboard.add(types.InlineKeyboardButton(text="Далее ->", callback_data="data", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Поиск по тема+сложность", callback_data="search", messages="one"))
    elif page_num > 1:
        keyboard.add(types.InlineKeyboardButton(text="<- Назад", callback_data="data-", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Далее ->", callback_data="data", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Поиск по тема+сложность", callback_data="search", messages="one"))
    elif page_num == page_range:
        keyboard.add(types.InlineKeyboardButton(text="<- Назад", callback_data="data-", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Поиск по тема+сложность", callback_data="search", messages="one"))
    start_row = "<b>Номер:</b>  <b>Тема:</b>  <b>Название:</b>  <b>Сложность:</b>  <b>Кол-во решивших:</b>"
    res = ",\n".join(map(str, db_data))
    await bot.send_message(chat_id=user_id, text=f"{start_row} \n {res}", reply_markup=keyboard)


@dp.callback_query_handler(text="data-", state=None)
async def go_ord(query: types.CallbackQuery):
    global page_num
    page_num -= 1
    user_id = query.message.chat.id
    await bot.delete_message(user_id, query.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    if page_num == 1:
        keyboard.add(types.InlineKeyboardButton(text="Далее ->", callback_data="data", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Поиск по тема+сложность", callback_data="search", messages="one"))
    elif page_num > 1:
        keyboard.add(types.InlineKeyboardButton(text="<- Назад", callback_data="data-", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Далее ->", callback_data="data", messages="one"))
        keyboard.add(types.InlineKeyboardButton(text="Поиск по тема+сложность", callback_data="search", messages="one"))
    db = PostgreSQL()
    db_data = db.select_data()[50 * (page_num - 1):50 * page_num]
    db.connect.close()
    start_row = "<b>Номер:</b>  <b>Тема:</b>  <b>Название:</b>  <b>Сложность:</b>  <b>Кол-во решивших:</b>"
    res = ",\n".join(map(str, db_data))
    await bot.send_message(chat_id=user_id, text=f"{start_row} \n {res}", reply_markup=keyboard)


@dp.callback_query_handler(text="search", state=None)
async def search(query: types.CallbackQuery):
    user_id = query.message.chat.id
    await bot.delete_message(user_id, query.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    db = PostgreSQL()
    topics = db.get_topics()
    db.connect.close()
    topics.sort()
    for topic in topics:
        keyboard.add(types.InlineKeyboardButton(text=f"{topic[0][:]}", callback_data=f"{topic[0][:]}", messages="one"))
    await bot.send_message(chat_id=user_id, text=f"Выберите тему: ", reply_markup=keyboard)
    await Search.topic.set()


@dp.callback_query_handler(state=Search.topic)
async def answer_q1(query: types.CallbackQuery, state: FSMContext):
    user_id = query.message.chat.id
    await bot.delete_message(user_id, query.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    topic = query.data
    db = PostgreSQL()
    complexity = db.get_complex()
    complexity.sort()
    db.connect.close()
    for cmpl in complexity:
        keyboard.add(types.InlineKeyboardButton(text=f"{cmpl[0]}", callback_data=str([cmpl[0], topic]), messages="one"))
    await bot.send_message(chat_id=user_id, text=f"Выберите сложность:", reply_markup=keyboard)
    await Search.next()


@dp.callback_query_handler(state=Search.complexity)
async def answer_q1(query: types.CallbackQuery, state: FSMContext):
    user_id = query.message.chat.id
    await bot.delete_message(user_id, query.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    db = PostgreSQL()

    lst = query.data[1:-1].split(',')
    # извлекаем первый элемент как int
    complexity = int(lst[0])
    # извлекаем второй элемент и удаляем кавычки
    topic = lst[1].strip()[1:-1]

    result = db.get_search(topic=topic, complexity=complexity)
    db.connect.close()
    result = ",\n".join(map(str, result))
    keyboard.add(types.InlineKeyboardButton(text=f"Главная страница", callback_data=f"data", messages="one"))
    start_row = "<b>№:</b>  <b>Название:</b>  <b>Тема:</b>  <b>Сложность:</b>  <b>Кол-во решивших:</b>"
    await bot.send_message(chat_id=user_id, text=f"{start_row} \n {result}", reply_markup=keyboard)
    await state.finish()
