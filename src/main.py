import asyncio
from aiogram import Dispatcher
from handlers.base_handlers import router, bot
from handlers.employer_handlers import e_router
from handlers.applicant_handlers import a_router
from database import create_database

async def main():
    dp = Dispatcher()
    dp.include_routers(router, e_router, a_router)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    create_database()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    finally:
        print('Завершение работы бота...')