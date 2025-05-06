from aiogram import Bot, types, Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import *
from parsing import *
from config import API_TOKEN

router = Router()
bot = Bot(token=API_TOKEN)

class VacancyForm(StatesGroup):
    title = State()
    salary = State()
    experience = State()
    viewers_count = State()
    company_name = State()
    vacancies_per_page = State()
    current_vacancy_index = State()

class ResumeForm(StatesGroup):
    job_title = State()
    work_experience = State()
    age = State()
    resumes_per_page = State()
    current_resume_index = State()

@router.message(Command('start'))
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Старт"), KeyboardButton(text="Помощь"), KeyboardButton(text="Очистить базу данных")]], resize_keyboard=True)
    await message.answer('Нажмите кнопку "Старт" для начала или "Помощь" для получения помощи:', reply_markup=keyboard)

@router.message(lambda message: message.text == "Старт")
async def start_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Соискатель", callback_data="role_applicant")],
        [InlineKeyboardButton(text="Работодатель", callback_data="role_employer")]
    ])
    await message.answer('Выберите вашу роль:', reply_markup=keyboard)

async def help_button(message: types.Message):
    await message.answer('Этот бот помогает найти работу или сотрудника. Используйте кнопки "Старт" и выберите вашу роль.')

@router.message(lambda message: message.text == "Очистить базу данных")
async def clear_database_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Вы точно хотите очистить БД?", callback_data="confirm_clear_db")]])
    await message.answer('Подтвердите очистку базы данных:', reply_markup=keyboard)

@router.callback_query(lambda c: c.data == 'confirm_clear_db')
async def confirm_clear_database(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    clear_database()
    await bot.send_message(callback_query.from_user.id, 'База данных очищена.')

def split_text_into_chunks(text, chunk_size=4000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]