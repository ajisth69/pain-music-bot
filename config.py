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

IMG_START = "https://tse4.mm.bing.net/th/id/OIP.dJlsP_XjmFw5POYAZvrKhQHaFj?r=0&w=1024&h=768&rs=1&pid=ImgDetMain&o=7&rm=3"
IMG_HELP = "https://wallpapercave.com/wp/XpfEz41.jpg"
IMG_PING = "https://tse4.mm.bing.net/th/id/OIP.aXkVny3mSVRGKDvni4SYEwHaE8?r=0&w=1920&h=1280&rs=1&pid=ImgDetMain&o=7&rm=3"
IMG_RELOAD = "https://motionbgs.com/media/1292/pain-nagato.jpg"
IMG_DEFAULT = "https://motionbgs.com/media/1292/pain-nagato.jpg"

JIOSAAVN_API_PRIMARY = "https://jiosaavn-api-two-beta.vercel.app/api/search/songs?query="
JIOSAAVN_API_SECONDARY = "https://jiosavan.ajisth007.workers.dev/api/search/songs?query="
