import os

from typing import Optional

import requests

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv


load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BASE_API_URL = os.getenv('BASE_API_URL')
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class RegistrationState(StatesGroup):
    """ Состояния для процесса регистрации клиента. """
    firstName = State()
    lastName = State()
    phone = State()
    manualPhoneInput = State()
    client_id = State()


class AppointmentState(StatesGroup):
    """ Состояния для процесса записи на прием в ветклинику. """
    choose_animal_type = State()
    choose_slot = State()


async def send_registration_message(message: types.Message, text: str) -> None:
    """ Отправляет сообщение о регистрации клиента. """
    await message.reply(text)


async def send_goodbye_message(message: types.Message):
    """ Отправляет конечное сообщение после успешной записи на прием."""
    await message.reply("Спасибо за запись на прием! Мы позаботимя о Вашем питомце <3. "
                        "С Вами скоро свяжутся для уточнения деталей")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """ Обработчик для команды Старт """
    bot_name = (await bot.get_me()).username
    registration_button = InlineKeyboardButton('Регистрация', callback_data='registration')
    keyboard = InlineKeyboardMarkup(row_width=1).add(registration_button)
    welcome_message = f'Привет! Я бот ветеринарной клиники {bot_name}. Выберите действие:'
    await message.reply(welcome_message, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'registration')
async def process_registration(callback_query: types.CallbackQuery):
    """ Обработчик для запуска процесса регистрации """
    await send_registration_message(callback_query.message, "Пожалуйста, введите ваше имя:")
    await RegistrationState.firstName.set()


@dp.message_handler(state=RegistrationState.firstName)
async def process_first_name(message: types.Message, state: FSMContext):
    """ Обработчик для записи имени клиента """
    async with state.proxy() as data:
        data['first_name'] = message.text
    await send_registration_message(message, "Спасибо! Теперь введите вашу фамилию:")
    await RegistrationState.lastName.set()


