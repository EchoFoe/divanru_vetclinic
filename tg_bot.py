import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests

from dotenv import load_dotenv
load_dotenv()


API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class RegistrationState(StatesGroup):
    firstName = State()
    lastName = State()
    phone = State()
    manualPhoneInput = State()


async def send_registration_message(message: types.Message, text: str):
    await message.reply(text)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    bot_name = (await bot.get_me()).username
    registration_button = InlineKeyboardButton("Регистрация", callback_data='registration')
    keyboard = InlineKeyboardMarkup(row_width=1).add(registration_button)
    welcome_message = f"Привет! Я бот ветеринарной клиники {bot_name}. Выберите действие:"
    await message.reply(welcome_message, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'registration')
async def process_registration(callback_query: types.CallbackQuery):
    await send_registration_message(callback_query.message, "Пожалуйста, введите ваше имя:")
    await RegistrationState.firstName.set()


@dp.message_handler(state=RegistrationState.firstName)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await send_registration_message(message, "Спасибо! Теперь введите вашу фамилию:")
    await RegistrationState.lastName.set()


@dp.message_handler(state=RegistrationState.lastName)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text
    share_contact_button = KeyboardButton("Поделиться контактом", request_contact=True)
    do_not_share_button = KeyboardButton("Не хочу делиться")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(share_contact_button, do_not_share_button)
    await message.reply("Пожалуйста, отправьте ваш контакт, чтобы мы могли использовать ваш номер телефона.",
                        reply_markup=keyboard)
    await RegistrationState.phone.set()


async def process_phone_input(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
        first_name = data['first_name']
        last_name = data['last_name']
        phone = data['phone']
        telegram_chat_id = message.chat.id

    registration_data = {
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'telegram_chat_id': telegram_chat_id
    }

    try:
        response = requests.post('http://127.0.0.1:8000/api/accounts/register/', json=registration_data)
        if response.status_code == 201:
            await bot.send_message(message.chat.id, "Пользователь успешно зарегистрирован!")
            await send_appointment_request(message)
        else:
            await bot.send_message(message.chat.id, "Произошла ошибка при регистрации пользователя.")
    except requests.exceptions.RequestException:
        await bot.send_message(message.chat.id, "К сожалению сервис временно не доступен.")


@dp.message_handler(lambda message: message.text == "Не хочу делиться", state=RegistrationState.phone)
async def do_not_share_contact(message: types.Message, state: FSMContext):
    await message.reply("Хорошо, введите ваш номер телефона в формате +1234567890:")
    await RegistrationState.manualPhoneInput.set()


@dp.message_handler(state=RegistrationState.manualPhoneInput)
async def process_manual_phone_input(message: types.Message, state: FSMContext):
    await process_phone_input(message, state)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegistrationState.phone)
async def process_contact(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.contact.phone_number
        first_name = data['first_name']
        last_name = data['last_name']
        phone = data['phone']
        telegram_chat_id = message.chat.id

    registration_data = {
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'telegram_chat_id': telegram_chat_id
    }

    try:
        response = requests.post('http://127.0.0.1:8000/api/accounts/register/', json=registration_data)
        if response.status_code == 201:
            await bot.send_message(message.chat.id, "Пользователь успешно зарегистрирован!")
            await send_appointment_request(message)
        else:
            await bot.send_message(message.chat.id, "Произошла ошибка при регистрации пользователя.")
    except requests.exceptions.RequestException:
        await bot.send_message(message.chat.id, "К сожалению сервис временно не доступен.")


async def send_appointment_request(message: types.Message):
    appointment_button = KeyboardButton("Записаться на прием в ветклинику")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(appointment_button)
    await message.reply("Хотите записаться на прием в ветклинику?", reply_markup=keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
