# parsing.py
import requests
from bs4 import BeautifulSoup
from database import *


def parse_vacancies(url, parsing_active):
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
                parse_vacancy_title(full_link, parsing_active)
                
def parse_vacancy_title(vacancy_url, parsing_active):
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

def parse_multiple_pages(base_url, start_page, end_page, parsing_active):
    for page in range(start_page, end_page + 1):
        if not parsing_active:
            break
        url = f"{base_url}&page={page}"
        parse_vacancies(url, parsing_active)

def get_resumes(query, start_page, end_page, conn, parsing_active):
    base_url = "https://hh.ru/search/resume"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    for page in range(start_page, end_page + 1):
        if not parsing_active:
            break
        params = {
            "text": query,
            "pos": "full_text",
            "logic": "normal",
            "exp_period": "all_time",
            "ored_clusters": "true",
            "order_by": "relevance",
            "search_period": "0",
            "page": page
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            resume_links = soup.find_all('a', {'data-qa': 'serp-item__title'})
            
            for link in resume_links:
                if not parsing_active:
                    break
                resume_url = "https://hh.ru" + link['href']
                print(f"Processing resume: {resume_url}")
                resume_data = get_resume_details(resume_url, headers)
                if resume_data:
                    resume_data['resume_url'] = resume_url
                    save_resume_data(resume_data, conn)
        else:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")

def get_resume_details(resume_url, headers):
    response = requests.get(resume_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_title_tag = soup.find('h2', {'data-qa': 'bloko-header-2'})
        job_title = job_title_tag.get_text(strip=True) if job_title_tag else "Job Title not found"
        
        personal_info_tag = soup.find('p')
        gender = "Gender not found"
        age = "Age not found"
        birthday = "Birthday not found"
        if personal_info_tag:
            gender_tag = personal_info_tag.find('span', {'data-qa': 'resume-personal-gender'})
            age_tag = personal_info_tag.find('span', {'data-qa': 'resume-personal-age'})
            birthday_tag = personal_info_tag.find('span', {'data-qa': 'resume-personal-birthday'})
            
            gender = gender_tag.get_text(strip=True) if gender_tag else "Gender not found"
            age = age_tag.get_text(strip=True) if age_tag else "Age not found"
            birthday = birthday_tag.get_text(strip=True) if birthday_tag else "Birthday not found"
        
        experience_tag = soup.find('span', {'class': 'resume-block__title-text resume-block__title-text_sub'})
        work_experience = experience_tag.get_text(strip=True) if experience_tag else "Work Experience not found"
        
        last_job_tag = soup.find('div', {'class': 'bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2'})
        last_job_duration = last_job_tag.get_text(strip=True) if last_job_tag else "Last Job Duration not found"
        
        return {
            "job_title": job_title,
            "gender": gender,
            "age": age,
            "birthday": birthday,
            "work_experience": work_experience,
            "last_job_duration": last_job_duration
        }
    else:
        print(f"Failed to retrieve resume details. Status code: {response.status_code}")
        return None

def save_resume_data(resume_data, conn):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resumes (job_title, gender, age, birthday, work_experience, last_job_duration, resume_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_data['job_title'],
        resume_data['gender'],
        resume_data['age'],
        resume_data['birthday'],
        resume_data['work_experience'],
        resume_data['last_job_duration'],
        resume_data['resume_url']
    ))
    conn.commit()