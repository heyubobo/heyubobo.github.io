import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "momo.db"
MEMORY_INDEX_PATH = BASE_DIR / "memory.index"
MEMORY_PKL_PATH = BASE_DIR / "memory.pkl"

DEFAULT_USER_ID = os.getenv("MOMO_USER_ID", "bobo")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

CHAT_MODEL = os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-chat")
SUMMARY_MODEL = os.getenv("DEEPSEEK_SUMMARY_MODEL", "deepseek-chat")

RECENT_MESSAGES_LIMIT = 10
SUMMARY_EVERY_N_MESSAGES = 20
SUMMARY_HISTORY_LIMIT = 50
MEMORY_SEARCH_K = 3
