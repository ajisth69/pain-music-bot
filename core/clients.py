from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

bot = Client(
    "pain_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins") # Dynamically load plugins
)

userbot = Client(
    "pain_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)
