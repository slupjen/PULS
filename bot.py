import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderState(StatesGroup):
    waiting_for_description = State()

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("👋 Привіт! Натисни /order щоб зробити нове замовлення.")

@dp.message_handler(commands="order")
async def cmd_order(message: types.Message):
    await OrderState.waiting_for_description.set()
    await message.answer("📝 Введи опис замовлення:")

@dp.message_handler(state=OrderState.waiting_for_description, content_types=types.ContentTypes.TEXT)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text
    user_id = message.from_user.id
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS orders (user_id INTEGER, description TEXT)")
    cursor.execute("INSERT INTO orders (user_id, description) VALUES (?, ?)", (user_id, description))
    conn.commit()
    conn.close()
    await message.answer("✅ Замовлення прийнято! Дякуємо!")
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
