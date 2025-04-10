from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .base_handlers import bot, VacancyForm, split_text_into_chunks
from database import get_vacancies_by_params
from parsing import parse_multiple_pages
import concurrent.futures
import asyncio

a_router = Router()
parsing_active = False

@a_router.callback_query(lambda c: c.data == 'role_applicant')
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

@a_router.callback_query(lambda c: c.data == 'vacancy_title')
async def process_callback_vacancy_title(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите название вакансии:')
    await state.set_state(VacancyForm.title)

@a_router.message(VacancyForm.title)
async def process_vacancy_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@a_router.callback_query(lambda c: c.data == 'vacancy_salary')
async def process_callback_vacancy_salary(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите зарплату:')
    await state.set_state(VacancyForm.salary)

@a_router.message(VacancyForm.salary)
async def process_vacancy_salary(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@a_router.callback_query(lambda c: c.data == 'vacancy_experience')
async def process_callback_vacancy_experience(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите требуемый опыт:')
    await state.set_state(VacancyForm.experience)

@a_router.message(VacancyForm.experience)
async def process_vacancy_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@a_router.callback_query(lambda c: c.data == 'vacancy_viewers_count')
async def process_callback_vacancy_viewers_count(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество просматривающих:')
    await state.set_state(VacancyForm.viewers_count)

@a_router.message(VacancyForm.viewers_count)
async def process_vacancy_viewers_count(message: types.Message, state: FSMContext):
    await state.update_data(viewers_count=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@a_router.callback_query(lambda c: c.data == 'vacancy_company_name')
async def process_callback_vacancy_company_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите название компании:')
    await state.set_state(VacancyForm.company_name)

@a_router.message(VacancyForm.company_name)
async def process_vacancy_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await state.set_state(None)
    await update_keyboard(message.from_user.id, state)

@a_router.callback_query(lambda c: c.data == 'vacancy_count_per_page')
async def process_callback_vacancy_count_per_page(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество вакансий, которые будут показываться за один поиск:')
    await state.set_state(VacancyForm.vacancies_per_page)

@a_router.message(VacancyForm.vacancies_per_page)
async def process_vacancy_count_per_page(message: types.Message, state: FSMContext):
    try:
        vacancies_per_page = int(message.text)
        await state.update_data(vacancies_per_page=vacancies_per_page)
        await state.set_state(None)
        await update_keyboard(message.from_user.id, state)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Пожалуйста, введите число.')

@a_router.callback_query(lambda c: c.data == 'show_vacancies')
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

@a_router.callback_query(lambda c: c.data == 'start_parsing')
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

@a_router.callback_query(lambda c: c.data == 'stop_parsing')
async def stop_parsing(callback_query: types.CallbackQuery):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if parsing_active:
        parsing_active = False
        await bot.send_message(callback_query.from_user.id, 'Парсинг остановлен.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг не запущен.')