@dp.message_handler(state=RegistrationState.lastName)
async def process_last_name(message: types.Message, state: FSMContext):
    """ Обработчик для записи фамилии клиента """
    async with state.proxy() as data:
        data['last_name'] = message.text
    share_contact_button = KeyboardButton("Поделиться контактом", request_contact=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(share_contact_button)
    await message.reply("Пожалуйста, нажмите кнопку 'Поделиться контактом', "
                        "чтобы мы могли использовать ваш номер телефона.",
                        reply_markup=keyboard)
    await RegistrationState.phone.set()


async def send_appointment_request(message: types.Message, state: FSMContext):
    """ Обработчик для записи на приём """
    await AppointmentState.choose_animal_type.set()
    appointment_button = KeyboardButton("Записаться на прием в ветклинику")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(appointment_button)
    await message.reply("Для записи на приём к врачу укажаите тип животного из предложенного", reply_markup=keyboard)
    await get_animal_types(message, state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=RegistrationState.phone)
async def process_text_as_contact(message: types.Message, state: FSMContext):
    """ Обработчик исключения возможности записи номера телефона с помощью инпута """
    await message.reply("Не надо ничего вводить в инпут, просто нажмите кнопку 'Поделиться контактом'.")
    share_contact_button = KeyboardButton('Поделиться контактом', request_contact=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(share_contact_button)
    await message.reply('Пожалуйста, поделитесь контактом, чтобы мы могли использовать ваш номер телефона.',
                        reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegistrationState.phone)
async def process_contact(message: types.Message, state: FSMContext):
    """ Обработчик для регистрации клиента в БД """
    async with state.proxy() as data:
        data['phone'] = message.contact.phone_number
        first_name = data['first_name']
        last_name = data['last_name']
        phone = data['phone']
        telegram_chat_id = message.chat.id
        client_id = data.get('client_id')

    registration_data = {
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'telegram_chat_id': telegram_chat_id
    }

    try:
        response = requests.post(f'{BASE_API_URL}/api/accounts/register/', json=registration_data)
        if response.status_code == 201 and 'id' in response.json():
            client_id = response.json()['id']
            await state.update_data(client_id=client_id)
            await bot.send_message(message.chat.id, 'Пользователь успешно зарегистрирован!')
            await send_appointment_request(message, state)
        else:
            await bot.send_message(message.chat.id, 'Произошла ошибка при регистрации пользователя.')
    except requests.exceptions.RequestException:
        await bot.send_message(message.chat.id, 'К сожалению сервис временно не доступен.')


async def get_animal_types(message: types.Message, state: FSMContext):
    """ Обработчик для предоставления типов животных, которые обслуживает ветклиника """
    try:
        response = requests.get(f'{BASE_API_URL}/api/vetclinics/animal-types/')
        if response.status_code == 200:
            animal_types = response.json()
            buttons = [KeyboardButton(animal_type['name']) for animal_type in animal_types]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*buttons)
            await message.reply('Выберите тип животного:', reply_markup=keyboard)
        else:
            await message.reply('К сожалению, в данный момент не удалось получить доступные типы животных.')
    except requests.exceptions.RequestException as e:
        print('Ошибка соединения:', e)
        await message.reply('К сожалению, сервис временно не доступен.')


async def get_animal_type_id(animal_type_name: str) -> Optional[int]:
    """ Обработчик для получения ID типа животного """
    try:
        response = requests.get(f'{BASE_API_URL}/api/vetclinics/animal-types/')
        if response.status_code == 200:
            animal_types = response.json()
            for animal_type in animal_types:
                if animal_type['name'] == animal_type_name:
                    return animal_type['id']
    except requests.exceptions.RequestException as e:
        print('Ошибка соединения:', e)
    return None


async def get_free_slots(message: types.Message, state: FSMContext):
    """ Обработчик для предоставления свободных слотов для записи на приём """
    try:
        response = requests.get(f'{BASE_API_URL}/api/vetclinics/free-slots/')
        if response.status_code == 200:
            free_slots = response.json()
            buttons = [KeyboardButton(slot) for slot in free_slots]
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*buttons)
            await message.reply('Выберите свободный слот для записи на прием:', reply_markup=keyboard)
            await AppointmentState.choose_slot.set()  # Устанавливаем состояние выбора слота
        else:
            await message.reply('К сожалению, в данный момент не удалось получить свободные слоты.')
    except requests.exceptions.RequestException:
        await message.reply('К сожалению, сервис временно не доступен.')


@dp.message_handler(state=AppointmentState.choose_animal_type)
async def process_animal_type_choice(message: types.Message, state: FSMContext):
    """ Обработчик для сохранения состояния типа животного """
    async with state.proxy() as data:
        data['animal_type'] = message.text
    await get_free_slots(message, state)


@dp.message_handler(state=AppointmentState.choose_slot)
async def process_slot_choice(message: types.Message, state: FSMContext):
    """ Обработчик для осуществления записи на приём """
    async with state.proxy() as data:
        data['chosen_slot'] = message.text
        client_id = data.get('client_id')
        appointment_date = data.get('chosen_slot')
        animal_type_name = data.get('animal_type')
        animal_type_id = await get_animal_type_id(animal_type_name)

    if animal_type_id is None:
        await bot.send_message(message.chat.id, "Не удалось определить тип животного.")
        return

    appointment_data = {
        'client': client_id,
        'appointment_date': appointment_date,
        'animal_type': animal_type_id
    }

    try:
        response = requests.post(f'{BASE_API_URL}/api/vetclinics/make-an-appointment/', json=appointment_data)
        if response.status_code == 201:
            await bot.send_message(message.chat.id, "Вы успешно записались на прием!")
            await send_goodbye_message(message)
        else:
            await bot.send_message(message.chat.id, "Произошла ошибка при записи на прием.")
    except requests.exceptions.RequestException:
        await bot.send_message(message.chat.id, "К сожалению, сервис временно не доступен.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
