import time
import sys
import os
import pytgcalls
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import IMG_START, IMG_HELP, IMG_PING, IMG_RELOAD, BOT_USERNAME, OWNER_USERNAME, OWNER_ID


# ── /start ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["start"]))
async def start_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕  Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton("👤  Developer", url=f"https://t.me/{OWNER_USERNAME}"),
            InlineKeyboardButton("📢  Channel",   url=f"https://t.me/letmesolo_her"),
        ],
    ])
    text = (
        f"🎵  **Welcome to PAIN !!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋  Hey {message.from_user.mention}!\n\n"
        f"I stream **high-quality music** straight into your group's voice chat "
        f"via JioSaavn — no lags, no limits.\n\n"
        f"**Get started:**  `/play <song name>`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀"
    )
    await message.reply_photo(IMG_START, caption=text, reply_markup=buttons)


# ── /help ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["help"]))
async def help_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤  Owner / Support", url=f"https://t.me/{OWNER_USERNAME}")],
    ])
    text = (
        "🛠  **PAIN !!  —  Command Reference**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "**🎵  Playback**\n"
        "  `/play <song>`     —  Stream a song\n"
        "  `/singer <name>`   —  Queue top 5 songs by artist\n\n"
        "**🎛  Controls**\n"
        "  `/pause`   —  Pause playback\n"
        "  `/resume`  —  Resume playback\n"
        "  `/skip`    —  Skip to next track\n"
        "  `/stop`    —  Stop & leave VC\n\n"
        "**📋  Info**\n"
        "  `/queue`   —  Show queue list\n"
        "  `/ping`    —  System latency stats\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀"
    )
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)


# ── /owner ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["owner"]))
async def owner_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬  Support",  url=f"https://t.me/{OWNER_USERNAME}"),
            InlineKeyboardButton("🐛  Report Bug", url=f"https://t.me/{OWNER_USERNAME}"),
        ],
        [InlineKeyboardButton("📢  Channel", url="https://t.me/letmesolo_her")],
    ])
    text = (
        "👑  **Owner Info**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧑‍💻  **Dev:** @{OWNER_USERNAME}\n"
        f"🐛  **Bugs:** DM @{OWNER_USERNAME}\n"
        f"💡  **PAIN !!** is built & maintained by _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ with ❤️\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀"
    )
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)


# ── /ping ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["ping"]))
async def ping_cmd(client, message: Message):
    start = time.time()
    msg   = await message.reply_photo(IMG_PING, caption="⚡️  _Pinging…_")
    ms    = (time.time() - start) * 1000

    # Simple quality label
    quality = "🟢  Excellent" if ms < 100 else ("🟡  Good" if ms < 300 else "🔴  Slow")

    text = (
        "🏓  **System Stats**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡️  **Latency:**   `{ms:.1f} ms`  {quality}\n"
        f"🔗  **API Node:**  Connected ✅\n"
        f"📞  **PyTgCalls:** `v{pytgcalls.__version__}`  🟢\n"
        f"🐍  **Python:**    `{sys.version.split()[0]}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀"
    )
    await msg.edit_caption(text)


# ── /reload ───────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["reload", "restart"]))
async def reload_cmd(client, message: Message):
    if not message.from_user or message.from_user.id != OWNER_ID:
        return await message.reply(f"🚫  Only @{OWNER_USERNAME} can use this.")

    await message.reply_photo(
        IMG_RELOAD,
        caption=(
            "🔄  **Reloading engine…**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "_All modules will be restarted. Takes ~3 seconds._"
        ),
    )
    import subprocess
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)
