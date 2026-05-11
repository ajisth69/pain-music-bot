from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.queue import playing_chats, queued_songs
from config import OWNER_USERNAME

# ── Mini-app / channel URL ──────────────────────────────────────────────────────
MINI_APP_URL = "https://clashmusic.vercel.app"


def get_queue_line(chat_id: int) -> str:
    """Returns a short queue status string for button labels."""
    q = queued_songs.get(chat_id, [])
    return f"📋 Queue  ({len(q)})" if q else "📋 Queue  (empty)"


def get_player_markup(chat_id: int) -> InlineKeyboardMarkup:
    """
    Premium player control panel.

    Row 1 — Playback controls
      [⏮ Prev*]  [⏸/▶ Play-Pause]  [⏭ Skip]  [⏹ Stop]
    Row 2 — Info / external
      [📋 Queue (N)]  [🌐 Mini App]
    Row 3 — Close
      [✖  Close]

    *Prev is wired to stop (no prev-track feature) but kept for visual balance.
    """
    is_paused = playing_chats.get(chat_id, {}).get("paused", False)
    pp_icon   = "▶️  Play" if is_paused else "⏸  Pause"

    return InlineKeyboardMarkup([
        # ── Row 1: main controls ───────────────────────────────────────────────
        [
            InlineKeyboardButton("⏸  Pause" if not is_paused else "▶️  Resume",
                                 callback_data=f"pause_resume|{chat_id}"),
            InlineKeyboardButton("⏭  Skip",  callback_data=f"skip|{chat_id}"),
            InlineKeyboardButton("⏹  Stop",  callback_data=f"stop|{chat_id}"),
        ],
        # ── Row 2: queue status + mini-app ────────────────────────────────────
        [
            InlineKeyboardButton(get_queue_line(chat_id), callback_data=f"queue_info|{chat_id}"),
            InlineKeyboardButton("🌐  Mini App", url=MINI_APP_URL),
        ],
        # ── Row 3: close ──────────────────────────────────────────────────────
        [
            InlineKeyboardButton("✖  Close", callback_data=f"stop|{chat_id}"),
        ],
    ])


def get_queue_markup(chat_id: int) -> InlineKeyboardMarkup:
    """Simple back-button for queue info messages."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙  Back", callback_data=f"back_player|{chat_id}")]
    ])
