import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from config import TOKEN

# Логирование
logging.basicConfig(level=logging.INFO)

# FSM-состояния
class Form(StatesGroup):
    username = State()
    age = State()
    grade = State()

# Бот и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Создание БД
conn = sqlite3.connect('students.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT
    )
''')
conn.commit()
conn.close()

# /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer('Привет, как тебя зовут?')
    await state.set_state(Form.username)

# Имя
@dp.message(Form.username)
async def process_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('Сколько тебе лет?')
    await state.set_state(Form.age)

# Возраст
@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи возраст числом.")
        return
    await state.update_data(age=int(message.text))
    await message.answer('В каком ты классе?')
    await state.set_state(Form.grade)

# Класс и сохранение
@dp.message(Form.grade)
async def process_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    # Сохранение в базу
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO students (username, age, grade) VALUES (?, ?, ?)',
        (user_data['username'], user_data['age'], user_data['grade'])
    )
    conn.commit()
    conn.close()

    await message.answer(
        f"✅ Данные сохранены!\n\n"
        f"Имя: {user_data['username']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Класс: {user_data['grade']}"
    )

    await state.clear()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
