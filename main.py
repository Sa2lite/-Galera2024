from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio

API_TOKEN = '7396063867:AAHT-46Dwu1Aa1NQJcFurr_XzpKY5w1uzCk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class VacancyForm(StatesGroup):
    title = State()
    salary = State()
    experience = State()
    viewers_count = State()
    company_name = State()

def create_database():
    conn = sqlite3.connect('vacancies.sql')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company_name TEXT,
            salary TEXT,
            experience TEXT,
            employment_info TEXT,
            viewers_count TEXT,
            response_link TEXT
        )
    ''')

    conn.commit()
    conn.close()

def insert_vacancy(vacancy_data):
    conn = sqlite3.connect('vacancies.sql')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO vacancies (title, company_name, salary, experience, employment_info, viewers_count, response_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', vacancy_data)

    conn.commit()
    conn.close()

def get_all_vacancies():
    conn = sqlite3.connect('vacancies.sql')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM vacancies')
    vacancies = cursor.fetchall()

    conn.close()
    return vacancies

def get_vacancies_by_params(params):
    conn = sqlite3.connect('vacancies.sql')
    cursor = conn.cursor()

    query = "SELECT * FROM vacancies WHERE 1=1"
    query_params = []
    for key, value in params.items():
        if value:
            query += f" AND {key} LIKE ?"
            query_params.append(f"%{value}%")

    cursor.execute(query, query_params)
    vacancies = cursor.fetchall()

    conn.close()
    return vacancies

@dp.message(Command('start'))
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Старт"), KeyboardButton(text="Помощь")]], resize_keyboard=True)
    await message.answer('Нажмите кнопку "Старт" для начала или "Помощь" для получения помощи:', reply_markup=keyboard)

@dp.message(lambda message: message.text == "Старт")
async def start_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Соискатель", callback_data="role_applicant")],
        [InlineKeyboardButton(text="Работодатель", callback_data="role_employer")]
    ])
    await message.answer('Выберите вашу роль:', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'role_applicant')
async def process_callback_applicant(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Подключаемся к базе данных...')
    await state.set_state(VacancyForm.title)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название вакансии", callback_data="vacancy_title")],
        [InlineKeyboardButton(text="Зарплата", callback_data="vacancy_salary")],
        [InlineKeyboardButton(text="Требуемый опыт", callback_data="vacancy_experience")],
        [InlineKeyboardButton(text="Количество просматривающих", callback_data="vacancy_viewers_count")],
        [InlineKeyboardButton(text="Название компании", callback_data="vacancy_company_name")],
        [InlineKeyboardButton(text="Показать вакансии", callback_data="show_vacancies")]
    ])
    await bot.send_message(callback_query.from_user.id, 'Выберите параметр для отображения:', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'vacancy_title')
async def process_callback_vacancy_title(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите название вакансии:')
    await state.set_state(VacancyForm.title)

@dp.message(VacancyForm.title)
async def process_vacancy_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@dp.callback_query(lambda c: c.data == 'vacancy_salary')
async def process_callback_vacancy_salary(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите зарплату:')
    await state.set_state(VacancyForm.salary)

@dp.message(VacancyForm.salary)
async def process_vacancy_salary(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@dp.callback_query(lambda c: c.data == 'vacancy_experience')
async def process_callback_vacancy_experience(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите требуемый опыт:')
    await state.set_state(VacancyForm.experience)

@dp.message(VacancyForm.experience)
async def process_vacancy_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@dp.callback_query(lambda c: c.data == 'vacancy_viewers_count')
async def process_callback_vacancy_viewers_count(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество просматривающих:')
    await state.set_state(VacancyForm.viewers_count)

@dp.message(VacancyForm.viewers_count)
async def process_vacancy_viewers_count(message: types.Message, state: FSMContext):
    await state.update_data(viewers_count=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@dp.callback_query(lambda c: c.data == 'vacancy_company_name')
async def process_callback_vacancy_company_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите название компании:')
    await state.set_state(VacancyForm.company_name)

@dp.message(VacancyForm.company_name)
async def process_vacancy_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@dp.callback_query(lambda c: c.data == 'show_vacancies')
async def process_callback_show_vacancies(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    vacancies = get_vacancies_by_params(data)
    if vacancies:
        vacancies_text = ""
        for vacancy in vacancies:
            vacancies_text += f"Название вакансии: {vacancy[1]}\n"
            vacancies_text += f"Название компании: {vacancy[2]}\n"
            vacancies_text += f"Зарплата: {vacancy[3]}\n"
            vacancies_text += f"Требуемый опыт: {vacancy[4]}\n"
            vacancies_text += f"Информация о занятости: {vacancy[5]}\n"
            vacancies_text += f"Количество просматривающих: {vacancy[6]}\n"
            vacancies_text += f"Ссылка для отклика: {vacancy[7]}\n\n"
        await bot.send_message(callback_query.from_user.id, f'Найдены вакансии:\n{vacancies_text}')
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Нажмите чтобы начать парсинг", callback_data="start_parsing")]])
        await bot.send_message(callback_query.from_user.id, 'Вакансии не найдены.', reply_markup=keyboard)

async def update_keyboard(user_id, state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название вакансии" + (" (указано)" if data.get('title') else ""), callback_data="vacancy_title")],
        [InlineKeyboardButton(text="Зарплата" + (" (указано)" if data.get('salary') else ""), callback_data="vacancy_salary")],
        [InlineKeyboardButton(text="Требуемый опыт" + (" (указано)" if data.get('experience') else ""), callback_data="vacancy_experience")],
        [InlineKeyboardButton(text="Количество просматривающих" + (" (указано)" if data.get('viewers_count') else ""), callback_data="vacancy_viewers_count")],
        [InlineKeyboardButton(text="Название компании" + (" (указано)" if data.get('company_name') else ""), callback_data="vacancy_company_name")],
        [InlineKeyboardButton(text="Показать вакансии", callback_data="show_vacancies")]
    ])
    await bot.send_message(user_id, 'Выберите параметр для отображения:', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'role_employer')
async def process_callback_employer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Работодатель выбран.')

@dp.message(lambda message: message.text == "Помощь")
async def help_button(message: types.Message):
    await message.answer('Этот бот помогает найти работу или сотрудника. Используйте кнопки "Старт" и выберите вашу роль.')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    create_database()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    finally:
        print('Завершение работы бота...')
