import sqlite3

def create_database():
    conn = sqlite3.connect('vacancies_and_resumes.sql')
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

    conn.commit()
    conn.close()

def insert_vacancy(vacancy_data):
    conn = sqlite3.connect('vacancies_and_resumes.sql')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO vacancies (title, company_name, salary, experience, employment_info, viewers_count, response_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', vacancy_data)

    conn.commit()
    conn.close()

def insert_resume(resume_data):
    conn = sqlite3.connect('vacancies_and_resumes.sql')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO resumes (job_title, gender, age, birthday, work_experience, last_job_duration, resume_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', resume_data)

    conn.commit()
    conn.close()



def get_all_vacancies():
    conn = sqlite3.connect('vacancies_and_resumes.sql')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM vacancies')
    vacancies = cursor.fetchall()

    conn.close()
    return vacancies

def get_vacancies_by_params(params):
    conn = sqlite3.connect('vacancies_and_resumes.sql')
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

def get_all_resumes():
    conn = sqlite3.connect('vacancies_and_resumes.sql')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM resumes')
    resumes = cursor.fetchall()

    conn.close()
    return resumes

def get_resumes_by_params(params):
    conn = sqlite3.connect('vacancies_and_resumes.sql')
    cursor = conn.cursor()

    query = "SELECT * FROM resumes WHERE 1=1"
    query_params = []
    for key, value in params.items():
        if key != 'resumes_per_page' and key != 'current_resume_index' and value:
            query += f" AND {key} LIKE ?"
            query_params.append(f"%{value}%")

    cursor.execute(query, query_params)
    resumes = cursor.fetchall()

    conn.close()
    return resumes

def clear_database():
    conn = sqlite3.connect('vacancies_and_resumes.sql')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM vacancies')
    cursor.execute('DELETE FROM resumes')

    conn.commit()
    conn.close()