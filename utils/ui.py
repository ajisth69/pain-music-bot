from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue import playing_chats
from config import OWNER_USERNAME

def get_player_markup(chat_id):
    is_paused = playing_chats.get(chat_id, {}).get("paused", False)
    play_pause_btn = InlineKeyboardButton("▷" if is_paused else "II", callback_data=f"pause_resume_{chat_id}")
    return InlineKeyboardMarkup([
        [play_pause_btn, InlineKeyboardButton("II", callback_data=f"pause_resume_{chat_id}"), InlineKeyboardButton("‣I", callback_data=f"skip_{chat_id}"), InlineKeyboardButton("◻", callback_data=f"stop_{chat_id}")],
        [InlineKeyboardButton("✧ ᴄʟᴏsᴇ ✧", callback_data=f"stop_{chat_id}")]
    ])
