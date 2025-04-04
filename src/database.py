import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), '../db/vacancies.db')

@contextmanager
def db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()

def create_database():
    with db_connection() as cursor:
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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT,
                gender TEXT,
                age TEXT,
                birthday TEXT,
                work_experience TEXT,
                last_job_duration TEXT,
                resume_url TEXT
            )
        ''')

def insert_vacancy(vacancy_data):
    with db_connection() as cursor:
        cursor.execute('''
            INSERT INTO vacancies (title, company_name, salary, experience, employment_info, viewers_count, response_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', vacancy_data)

def insert_resume(resume_data):
    with db_connection() as cursor:
        cursor.execute('''
            INSERT INTO resumes (job_title, gender, age, birthday, work_experience, last_job_duration, resume_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', resume_data)

def get_all_vacancies():
    with db_connection() as cursor:
        cursor.execute('SELECT * FROM vacancies')
        return cursor.fetchall()

def get_vacancies_by_params(params):
    with db_connection() as cursor:
        query = "SELECT * FROM vacancies WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if key not in ['vacancies_per_page', 'current_vacancy_index'] and value:
                query += f" AND {key} LIKE ?"
                query_params.append(f"%{value}%")
        cursor.execute(query, query_params)
        return cursor.fetchall()

def get_all_resumes():
    with db_connection() as cursor:
        cursor.execute('SELECT * FROM resumes')
        return cursor.fetchall()

def get_resumes_by_params(params):
    column_mapping = {
        'title': 'job_title',
    }
    
    with db_connection() as cursor:
        query = "SELECT * FROM resumes WHERE 1=1"
        query_params = []
        
        for key, value in params.items():
            if key not in ['resumes_per_page', 'current_resume_index'] and value:
                db_column = column_mapping.get(key, key)
                query += f" AND {db_column} LIKE ?"
                query_params.append(f"%{value}%")
                
        cursor.execute(query, query_params)
        return cursor.fetchall()

def clear_database():
    with db_connection() as cursor:
        cursor.execute('DELETE FROM vacancies')
        cursor.execute('DELETE FROM resumes')