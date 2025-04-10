import pytest
import sys
from pathlib import Path
from aiogram import types
from src.database import *

sys.path.append(str(Path(__file__).parent.parent / "src"))
from handlers.base_handlers import (
    router,
    VacancyForm,
    ResumeForm,
    start,
    start_button,
    help_button,
    clear_database_button,
    confirm_clear_database,
    bot
)
class MockMessage:
    def __init__(self, text=""):
        self.text = text
        self.chat = types.Chat(id=1234, type="private")
        self.from_user = types.User(id=1234, is_bot=False, first_name="Test")
        self.message_id = 1

    async def answer(self, text, reply_markup=None):
        assert isinstance(text, str)
        return text

class MockCallbackQuery:
    def __init__(self, data):
        self.data = data
        self.from_user = types.User(id=1234, is_bot=False, first_name="Test")
        self.id = "callback_query_id"

    async def answer(self):
        pass

    async def message(self):
        return self

@pytest.mark.asyncio
async def test_start():
    message = MockMessage("/start")
    response = await start(message)
    assert response is None  

@pytest.mark.asyncio
async def test_start_button():
    message = MockMessage("Старт")
    response = await start_button(message)
    assert response is None

@pytest.mark.asyncio
async def test_clear_database_button():
    message = MockMessage("Очистить базу данных")
    response = await clear_database_button(message)
    assert response is None


