import asyncio
import concurrent.futures
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
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
#соискатель___________________________________________________________________________________________________________
@router.callback_query(lambda c: c.data == 'role_applicant')
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

@router.callback_query(lambda c: c.data == 'role_employer')
async def process_callback_employer(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Работодатель выбран.')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Профессия", callback_data="resume_job_title")],
        [InlineKeyboardButton(text="Опыт работы", callback_data="resume_work_experience")],
        [InlineKeyboardButton(text="Возраст", callback_data="resume_age")],
        [InlineKeyboardButton(text="Количество резюме за раз", callback_data="resume_count_per_page")],
        [InlineKeyboardButton(text="Показать резюме", callback_data="show_resumes")]
    ])
    await bot.send_message(callback_query.from_user.id, 'Выберите параметр для отображения:', reply_markup=keyboard)
    

@router.callback_query(lambda c: c.data == 'vacancy_title')
async def process_callback_vacancy_title(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите название вакансии:')
    await state.set_state(VacancyForm.title)

@router.message(VacancyForm.title)
async def process_vacancy_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'vacancy_salary')
async def process_callback_vacancy_salary(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите зарплату:')
    await state.set_state(VacancyForm.salary)

@router.message(VacancyForm.salary)
async def process_vacancy_salary(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'vacancy_experience')
async def process_callback_vacancy_experience(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите требуемый опыт:')
    await state.set_state(VacancyForm.experience)

@router.message(VacancyForm.experience)
async def process_vacancy_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'vacancy_viewers_count')
async def process_callback_vacancy_viewers_count(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество просматривающих:')
    await state.set_state(VacancyForm.viewers_count)

@router.message(VacancyForm.viewers_count)
async def process_vacancy_viewers_count(message: types.Message, state: FSMContext):
    await state.update_data(viewers_count=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'vacancy_company_name')
async def process_callback_vacancy_company_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите название компании:')
    await state.set_state(VacancyForm.company_name)

@router.message(VacancyForm.company_name)
async def process_vacancy_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'vacancy_count_per_page')
async def process_callback_vacancy_count_per_page(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество вакансий, которые будут показываться за один поиск:')
    await state.set_state(VacancyForm.vacancies_per_page)

@router.message(VacancyForm.vacancies_per_page)
async def process_vacancy_count_per_page(message: types.Message, state: FSMContext):
    try:
        vacancies_per_page = int(message.text)
        await state.update_data(vacancies_per_page=vacancies_per_page)
        await state.set_state(None)
        await update_keyboard(message.from_user.id, state)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Пожалуйста, введите число.')

@router.callback_query(lambda c: c.data == 'show_vacancies')
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

@router.callback_query(lambda c: c.data == 'role_employer')
async def process_callback_employer(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Работодатель выбран.')
    
async def help_button(message: types.Message):
    await message.answer('Этот бот помогает найти работу или сотрудника. Используйте кнопки "Старт" и выберите вашу роль.')

@router.callback_query(lambda c: c.data == 'start_parsing')
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
            await loop.run_in_executor(executor, parse_multiple_pages, base_url, 0, 2, parsing_active)
        
        await bot.send_message(callback_query.from_user.id, 'Парсинг завершен. Данные сохранены в базу данных.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг уже запущен.')

@router.callback_query(lambda c: c.data == 'stop_parsing')
async def stop_parsing(callback_query: types.CallbackQuery):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if parsing_active:
        parsing_active = False
        await bot.send_message(callback_query.from_user.id, 'Парсинг остановлен.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг не запущен.')

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

#Работодатель      

# Обработчики для кнопок "Работодатель"
@router.callback_query(lambda c: c.data == 'resume_job_title')
async def process_callback_resume_job_title(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите профессию:')
    await state.set_state(ResumeForm.job_title)

@router.message(ResumeForm.job_title)
async def process_resume_job_title(message: types.Message, state: FSMContext):
    await state.update_data(job_title=message.text)
    await state.set_state(None)
    await update_resume_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'resume_work_experience')
async def process_callback_resume_work_experience(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите опыт работы:')
    await state.set_state(ResumeForm.work_experience)

@router.message(ResumeForm.work_experience)
async def process_resume_work_experience(message: types.Message, state: FSMContext):
    await state.update_data(work_experience=message.text)
    await state.set_state(None)
    await update_resume_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'resume_age')
async def process_callback_resume_age(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите возраст:')
    await state.set_state(ResumeForm.age)

@router.message(ResumeForm.age)
async def process_resume_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(None)
    await update_resume_keyboard(message.from_user.id, state)

@router.callback_query(lambda c: c.data == 'resume_count_per_page')
async def process_callback_resume_count_per_page(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество резюме, которые будут показываться за один поиск:')
    await state.set_state(ResumeForm.resumes_per_page)

@router.message(ResumeForm.resumes_per_page)
async def process_resume_count_per_page(message: types.Message, state: FSMContext):
    try:
        resumes_per_page = int(message.text)
        await state.update_data(resumes_per_page=resumes_per_page)
        await state.set_state(None)
        await update_resume_keyboard(message.from_user.id, state)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Пожалуйста, введите число.')

async def update_resume_keyboard(user_id, state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Профессия: {data.get('job_title', 'Не указано')}", callback_data="resume_job_title")],
        [InlineKeyboardButton(text=f"Опыт работы: {data.get('work_experience', 'Не указано')}", callback_data="resume_work_experience")],
        [InlineKeyboardButton(text=f"Возраст: {data.get('age', 'Не указано')}", callback_data="resume_age")],
        [InlineKeyboardButton(text=f"Количество резюме за раз: {data.get('resumes_per_page', 'Не указано')}", callback_data="resume_count_per_page")],
        [InlineKeyboardButton(text="Показать резюме", callback_data="show_resumes")]
    ])
    await bot.send_message(user_id, 'Выберите параметр для отображения:', reply_markup=keyboard)

@router.callback_query(lambda c: c.data == 'show_resumes')
async def process_callback_show_resumes(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = await state.get_data()
    resumes = get_resumes_by_params(data)
    resumes_per_page = data.get('resumes_per_page', 5)
    current_index = data.get('current_resume_index', 0)

    if not resumes:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Начать парсинг", callback_data="start_parsing_resumes")]])
        await bot.send_message(callback_query.from_user.id, 'Резюме не найдены. Начать парсинг?', reply_markup=keyboard)
        return

    end_index = current_index + resumes_per_page
    resumes_to_show = resumes[current_index:end_index]

    if resumes_to_show:
        for resume in resumes_to_show:
            resume_text = f"Профессия: {resume[1]}\n"
            resume_text += f"Пол: {resume[2]}\n"
            resume_text += f"Возраст: {resume[3]}\n"
            resume_text += f"День рождения: {resume[4]}\n"
            resume_text += f"Опыт работы: {resume[5]}\n"
            resume_text += f"Длительность последней работы: {resume[6]}\n"
            resume_text += f"Ссылка на резюме: {resume[7]}\n\n"
            await bot.send_message(callback_query.from_user.id, resume_text)

        if end_index < len(resumes):
            await state.update_data(current_resume_index=end_index)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Показать еще", callback_data="show_resumes")]])
            await bot.send_message(callback_query.from_user.id, 'Показать еще резюме?', reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Начать парсинг", callback_data="start_parsing_resumes")]])
            await bot.send_message(callback_query.from_user.id, 'Больше резюме нет. Начать парсинг?', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Начать парсинг", callback_data="start_parsing_resumes")]])
        await bot.send_message(callback_query.from_user.id, 'Больше резюме нет. Начать парсинг?', reply_markup=keyboard)

parsing_active = False

@router.callback_query(lambda c: c.data == 'start_parsing_resumes')
async def start_parsing_resumes(callback_query: types.CallbackQuery, state: FSMContext):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if not parsing_active:
        parsing_active = True
        await bot.send_message(callback_query.from_user.id, 'Начинаем парсинг резюме...')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Остановить парсинг", callback_data="stop_parsing_resumes")]])
        await bot.send_message(callback_query.from_user.id, 'Нажмите кнопку ниже, чтобы остановить парсинг.', reply_markup=keyboard)

        data = await state.get_data()
        job_title = data.get('job_title', 'python')
        conn = sqlite3.connect('vacancies_and_resumes.sql')

        await get_resumes(job_title, 0, 2, conn)

        await bot.send_message(callback_query.from_user.id, 'Парсинг резюме завершен.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг резюме уже запущен.')
    

@router.callback_query(lambda c: c.data == 'stop_parsing_resumes')
async def stop_parsing_resumes(callback_query: types.CallbackQuery):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if parsing_active:
        parsing_active = False
        await bot.send_message(callback_query.from_user.id, 'Парсинг резюме остановлен.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг резюме не запущен.')
