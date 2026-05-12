import subprocess
import sys
import time

import pytgcalls
from pyrogram import Client, filters
from pyrogram.types import Message

from config import IMG_HELP, IMG_PING, IMG_RELOAD, IMG_START, BOT_USERNAME, OWNER_USERNAME, OWNER_ID
from utils.fonts import bold_italic, bold_sans, smallcaps
from utils.formatters import FOOTER, GLOW_LINE, THIN_LINE, quote_block
from utils.ui import get_help_markup, get_owner_markup, get_start_markup


# ── /start ────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["start"]))
async def start_cmd(client, message: Message):
    buttons = get_start_markup(BOT_USERNAME, OWNER_USERNAME)
    intro = quote_block(
        f"👋  Hey {message.from_user.mention}!",
        "I stream **high-quality music** straight into your group voice chat.",
        "🎵  `/play <song name>`  to start",
        "🎤  `/singer <name>`  to queue top tracks",
    )
    tagline = quote_block(f"{smallcaps('Made for smooth streaming')}  ⚡")
    text = (
        f"🎧  {bold_sans('PAIN !!')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"{intro}\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{tagline}\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await message.reply_photo(IMG_START, caption=text, reply_markup=buttons)


# ── /help ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["help"]))
async def help_cmd(client, message: Message):
    buttons = get_help_markup(OWNER_USERNAME)
    playback = quote_block(
        f"🎵  {bold_sans('Playback')}",
        "`/play <song>`  —  Stream a song",
        "`/singer <name>`  —  Queue top 5 by artist",
    )
    controls = quote_block(
        f"🎛  {bold_sans('Controls')}",
        "`/pause`  —  Pause playback",
        "`/resume`  —  Resume playback",
        "`/skip`  —  Skip to next track",
        "`/stop`  —  Stop and leave VC",
    )
    info = quote_block(
        f"📋  {bold_sans('Info')}",
        "`/queue`  —  Show queue list",
        "`/ping`  —  System latency stats",
    )
    text = (
        f"📖  {bold_sans('COMMAND REFERENCE')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"{playback}\n"
        f"\n"
        f"{controls}\n"
        f"\n"
        f"{info}\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)


# ── /owner ────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["owner"]))
async def owner_cmd(client, message: Message):
    buttons = get_owner_markup(OWNER_USERNAME)
    details = quote_block(
        f"🧑‍💻  {bold_sans('Dev')}  —  @{OWNER_USERNAME}",
        f"🐛  {bold_sans('Bugs')}  —  DM @{OWNER_USERNAME}",
        f"💡  {bold_sans('PAIN !!')} is built and maintained by {smallcaps('LetMe Solo Her')}",
    )
    text = (
        f"👑  {bold_sans('DEVELOPER INFO')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"{details}\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)


# ── /ping ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["ping"]))
async def ping_cmd(client, message: Message):
    start = time.time()
    msg = await message.reply_photo(IMG_PING, caption=f"⚡  _{bold_italic('Pinging...')}_")
    ms = (time.time() - start) * 1000

    if ms < 100:
        quality = "🟢 Excellent"
        bar = "▰▰▰▰▰▱▱▱▱▱"
    elif ms < 300:
        quality = "🟡 Good"
        bar = "▰▰▰▱▱▱▱▱▱▱"
    else:
        quality = "🔴 Slow"
        bar = "▰▱▱▱▱▱▱▱▱▱"

    stats = quote_block(
        f"⚡  {bold_sans('Latency')}  —  `{ms:.1f} ms`",
        f"{bar}  {quality}",
        f"🔗  {bold_sans('API Node')}  —  Connected ✅",
        f"📞  {bold_sans('PyTgCalls')}  —  `v{pytgcalls.__version__}` 🟢",
        f"🐍  {bold_sans('Python')}  —  `{sys.version.split()[0]}`",
    )
    text = (
        f"🏓  {bold_sans('SYSTEM STATS')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"{stats}\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await msg.edit_caption(text)


# ── /reload ───────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["reload", "restart"]))
async def reload_cmd(client, message: Message):
    if not message.from_user or message.from_user.id != OWNER_ID:
        return await message.reply(f"🚫  Only @{OWNER_USERNAME} can use this.")

    status = quote_block("_All modules will be restarted._", "_Takes ~3 seconds._")
    await message.reply_photo(
        IMG_RELOAD,
        caption=(
            f"🔄  {bold_sans('RELOADING ENGINE')}\n"
            f"{GLOW_LINE}\n"
            f"\n"
            f"{status}\n"
            f"\n"
            f"{THIN_LINE}\n"
            f"{FOOTER}"
        ),
    )
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)
