from unittest.mock import patch
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.parsing import (
    fetch_page,
    parse_vacancy_details,
    get_resume_details,
    parse_vacancies
)

example_vacancy_html = '''
<html>
    <h1 data-qa="vacancy-title">Python Developer</h1>
    <span data-qa="vacancy-salary-compensation-type-net">100 000 ₽</span>
    <span data-qa="vacancy-experience">3–6 лет</span>
    <p data-qa="vacancy-view-employment-mode">Полный день</p>
    <p data-qa="vacancy-view-parttime-options">Можно удалённо</p>
    <span class="vacancy-viewers-count">42</span>
    <a data-qa="vacancy-company-name">Some Company</a>
    <a data-qa="vacancy-response-link-top" href="/respond">Откликнуться</a>
</html>
'''

example_resume_html = '''
<html>
    <h2 data-qa="bloko-header-2">Senior Python Dev</h2>
    <p>
        <span data-qa="resume-personal-gender">Мужской</span>
        <span data-qa="resume-personal-age">30 лет</span>
        <span data-qa="resume-personal-birthday">01.01.1994</span>
    </p>
    <span class="resume-block__title-text resume-block__title-text_sub">Опыт работы 5 лет</span>
    <div class="bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2">2 года в последней компании</div>
</html>
'''


@patch("src.parsing.fetch_page", return_value=example_vacancy_html)
@patch("src.parsing.insert_vacancy")
def test_parse_vacancy_details(mock_insert, mock_fetch):
    parse_vacancy_details("https://hh.ru/vacancy/123", parsing_active=True)
    mock_insert.assert_called_once()
    args = mock_insert.call_args[0][0]
    assert "Python Developer" in args
    assert "100 000 ₽" in args

@patch("src.parsing.fetch_page", return_value=example_resume_html)
def test_get_resume_details(mock_fetch):
    data = get_resume_details("https://hh.ru/resume/123")
    assert data['job_title'] == "Senior Python Dev"
    assert data['gender'] == "Мужской"
    assert data['age'] == "30 лет"
    assert data['birthday'] == "01.01.1994"
    assert "5 лет" in data['work_experience']

@patch("src.parsing.parse_vacancy_details")
@patch("src.parsing.fetch_page")
def test_parse_vacancies_calls_detail(mock_fetch, mock_detail):
    html = '''
    <html>
        <a data-qa="serp-item__title" href="/vacancy/1">
            <span data-qa="serp-item__title-text">Vacancy 1</span>
        </a>
    </html>
    '''
    mock_fetch.return_value = html
    parse_vacancies("https://hh.ru/search/vacancy", parsing_active=True)
    mock_detail.assert_called_once()
