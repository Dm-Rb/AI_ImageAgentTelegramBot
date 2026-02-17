import os
from dotenv import load_dotenv


"""Load environment variables from .env"""


load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    PASSPHRASE = os.getenv("PASSPHRASE")
    API_TOKEN = os.getenv("API_TOKEN")
    API_BASE_URL = os.getenv("API_BASE_URL")
    EP_GENERATIONS = os.getenv("EP_GENERATIONS")
    EP_EDITS = os.getenv("EP_EDITS")


config_ = Config()