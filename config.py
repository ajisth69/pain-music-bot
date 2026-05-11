import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

OWNER_ID = int(os.environ.get("OWNER_ID", 0))
LOGGER_ID = int(os.environ.get("LOGGER_ID", 0))
BOT_USERNAME = os.environ.get("BOT_USERNAME")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME")

IMG_START = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png"
IMG_HELP = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png"
IMG_PING = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png"
IMG_RELOAD = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png"
IMG_DEFAULT = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/512px-Telegram_logo.svg.png"

JIOSAAVN_API_PRIMARY = "https://jiosaavn-api-two-beta.vercel.app/api/search/songs?query="
JIOSAAVN_API_SECONDARY = "https://jiosavan.ajisth007.workers.dev/api/search/songs?query="
