import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.player import call_py
from utils.queue import (
    playing_chats, queued_songs, updater_tasks, get_next, clear_queue,
    process_queue_downloads, resolve_song_file,
)
from utils.audio import make_audio_stream
from utils.formatters import (
    create_progress_bar, make_now_playing_caption, format_time,
    make_queue_list, make_stopped_caption, make_skipped_caption,
    GLOW_LINE, THIN_LINE, FOOTER,
)
from utils.fonts import bold_sans, bold_italic
from utils.ui import get_player_markup
from utils.updater import progress_updater
import os


async def _play_next_song(client, chat_id, next_song, requester_mention=None):
    """Resolve file, play it, send the player card, update state."""
    process_queue_downloads(chat_id)
    file_path = await resolve_song_file(chat_id, next_song)
    await call_py.play(chat_id, make_audio_stream(file_path))

    bar     = create_progress_bar(0, next_song["duration"])
    caption = make_now_playing_caption(next_song, bar)
    markup  = get_player_markup(chat_id)

    try:
        player_msg = await client.send_photo(
            chat_id, photo=next_song["thumbnail"], caption=caption, reply_markup=markup)
    except Exception as e:
        print(f"[controls] send_photo fallback: {e}")
        player_msg = await client.send_message(chat_id, text=caption, reply_markup=markup)

    playing_chats[chat_id] = {
        "message": player_msg, "start_time": int(time.time()),
        "duration": next_song["duration"], "title": next_song["title"],
        "artist": next_song.get("artist", "Unknown"),
        "requester": next_song.get("requester", requester_mention or "Admin"),
        "paused": False, "audio_url": next_song["audio_url"],
        "thumbnail": next_song["thumbnail"], "file_path": file_path,
    }
    updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
    return player_msg


# ── /pause ──────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["pause"]))
async def pause_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply(f"⚠️  {bold_sans('No active stream found.')}")
    data = playing_chats[chat_id]
    if data["paused"]:
        return await message.reply(f"⏸  {bold_sans('Already paused.')}")
    await call_py.pause_stream(chat_id)
    data["paused"] = True
    data["pause_start_time"] = int(time.time())
    await message.reply(
        f"⏸  {bold_sans('Paused')} by {message.from_user.mention}",
        reply_markup=get_player_markup(chat_id),
    )


# ── /resume ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["resume"]))
async def resume_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply(f"⚠️  {bold_sans('No active stream found.')}")
    data = playing_chats[chat_id]
    if not data["paused"]:
        return await message.reply(f"▶️  {bold_sans('Already playing.')}")
    await call_py.resume_stream(chat_id)
    data["paused"] = False
    pause_dur = int(time.time()) - data.get("pause_start_time", int(time.time()))
    data["start_time"] += pause_dur
    await message.reply(
        f"▶️  {bold_sans('Resumed')} by {message.from_user.mention}",
        reply_markup=get_player_markup(chat_id),
    )


# ── /stop ────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["stop", "end"]))
async def stop_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply(f"⚠️  {bold_sans('No active stream found.')}")
    clear_queue(chat_id)
    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
        updater_tasks.pop(chat_id, None)
    if chat_id in playing_chats:
        fp = playing_chats[chat_id].get("file_path")
        if fp and os.path.exists(fp):
            try: os.remove(fp)
            except Exception: pass
        playing_chats.pop(chat_id, None)
    try: await call_py.leave_call(chat_id)
    except Exception: pass
    await message.reply(make_stopped_caption(message.from_user.mention))


# ── /skip ────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["skip", "next"]))
async def skip_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply(f"⚠️  {bold_sans('No active stream found.')}")
    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
        updater_tasks.pop(chat_id, None)
    old_fp = playing_chats[chat_id].get("file_path")
    if old_fp and os.path.exists(old_fp):
        try: os.remove(old_fp)
        except Exception: pass
    playing_chats.pop(chat_id, None)

    next_song = get_next(chat_id)
    if not next_song:
        try: await call_py.leave_call(chat_id)
        except Exception: pass
        return await message.reply(
            make_skipped_caption(message.from_user.mention) +
            "\n  📋  _Queue is empty — leaving VC._"
        )
    try:
        await _play_next_song(client, chat_id, next_song, message.from_user.mention)
        await message.reply(
            f"⏭  {bold_sans('Skipped')} by {message.from_user.mention}",
            reply_markup=get_player_markup(chat_id),
        )
    except Exception as e:
        await message.reply(f"❌  {bold_sans('Skip failed:')} `{e}`")


# ── /queue ────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command(["queue", "q"]))
async def queue_cmd(client, message: Message):
    chat_id = message.chat.id
    q   = queued_songs.get(chat_id, [])
    now = playing_chats.get(chat_id)
    caption = make_queue_list(now, q)
    await message.reply(caption, reply_markup=get_player_markup(chat_id) if now else None)
