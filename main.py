import asyncio
import concurrent.futures
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7396063867:AAHT-46Dwu1Aa1NQJcFurr_XzpKY5w1uzCk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class VacancyForm(StatesGroup):
    title = State()
    salary = State()
    experience = State()
    viewers_count = State()
    company_name = State()
    vacancies_per_page = State()
    current_vacancy_index = State()

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
        if key != 'vacancies_per_page' and key != 'current_vacancy_index' and value:
            query += f" AND {key} LIKE ?"
            query_params.append(f"%{value}%")

    cursor.execute(query, query_params)
    vacancies = cursor.fetchall()

    conn.close()
    return vacancies

def clear_database():
    conn = sqlite3.connect('vacancies.sql')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM vacancies')

    conn.commit()
    conn.close()

@dp.message(Command('start'))
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Старт"), KeyboardButton(text="Помощь"), KeyboardButton(text="Очистить базу данных")]], resize_keyboard=True)
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
    await state.set_state(None)  
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Название вакансии", callback_data="vacancy_title")],
        [InlineKeyboardButton(text="Зарплата", callback_data="vacancy_salary")],
        [InlineKeyboardButton(text="Требуемый опыт", callback_data="vacancy_experience")],
        [InlineKeyboardButton(text="Количество просматривающих", callback_data="vacancy_viewers_count")],
        [InlineKeyboardButton(text="Название компании", callback_data="vacancy_company_name")],
        [InlineKeyboardButton(text="Количество вакансий за раз", callback_data="vacancy_count_per_page")],
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

@dp.callback_query(lambda c: c.data == 'vacancy_count_per_page')
async def process_callback_vacancy_count_per_page(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество вакансий, которые будут показываться за один поиск:')
    await state.set_state(VacancyForm.vacancies_per_page)

@dp.message(VacancyForm.vacancies_per_page)
async def process_vacancy_count_per_page(message: types.Message, state: FSMContext):
    try:
        vacancies_per_page = int(message.text)
        await state.update_data(vacancies_per_page=vacancies_per_page)
        await state.set_state(None)
        await update_keyboard(message.from_user.id, state)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Пожалуйста, введите число.')

@dp.callback_query(lambda c: c.data == 'show_vacancies')
async def process_callback_show_vacancies(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    vacancies = get_vacancies_by_params(data)
    vacancies_per_page = data.get('vacancies_per_page', 5)
    current_index = data.get('current_vacancy_index', 0)

    if not vacancies:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Нажмите чтобы начать парсинг", callback_data="start_parsing")]])
        await bot.send_message(callback_query.from_user.id, 'Вакансии не найдены.', reply_markup=keyboard)
        return

    end_index = current_index + vacancies_per_page
    vacancies_to_show = vacancies[current_index:end_index]

    if vacancies_to_show:
        vacancies_text = ""
        for vacancy in vacancies_to_show:
            vacancies_text += f"Название вакансии: {vacancy[1]}\n"
            vacancies_text += f"Название компании: {vacancy[2]}\n"
            vacancies_text += f"Зарплата: {vacancy[3]}\n"
            vacancies_text += f"Требуемый опыт: {vacancy[4]}\n"
            vacancies_text += f"Информация о занятости: {vacancy[5]}\n"
            vacancies_text += f"Количество просматривающих: {vacancy[6]}\n"
            vacancies_text += f"Ссылка для отклика: {vacancy[7]}\n\n"
        
        chunks = split_text_into_chunks(vacancies_text)
        
        for chunk in chunks:
            await bot.send_message(callback_query.from_user.id, chunk)

        if end_index < len(vacancies):
            await state.update_data(current_vacancy_index=end_index)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Показать еще", callback_data="show_vacancies")]])
            await bot.send_message(callback_query.from_user.id, 'Показать еще вакансии?', reply_markup=keyboard)
        else:
            await bot.send_message(callback_query.from_user.id, 'Больше вакансий нет.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Больше вакансий нет.')

async def update_keyboard(user_id, state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Название вакансии: {data.get('title', 'Не указано')}", callback_data="vacancy_title")],
        [InlineKeyboardButton(text=f"Зарплата: {data.get('salary', 'Не указано')}", callback_data="vacancy_salary")],
        [InlineKeyboardButton(text=f"Требуемый опыт: {data.get('experience', 'Не указано')}", callback_data="vacancy_experience")],
        [InlineKeyboardButton(text=f"Количество просматривающих: {data.get('viewers_count', 'Не указано')}", callback_data="vacancy_viewers_count")],
        [InlineKeyboardButton(text=f"Название компании: {data.get('company_name', 'Не указано')}", callback_data="vacancy_company_name")],
        [InlineKeyboardButton(text=f"Количество вакансий за раз: {data.get('vacancies_per_page', 'Не указано')}", callback_data="vacancy_count_per_page")],
        [InlineKeyboardButton(text="Показать вакансии", callback_data="show_vacancies")]
    ])
    await bot.send_message(user_id, 'Выберите параметр для отображения:', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'role_employer')
async def process_callback_employer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Работодатель выбран.')
    
async def help_button(message: types.Message):
    await message.answer('Этот бот помогает найти работу или сотрудника. Используйте кнопки "Старт" и выберите вашу роль.')

parsing_active = False

@dp.callback_query(lambda c: c.data == 'start_parsing')
async def start_parsing(callback_query: types.CallbackQuery, state: FSMContext):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if not parsing_active:
        parsing_active = True
        await bot.send_message(callback_query.from_user.id, 'Начинаем парсинг вакансий...')
        data = await state.get_data()
        title = data.get('title', 'python')
        base_url = f"https://hh.ru/search/vacancy?text={title}&area=1"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Остановить парсинг", callback_data="stop_parsing")]])
        await bot.send_message(callback_query.from_user.id, 'Парсинг запущен. Нажмите кнопку ниже, чтобы остановить.', reply_markup=keyboard)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, parse_multiple_pages, base_url, 0, 2)
        
        await bot.send_message(callback_query.from_user.id, 'Парсинг завершен. Данные сохранены в базу данных.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг уже запущен.')

