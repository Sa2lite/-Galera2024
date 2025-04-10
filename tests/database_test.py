import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import os
from src.database import (
    create_database,
    insert_vacancy,
    insert_resume,
    get_all_vacancies,
    get_all_resumes,
    clear_database,
    DB_PATH
)

@pytest.fixture
def test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    create_database()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_insert_and_get_vacancy(test_db):
    test_vacancy = (
        "Python Developer",
        "Tech Corp",
        "100000",
        "3+ years",
        "Full-time",
        "42",
        "http://example.com/vacancy/1"
    )
    insert_vacancy(test_vacancy)
    vacancies = get_all_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0][1] == "Python Developer"

def test_insert_and_get_resume(test_db):
    test_resume = (
        "Data Scientist",
        "Female",
        "28",
        "1995-05-15",
        "3 years",
        "1 year",
        "http://example.com/resume/1"
    )
    insert_resume(test_resume)
    resumes = get_all_resumes()
    assert len(resumes) == 1
    assert resumes[0][1] == "Data Scientist"

def test_multiple_inserts(test_db):
    insert_vacancy(("Job 1", "Company A", "100", "1", "FT", "10", "link1"))
    insert_vacancy(("Job 2", "Company B", "200", "2", "PT", "20", "link2"))
    insert_resume(("Dev 1", "M", "30", "1993", "5", "3", "res1"))
    insert_resume(("Dev 2", "F", "25", "1998", "2", "1", "res2"))
    assert len(get_all_vacancies()) == 2
    assert len(get_all_resumes()) == 2