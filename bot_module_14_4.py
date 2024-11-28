"""Д/З по теме "План написания админ панели"""
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import asyncio
from keyboard_for_14_3 import *
from crud_function import initiate_db, get_all_products

connection = sqlite3.connect('initiate_db')
cursor = connection.cursor()
initiate_db()

api = "7902261422:AAEPIuK48tw7Rfx0Bm0eyCZmnOpMb71_yh4"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

"""ф-ия по отработке команды /start"""


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.",
                         reply_markup=start_kb)  # исп.клв в отв. ф-ии /start


@dp.message_handler(text='Купить')
async def get_buying_list(message):

    for i in range(1, 5):
        await message.answer(f'Название: Продукт {i}| Описание: Описание {i}| Цена: {i * 100}')
        with open(f'{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer(text="Выберите продукт для покупки:", reply_markup=catalog_kb)


@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


"""создание класса с 3-мя объектами"""


class UserState(StatesGroup):
    age = State()  # возраст
    growth = State()  # рост
    weight = State()  # вес


"""отработка кода по установлению возраста"""


@dp.message_handler(text='Рассчитать')
async def set_age(message):
    await message.answer('Введите свой возраст:')
    await UserState.age.set()  # ожидает ввода возраста


"""отработка кода по установлению роста"""


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()  # ожидает ввода роста


"""отработка кода по установлению веса"""


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()  # ожидает ввода веса


"""отработка кода по расчёту нормы калорий"""


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    calories = int(10 * weight + 6.25 * growth - 5 * age + 5)  # формула Миффлина-Сан Жеора (для мужчин)
    await message.answer(f"Ваша норма калорий: {calories} Ккал в день")
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    print('Мы получили сообщение!')
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
