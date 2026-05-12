import time
import asyncio
import os
from core.player import call_py
from core.clients import bot
from pytgcalls.types import Update, StreamEnded
from utils.queue import (
    playing_chats, updater_tasks, get_next, clear_queue, process_queue_downloads,
    resolve_song_file,
)
from utils.formatters import (
    create_progress_bar, make_now_playing_caption, make_track_finished_caption,
)
from utils.ui import get_player_markup
from utils.updater import progress_updater
from utils.audio import make_audio_stream


@call_py.on_update()
async def stream_ended(_, update: Update):
    if not isinstance(update, StreamEnded):
        return

    chat_id = update.chat_id
    print(f"[events] StreamEnded  chat_id={chat_id}")

    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
        updater_tasks.pop(chat_id, None)

    if chat_id in playing_chats:
        old = playing_chats.pop(chat_id)
        try:
            await old["message"].edit_caption(
                make_track_finished_caption(), reply_markup=None)
        except Exception:
            pass
        fp = old.get("file_path")
        if fp and os.path.exists(fp):
            try: os.remove(fp)
            except Exception as e: print(f"[events] file remove error: {e}")

    while True:
        next_song = get_next(chat_id)
        if not next_song:
            print(f"[events] Queue empty for {chat_id} — leaving call.")
            try: await call_py.leave_call(chat_id)
            except Exception: pass
            break

        process_queue_downloads(chat_id)

        try:
            file_path = await resolve_song_file(chat_id, next_song)
            await call_py.play(chat_id, make_audio_stream(file_path))

            bar     = create_progress_bar(0, next_song["duration"])
            caption = make_now_playing_caption(next_song, bar)
            markup  = get_player_markup(chat_id)

            try:
                player_msg = await bot.send_photo(
                    chat_id, photo=next_song["thumbnail"],
                    caption=caption, reply_markup=markup)
            except Exception as e:
                print(f"[events] send_photo failed, fallback: {e}")
                player_msg = await bot.send_message(
                    chat_id, text=caption, reply_markup=markup)

            playing_chats[chat_id] = {
                "message": player_msg, "start_time": int(time.time()),
                "duration": next_song["duration"], "title": next_song["title"],
                "artist": next_song.get("artist", "Unknown"),
                "requester": next_song.get("requester", "Admin"),
                "paused": False, "audio_url": next_song["audio_url"],
                "thumbnail": next_song["thumbnail"], "file_path": file_path,
            }
            updater_tasks[chat_id] = asyncio.create_task(
                progress_updater(chat_id, player_msg))
            print(f"[events] ▶ {next_song['title']}  in  {chat_id}")
            break

        except Exception as e:
            print(f"[events] Failed to play '{next_song.get('title')}': {e}")
            fp = next_song.get("file_path")
            if fp and os.path.exists(fp):
                try: os.remove(fp)
                except Exception: pass
