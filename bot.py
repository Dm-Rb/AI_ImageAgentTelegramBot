from config import config_
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
import handler_login, handler_logout, handler_images
from middleware_ban import BanMiddleware


async def start_bot():

    bot = Bot(token=config_.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(handler_login.router)
    dp.include_router(handler_logout.router)
    dp.include_router(handler_images.router)
    # dp.include_router(callbacks.router)
    dp.update.middleware(BanMiddleware())  # This connected middleware contains the logic for ignoring banned users

    # Set commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Старт/Вход"),
        BotCommand(command="logout", description="Выход"),

    ])

    try:
        await dp.start_polling(bot)
    finally:
        # Close API client after end of work
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot())