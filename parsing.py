import requests
from bs4 import BeautifulSoup
from database import db_connection, insert_vacancy

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
BASE_HH_URL = "https://hh.ru"

def fetch_page(url, headers=HEADERS):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return None

def parse_vacancies(url, parsing_active):
    page_content = fetch_page(url)
    if not page_content or not parsing_active:
        return

    soup = BeautifulSoup(page_content, 'html.parser')
    # Измененный селектор для поиска вакансий
    vacancies = soup.find_all('a', {'data-qa': 'serp-item__title'})
    
    for vacancy in vacancies:
        link = vacancy['href']
        if 'vacancy' in link:
            full_link = f"{BASE_HH_URL}{link}" if link.startswith('/') else link
            title = vacancy.find('span', {'data-qa': 'serp-item__title-text'})
            if title:
                print(f"Found vacancy: {title.text.strip()} - {full_link}")
            parse_vacancy_details(full_link, parsing_active)

def parse_vacancy_details(vacancy_url, parsing_active):
    if not parsing_active:
        return

    page_content = fetch_page(vacancy_url)
    if not page_content:
        return

    soup = BeautifulSoup(page_content, 'html.parser')
    title = soup.find('h1', {'data-qa': 'vacancy-title'})
    salary = soup.find('span', {'data-qa': 'vacancy-salary-compensation-type-net'})
    experience = soup.find('span', {'data-qa': 'vacancy-experience'})
    employment_mode = soup.find('p', {'data-qa': 'vacancy-view-employment-mode'})
    parttime_options = soup.find('p', {'data-qa': 'vacancy-view-parttime-options'})
    viewers_count = soup.find('span', class_='vacancy-viewers-count')
    company_name = soup.find('a', {'data-qa': 'vacancy-company-name'})
    response_link = soup.find('a', {'data-qa': 'vacancy-response-link-top'})

    if title:
        vacancy_data = (
            title.text.strip(),
            company_name.text.strip() if company_name else "Company name not specified",
            salary.text.strip() if salary else "Salary not specified",
            experience.text.strip() if experience else "Experience not specified",
            " ".join([
                employment_mode.text.strip() if employment_mode else "",
                parttime_options.text.strip() if parttime_options else ""
            ]).strip() or "Employment mode and part-time options not specified",
            viewers_count.text.strip() if viewers_count else "Viewers count not specified",
            f"{BASE_HH_URL}{response_link['href']}" if response_link else "Response link not specified"
        )
        insert_vacancy(vacancy_data)

def parse_multiple_pages(base_url, start_page, end_page, parsing_active):
    for page in range(start_page, end_page + 1):
        if not parsing_active:
            break
        url = f"{base_url}&page={page}"
        parse_vacancies(url, parsing_active)

def get_resumes(query, start_page, end_page, parsing_active):
    base_url = f"{BASE_HH_URL}/search/resume"
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
        page_content = fetch_page(base_url, headers=HEADERS, params=params)
        if not page_content:
            continue

        soup = BeautifulSoup(page_content, 'html.parser')
        resume_links = soup.find_all('a', {'data-qa': 'serp-item__title'})
        for link in resume_links:
            if not parsing_active:
                break
            resume_url = f"{BASE_HH_URL}{link['href']}"
            print(f"Processing resume: {resume_url}")
            resume_data = get_resume_details(resume_url)
            if resume_data:
                resume_data['resume_url'] = resume_url
                save_resume_data(resume_data)

def get_resume_details(resume_url):
    page_content = fetch_page(resume_url)
    if not page_content:
        return None

    soup = BeautifulSoup(page_content, 'html.parser')
    job_title_tag = soup.find('h2', {'data-qa': 'bloko-header-2'})
    personal_info_tag = soup.find('p')
    experience_tag = soup.find('span', {'class': 'resume-block__title-text resume-block__title-text_sub'})
    last_job_tag = soup.find('div', {'class': 'bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2'})

    return {
        "job_title": job_title_tag.get_text(strip=True) if job_title_tag else "Job Title not found",
        "gender": personal_info_tag.find('span', {'data-qa': 'resume-personal-gender'}).get_text(strip=True) if personal_info_tag else "Gender not found",
        "age": personal_info_tag.find('span', {'data-qa': 'resume-personal-age'}).get_text(strip=True) if personal_info_tag else "Age not found",
        "birthday": personal_info_tag.find('span', {'data-qa': 'resume-personal-birthday'}).get_text(strip=True) if personal_info_tag else "Birthday not found",
        "work_experience": experience_tag.get_text(strip=True) if experience_tag else "Work Experience not found",
        "last_job_duration": last_job_tag.get_text(strip=True) if last_job_tag else "Last Job Duration not found"
    }

def save_resume_data(resume_data):
    with db_connection() as cursor:
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