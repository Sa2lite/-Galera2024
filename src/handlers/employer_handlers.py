from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .base_handlers import  bot, ResumeForm, split_text_into_chunks
from database import get_resumes_by_params
from parsing import get_resumes
import concurrent.futures
import asyncio
import sqlite3

e_router = Router()
parsing_active = False

@e_router.callback_query(lambda c: c.data == 'role_employer')
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

@e_router.callback_query(lambda c: c.data == 'resume_job_title')
async def process_callback_resume_job_title(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите профессию:')
    await state.set_state(ResumeForm.job_title)

@e_router.message(ResumeForm.job_title)
async def process_resume_job_title(message: types.Message, state: FSMContext):
    await state.update_data(job_title=message.text)
    await state.set_state(None)
    await update_resume_keyboard(message.from_user.id, state)

@e_router.callback_query(lambda c: c.data == 'resume_work_experience')
async def process_callback_resume_work_experience(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите опыт работы:')
    await state.set_state(ResumeForm.work_experience)

@e_router.message(ResumeForm.work_experience)
async def process_resume_work_experience(message: types.Message, state: FSMContext):
    await state.update_data(work_experience=message.text)
    await state.set_state(None)
    await update_resume_keyboard(message.from_user.id, state)

@e_router.callback_query(lambda c: c.data == 'resume_age')
async def process_callback_resume_age(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите возраст:')
    await state.set_state(ResumeForm.age)

@e_router.message(ResumeForm.age)
async def process_resume_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(None)
    await update_resume_keyboard(message.from_user.id, state)

@e_router.callback_query(lambda c: c.data == 'resume_count_per_page')
async def process_callback_resume_count_per_page(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Укажите количество резюме, которые будут показываться за один поиск:')
    await state.set_state(ResumeForm.resumes_per_page)

@e_router.message(ResumeForm.resumes_per_page)
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

@e_router.callback_query(lambda c: c.data == 'show_resumes')
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

@e_router.callback_query(lambda c: c.data == 'start_parsing_resumes')
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

@e_router.callback_query(lambda c: c.data == 'stop_parsing_resumes')
async def stop_parsing_resumes(callback_query: types.CallbackQuery):
    global parsing_active
    await bot.answer_callback_query(callback_query.id)
    if parsing_active:
        parsing_active = False
        await bot.send_message(callback_query.from_user.id, 'Парсинг резюме остановлен.')
    else:
        await bot.send_message(callback_query.from_user.id, 'Парсинг резюме не запущен.')