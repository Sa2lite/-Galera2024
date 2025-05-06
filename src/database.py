import sqlite3
import os
import time
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
    create_indexes()

def create_indexes():
    with db_connection() as cursor:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vacancies_title ON vacancies(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resumes_job_title ON resumes(job_title)')

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
        cursor.execute('SELECT id, title, company_name, salary FROM vacancies')
        return cursor.fetchall()

def get_vacancies_by_params(params):
    with db_connection() as cursor:
        query = "SELECT id, title, company_name, salary FROM vacancies WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if key not in ['vacancies_per_page', 'current_vacancy_index'] and value:
                if key == 'title':
                    query += " AND title LIKE ?"
                    query_params.append(f"{value}%")
                else:
                    query += f" AND {key} LIKE ?"
                    query_params.append(f"%{value}%")
        cursor.execute(query, query_params)
        return cursor.fetchall()

def get_all_resumes():
    with db_connection() as cursor:
        cursor.execute('SELECT id, job_title, gender, age FROM resumes')
        return cursor.fetchall()

def get_resumes_by_params(params):
    column_mapping = {
        'title': 'job_title',
    }
    with db_connection() as cursor:
        query = "SELECT id, job_title, gender, age FROM resumes WHERE 1=1"
        query_params = []
        for key, value in params.items():
            if key not in ['resumes_per_page', 'current_resume_index'] and value:
                db_column = column_mapping.get(key, key)
                if db_column == 'job_title':
                    query += " AND job_title LIKE ?"
                    query_params.append(f"{value}%")
                else:
                    query += f" AND {db_column} LIKE ?"
                    query_params.append(f"%{value}%")
        cursor.execute(query, query_params)
        return cursor.fetchall()

def clear_database():
    with db_connection() as cursor:
        cursor.execute('DELETE FROM vacancies')
        cursor.execute('DELETE FROM resumes')

def explain_query(query, params=()):
    with db_connection() as cursor:
        cursor.execute(f'EXPLAIN QUERY PLAN {query}', params)
        return cursor.fetchall()

def measure_execution_time(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    duration = time.time() - start
    print(f"Время выполнения: {duration:.4f} сек")
    return result

start = time.time()
result = get_all_vacancies()
print("Execution time:", time.time() - start)
