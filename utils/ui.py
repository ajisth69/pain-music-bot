from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue import playing_chats, queued_songs
from utils.fonts import bold_sans, smallcaps
from config import OWNER_USERNAME

# ── Mini-app / channel URL ──────────────────────────────────────────────────────
MINI_APP_URL = "https://clashmusic.vercel.app"
CHANNEL_URL  = "https://t.me/letmesolo_her"


def get_queue_line(chat_id: int) -> str:
    """Returns a short queue status string for button labels."""
    q = queued_songs.get(chat_id, [])
    count = len(q)
    return f"📋 {count} Song{'s' if count != 1 else ''}" if q else "📋 Empty"


def get_player_markup(chat_id: int) -> InlineKeyboardMarkup:
    """
    ✨ Premium player control panel with colorful emoji buttons ✨

    Row 1 — Main playback controls (colorful)
      [⏸ 𝗣𝗮𝘂𝘀𝗲 / ▶️ 𝗣𝗹𝗮𝘆]  [⏭ 𝗡𝗲𝘅𝘁]  [⏹ 𝗦𝘁𝗼𝗽]
    Row 2 — Queue & extras
      [📋 𝗤𝘂𝗲𝘂𝗲 (N)]  [🔁 𝗟𝗼𝗼𝗽]
    Row 3 — Links
      [🌐 𝗠𝗶𝗻𝗶 𝗔𝗽𝗽]  [📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹]
    Row 4 — Close
      [✖ 𝗖𝗹𝗼𝘀𝗲]
    """
    is_paused = playing_chats.get(chat_id, {}).get("paused", False)

    if is_paused:
        pp_text = "▶️ 𝗥𝗲𝘀𝘂𝗺𝗲"
    else:
        pp_text = "⏸ 𝗣𝗮𝘂𝘀𝗲"

    return InlineKeyboardMarkup([
        # ── Row 1: main playback ──────────────────────────────────────────────
        [
            InlineKeyboardButton(pp_text, callback_data=f"pause_resume|{chat_id}"),
            InlineKeyboardButton("⏭ 𝗡𝗲𝘅𝘁", callback_data=f"skip|{chat_id}"),
            InlineKeyboardButton("⏹ 𝗦𝘁𝗼𝗽", callback_data=f"stop|{chat_id}"),
        ],
        # ── Row 2: queue & info ───────────────────────────────────────────────
        [
            InlineKeyboardButton(f"📋 {get_queue_line(chat_id)}", callback_data=f"queue_info|{chat_id}"),
            InlineKeyboardButton("🔄 𝗥𝗲𝗽𝗹𝗮𝘆", callback_data=f"replay|{chat_id}"),
        ],
        # ── Row 3: external links ─────────────────────────────────────────────
        [
            InlineKeyboardButton("🌐 𝗠𝗶𝗻𝗶 𝗔𝗽𝗽", url=MINI_APP_URL),
            InlineKeyboardButton("📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=CHANNEL_URL),
        ],
        # ── Row 4: close ──────────────────────────────────────────────────────
        [
            InlineKeyboardButton("✖ 𝗖𝗹𝗼𝘀𝗲", callback_data=f"close_panel|{chat_id}"),
        ],
    ])


def get_start_markup(bot_username: str, owner_username: str) -> InlineKeyboardMarkup:
    """Premium /start inline buttons."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ 𝗔𝗱𝗱 𝘁𝗼 𝗚𝗿𝗼𝘂𝗽", url=f"https://t.me/{bot_username}?startgroup=true"),
        ],
        [
            InlineKeyboardButton("👤 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿", url=f"https://t.me/{owner_username}"),
            InlineKeyboardButton("📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=CHANNEL_URL),
        ],
        [
            InlineKeyboardButton("❓ 𝗛𝗲𝗹𝗽", url=f"https://t.me/{bot_username}?start=help"),
            InlineKeyboardButton("🌐 𝗠𝗶𝗻𝗶 𝗔𝗽𝗽", url=MINI_APP_URL),
        ],
    ])


def get_help_markup(owner_username: str) -> InlineKeyboardMarkup:
    """Premium /help inline buttons."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 𝗦𝘂𝗽𝗽𝗼𝗿𝘁", url=f"https://t.me/{owner_username}"),
            InlineKeyboardButton("📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=CHANNEL_URL),
        ],
    ])


def get_owner_markup(owner_username: str) -> InlineKeyboardMarkup:
    """Premium /owner inline buttons."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 𝗦𝘂𝗽𝗽𝗼𝗿𝘁", url=f"https://t.me/{owner_username}"),
            InlineKeyboardButton("🐛 𝗥𝗲𝗽𝗼𝗿𝘁 𝗕𝘂𝗴", url=f"https://t.me/{owner_username}"),
        ],
        [
            InlineKeyboardButton("📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=CHANNEL_URL),
        ],
    ])


def get_queue_markup(chat_id: int) -> InlineKeyboardMarkup:
    """Back button for queue info messages."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸 𝘁𝗼 𝗣𝗹𝗮𝘆𝗲𝗿", callback_data=f"back_player|{chat_id}")]
    ])
