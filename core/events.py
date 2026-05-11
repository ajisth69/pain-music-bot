import time
import asyncio
import os
from core.player import call_py
from core.clients import bot  # Pyrogram bot — NOT the pytgcalls client
from pytgcalls.types import Update, StreamEnded, MediaStream
from utils.queue import playing_chats, updater_tasks, get_next, clear_queue, process_queue_downloads
from utils.formatters import create_progress_bar, make_now_playing_caption
from utils.ui import get_player_markup
from utils.updater import progress_updater
from utils.jiosaavn import download_file


# ── Shared download-wait helper ─────────────────────────────────────────────────

async def _wait_for_download(song_data, timeout=60):
    """Block until background download completes. Returns file_path or None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        fp = song_data.get("file_path")
        if fp and os.path.exists(fp) and os.path.getsize(fp) > 0:
            return fp
        if not song_data.get("downloading"):
            return None
        await asyncio.sleep(0.5)
    return None


async def _resolve_file(chat_id, next_song):
    """Ensure next_song has a usable audio file on disk. Returns path or raises."""
    fp = next_song.get("file_path")
    if fp and os.path.exists(fp) and os.path.getsize(fp) > 0:
        return fp

    if next_song.get("downloading"):
        fp = await _wait_for_download(next_song, timeout=60)
        if not fp:
            raise Exception(f"Download timed out: {next_song['title']}")
        return fp

    # Download synchronously as a fallback
    fp = f"downloads/{chat_id}_{int(time.time())}_{id(next_song)}.mp3"
    os.makedirs("downloads", exist_ok=True)
    if not await download_file(next_song["audio_url"], fp):
        raise Exception(f"Download failed: {next_song['title']}")

    wav = fp.replace(".mp3", ".wav")
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", fp, "-ar", "48000", "-ac", "2", wav, "-y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode == 0:
            os.remove(fp)
            fp = wav
    except Exception as e:
        print(f"[events] FFmpeg failed: {e}")

    return fp


# ── Stream-ended handler ────────────────────────────────────────────────────────

@call_py.on_update()
async def stream_ended(_, update: Update):
    """pytgcalls fires this when a stream finishes. First arg is pytgcalls — use `bot`."""
    if not isinstance(update, StreamEnded):
        return

    chat_id = update.chat_id
    print(f"[events] StreamEnded  chat_id={chat_id}")

    # ── Cancel updater ──────────────────────────────────────────────────────────
    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
        updater_tasks.pop(chat_id, None)

    # ── Tidy up finished song ───────────────────────────────────────────────────
    if chat_id in playing_chats:
        old = playing_chats.pop(chat_id)
        try:
            await old["message"].edit_caption(
                "✅  **Track finished.**\n_Playing next…_",
                reply_markup=None,
            )
        except Exception:
            pass
        fp = old.get("file_path")
        if fp and os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception as e:
                print(f"[events] file remove error: {e}")

    # ── Play next from queue ────────────────────────────────────────────────────
    while True:
        next_song = get_next(chat_id)
        if not next_song:
            print(f"[events] Queue empty for {chat_id} — leaving call.")
            try:
                await call_py.leave_call(chat_id)
            except Exception:
                pass
            break

        process_queue_downloads(chat_id)  # keep prefetching ahead

        try:
            file_path = await _resolve_file(chat_id, next_song)

            await call_py.play(chat_id, MediaStream(file_path))

            bar     = create_progress_bar(0, next_song["duration"])
            caption = make_now_playing_caption(next_song, bar)
            markup  = get_player_markup(chat_id)

            try:
                player_msg = await bot.send_photo(
                    chat_id,
                    photo=next_song["thumbnail"],
                    caption=caption,
                    reply_markup=markup,
                )
            except Exception as e:
                print(f"[events] send_photo failed, fallback to text: {e}")
                player_msg = await bot.send_message(
                    chat_id, text=caption, reply_markup=markup
                )

            playing_chats[chat_id] = {
                "message":    player_msg,
                "start_time": int(time.time()),
                "duration":   next_song["duration"],
                "title":      next_song["title"],
                "artist":     next_song.get("artist", "Unknown"),
                "requester":  next_song.get("requester", "Admin"),
                "paused":     False,
                "audio_url":  next_song["audio_url"],
                "thumbnail":  next_song["thumbnail"],
                "file_path":  file_path,
            }
            updater_tasks[chat_id] = asyncio.create_task(
                progress_updater(chat_id, player_msg)
            )
            print(f"[events] ▶ {next_song['title']}  in  {chat_id}")
            break

        except Exception as e:
            print(f"[events] Failed to play '{next_song.get('title')}': {e} — trying next.")
            fp = next_song.get("file_path")
            if fp and os.path.exists(fp):
                try:
                    os.remove(fp)
                except Exception:
                    pass
