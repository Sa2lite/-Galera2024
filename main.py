import asyncio
from aiogram import Bot, Dispatcher
from handlers import dp

bot = Bot(token='7396063867:AAHT-46Dwu1Aa1NQJcFurr_XzpKY5w1uzCk')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
