from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def logout_keyboard():
    # build logout keyboard
    logout_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return logout_kb
