import asyncio
from aiogram import Dispatcher
from handlers import router, bot
from database import create_database

async def main():
    dp = Dispatcher()
    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    create_database()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
    finally:
        print('Завершение работы бота...')