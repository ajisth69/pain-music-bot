import time
import sys
import os
import pytgcalls
from pyrogram import Client, filters
from pyrogram.types import Message
from config import IMG_START, IMG_HELP, IMG_PING, IMG_RELOAD, BOT_USERNAME, OWNER_USERNAME, OWNER_ID
from utils.fonts import bold_sans, bold_italic, smallcaps, outline, mono
from utils.formatters import GLOW_LINE, THIN_LINE, FOOTER, BRAND_LINE
from utils.ui import get_start_markup, get_help_markup, get_owner_markup


# ── /start ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["start"]))
async def start_cmd(client, message: Message):
    buttons = get_start_markup(BOT_USERNAME, OWNER_USERNAME)
    text = (
        f"🎧  {bold_sans('PAIN !!')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"  👋  Hey {message.from_user.mention}!\n"
        f"\n"
        f"  I stream **high-quality music** straight\n"
        f"  into your group's voice chat\n"
        f"  — no lags, no limits.\n"
        f"\n"
        f"  🎵  `/play <song name>`  to get started!\n"
        f"  🎤  `/singer <name>`  to queue top tracks\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"  {smallcaps('Made for smooth streaming')}  ⚡\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await message.reply_photo(IMG_START, caption=text, reply_markup=buttons)


# ── /help ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["help"]))
async def help_cmd(client, message: Message):
    buttons = get_help_markup(OWNER_USERNAME)
    text = (
        f"📖  {bold_sans('COMMAND REFERENCE')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"  🎵  {bold_sans('Playback')}\n"
        f"  ├  `/play <song>`  ─  Stream a song\n"
        f"  └  `/singer <name>`  ─  Queue top 5 by artist\n"
        f"\n"
        f"  🎛  {bold_sans('Controls')}\n"
        f"  ├  `/pause`  ─  Pause playback\n"
        f"  ├  `/resume`  ─  Resume playback\n"
        f"  ├  `/skip`  ─  Skip to next track\n"
        f"  └  `/stop`  ─  Stop & leave VC\n"
        f"\n"
        f"  📋  {bold_sans('Info')}\n"
        f"  ├  `/queue`  ─  Show queue list\n"
        f"  └  `/ping`  ─  System latency stats\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)


# ── /owner ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["owner"]))
async def owner_cmd(client, message: Message):
    buttons = get_owner_markup(OWNER_USERNAME)
    text = (
        f"👑  {bold_sans('DEVELOPER INFO')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"  🧑‍💻  {bold_sans('Dev')}  ─  @{OWNER_USERNAME}\n"
        f"  🐛  {bold_sans('Bugs')}  ─  DM @{OWNER_USERNAME}\n"
        f"\n"
        f"  💡  {bold_sans('PAIN !!')} is built & maintained\n"
        f"     by {smallcaps('LetMe Solo Her')} with ❤️\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
    )
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)


# ── /ping ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["ping"]))
async def ping_cmd(client, message: Message):
    start = time.time()
    msg   = await message.reply_photo(IMG_PING, caption=f"⚡  _{bold_italic('Pinging...')}_")
    ms    = (time.time() - start) * 1000

    # Quality with colored indicators
    if ms < 100:
        quality = "🟢 Excellent"
        bar = "▰▰▰▰▰▱▱▱▱▱"
    elif ms < 300:
        quality = "🟡 Good"
        bar = "▰▰▰▱▱▱▱▱▱▱"
    else:
        quality = "🔴 Slow"
        bar = "▰▱▱▱▱▱▱▱▱▱"

    text = (
        f"🏓  {bold_sans('SYSTEM STATS')}\n"
        f"{GLOW_LINE}\n"
        f"\n"
        f"  ⚡  {bold_sans('Latency')}   ─  `{ms:.1f} ms`\n"
        f"      {bar}  {quality}\n"
        f"\n"
        f"  🔗  {bold_sans('API Node')}  ─  Connected ✅\n"
        f"  📞  {bold_sans('PyTgCalls')} ─  `v{pytgcalls.__version__}` 🟢\n"
        f"  🐍  {bold_sans('Python')}    ─  `{sys.version.split()[0]}`\n"
        f"\n"
        f"{THIN_LINE}\n"
        f"{FOOTER}"
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
            f"🔄  {bold_sans('RELOADING ENGINE')}\n"
            f"{GLOW_LINE}\n"
            f"\n"
            f"  _All modules will be restarted._\n"
            f"  _Takes ~3 seconds._\n"
            f"\n"
            f"{THIN_LINE}\n"
            f"{FOOTER}"
        ),
    )
    import subprocess
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)
