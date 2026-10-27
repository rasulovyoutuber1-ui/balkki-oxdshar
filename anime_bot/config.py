"""
Konfiguratsiya fayli
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida topilmadi!")

OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))

_admins_raw = os.getenv("ADMINS", "")
INITIAL_ADMINS: list[int] = [
    int(x.strip()) for x in _admins_raw.split(",") if x.strip().isdigit()
]

DB_NAME: str = os.getenv("DB_NAME", "anime_bot.db")
CHANNEL_POST_ID: str = os.getenv("CHANNEL_POST_ID", "")
DEFAULT_CHANNEL_ID: str = os.getenv("DEFAULT_CHANNEL_ID", "")
DEFAULT_CHANNEL_NAME: str = os.getenv("DEFAULT_CHANNEL_NAME", "Anime Kanali")
DEFAULT_CHANNEL_URL: str = os.getenv("DEFAULT_CHANNEL_URL", "")
VIP_MONTHLY_PRICE: int = int(os.getenv("VIP_MONTHLY_PRICE", "10000"))
SUPPORT_USERNAME: str = os.getenv("SUPPORT_USERNAME", "admin")
