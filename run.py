import os
import asyncio
from aiogram import Bot, Dispatcher
from handlers import main_router



async def main():

    TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(main_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(e)