@dp.callback_query(lambda c: c.data == 'stop_parsing')
async def stop_parsing(callback_query: types.CallbackQuery):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if parsing_active:
        parsing_active = False
        await bot.send_message(callback_query.from_user.id, 'Парсинг остановлен.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг не запущен.')

@dp.message(lambda message: message.text == "Очистить базу данных")
async def clear_database_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Вы точно хотите очистить БД?", callback_data="confirm_clear_db")]])
    await message.answer('Подтвердите очистку базы данных:', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == 'confirm_clear_db')
async def confirm_clear_database(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    clear_database()
    await bot.send_message(callback_query.from_user.id, 'База данных очищена.')

def split_text_into_chunks(text, chunk_size=4000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def parse_vacancies(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies = soup.find_all('a', class_='bloko-link')
        for vacancy in vacancies:
            link = vacancy['href']
            if 'vacancy' in link:  
                full_link = f"https://hh.ru{link}" if link.startswith('/') else link
                parse_vacancy_title(full_link)
                
def parse_vacancy_title(vacancy_url):
    global parsing_active
    if not parsing_active:
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(vacancy_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'data-qa': 'vacancy-title'})
        salary = soup.find('span', {'data-qa': 'vacancy-salary-compensation-type-net'})
        experience = soup.find('span', {'data-qa': 'vacancy-experience'})
        employment_mode = soup.find('p', {'data-qa': 'vacancy-view-employment-mode'})
        parttime_options = soup.find('p', {'data-qa': 'vacancy-view-parttime-options'})
        viewers_count = soup.find('span', class_='vacancy-viewers-count')
        company_name = soup.find('a', {'data-qa': 'vacancy-company-name'})
        response_link = soup.find('a', {'data-qa': 'vacancy-response-link-top'})
        if title:
            title_text = title.text.strip()
            salary_text = salary.text.strip() if salary else "Salary not specified"
            experience_text = experience.text.strip() if experience else "Experience not specified"
            employment_mode_text = employment_mode.text.strip() if employment_mode else ""
            parttime_options_text = parttime_options.text.strip() if parttime_options else ""
            employment_info = " ".join([employment_mode_text, parttime_options_text]).strip()
            employment_info = employment_info if employment_info else "Employment mode and part-time options not specified"
            viewers_count_text = viewers_count.text.strip() if viewers_count else "Viewers count not specified"
            company_name_text = company_name.text.strip() if company_name else "Company name not specified"
            response_link_href = f"https://hh.ru{response_link['href']}" if response_link else "Response link not specified"
            vacancy_data = (title_text, company_name_text, salary_text, experience_text, employment_info, viewers_count_text, response_link_href)
            insert_vacancy(vacancy_data)

def parse_multiple_pages(base_url, start_page, end_page):
    for page in range(start_page, end_page + 1):
        if not parsing_active:
            break
        url = f"{base_url}&page={page}"
        parse_vacancies(url)

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
