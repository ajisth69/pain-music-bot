import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from core.player import call_py
import os
from utils.queue import playing_chats, queued_songs, updater_tasks, get_next, clear_queue, process_queue_downloads
from utils.jiosaavn import download_file
from utils.ui import get_player_markup
from pytgcalls.types import MediaStream
from utils.formatters import (
    create_progress_bar, make_now_playing_caption, format_time,
    make_stopped_caption, make_skipped_caption, make_queue_list,
)
from utils.fonts import bold_sans
from utils.updater import progress_updater
from utils.audio import prepare_audio


async def _wait_for_download(song_data, timeout=60):
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
    fp = next_song.get("file_path")
    if fp and os.path.exists(fp) and os.path.getsize(fp) > 0:
        return fp
    if next_song.get("downloading"):
        fp = await _wait_for_download(next_song, timeout=60)
        if not fp:
            raise Exception(f"Download timed out: {next_song['title']}")
        return fp
    fp = f"downloads/{chat_id}_{int(time.time())}_{id(next_song)}.mp3"
    os.makedirs("downloads", exist_ok=True)
    if not await download_file(next_song["audio_url"], fp):
        raise Exception(f"Download failed: {next_song['title']}")
    return await prepare_audio(fp)


@Client.on_callback_query(filters.regex(r"^(pause_resume|skip|stop|queue_info|back_player|replay|close_panel)\|"))
async def callbacks(client, query: CallbackQuery):
    action, chat_id_str = query.data.split("|", 1)
    chat_id = int(chat_id_str)

    # ── close_panel ───────────────────────────────────────────────────────────
    if action == "close_panel":
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.answer("✖ Closed")
        return

    # ── queue_info ────────────────────────────────────────────────────────────
    if action == "queue_info":
        q   = queued_songs.get(chat_id, [])
        now = playing_chats.get(chat_id)
        caption = make_queue_list(now, q)
        try:
            await query.answer()
            await query.message.edit_caption(caption, reply_markup=get_player_markup(chat_id))
        except Exception:
            pass
        return

    # ── back_player ──────────────────────────────────────────────────────────
    if action == "back_player":
        now = playing_chats.get(chat_id)
        if now:
            played  = int(time.time()) - now["start_time"]
            bar     = create_progress_bar(played, now["duration"])
            caption = make_now_playing_caption(now, bar)
            try:
                await query.answer()
                await query.message.edit_caption(caption, reply_markup=get_player_markup(chat_id))
            except Exception:
                pass
        else:
            await query.answer("Nothing playing.", show_alert=True)
        return

    # ── replay ────────────────────────────────────────────────────────────────
    if action == "replay":
        if chat_id not in playing_chats:
            return await query.answer("⚠️  No active stream.", show_alert=True)
        data = playing_chats[chat_id]
        fp = data.get("file_path")
        if fp and os.path.exists(fp):
            try:
                await call_py.play(chat_id, MediaStream(fp))
                data["start_time"] = int(time.time())
                data["paused"] = False
                await query.answer("🔄 Replaying!")
                try:
                    await query.message.edit_reply_markup(reply_markup=get_player_markup(chat_id))
                except Exception:
                    pass
            except Exception as e:
                await query.answer(f"❌ {e}", show_alert=True)
        else:
            await query.answer("❌ Audio file not found.", show_alert=True)
        return

    # ── All other actions need active stream ──────────────────────────────────
    if chat_id not in playing_chats:
        return await query.answer("⚠️  No active stream found.", show_alert=True)

    data = playing_chats[chat_id]

    try:
        if action == "pause_resume":
            if data["paused"]:
                await call_py.resume_stream(chat_id)
                data["paused"] = False
                pause_dur = int(time.time()) - data.get("pause_start_time", int(time.time()))
                data["start_time"] += pause_dur
                await query.answer("▶️  Resumed")
            else:
                await call_py.pause_stream(chat_id)
                data["paused"] = True
                data["pause_start_time"] = int(time.time())
                await query.answer("⏸  Paused")
            try:
                await query.message.edit_reply_markup(reply_markup=get_player_markup(chat_id))
            except Exception:
                pass

        elif action == "stop":
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
            try:
                await query.message.edit_caption(
                    make_stopped_caption(query.from_user.mention), reply_markup=None)
            except Exception: pass
            await query.answer("Stopped")

        elif action == "skip":
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
                try:
                    await query.message.edit_caption(
                        make_skipped_caption(query.from_user.mention) + "\n  _Queue empty — leaving VC._",
                        reply_markup=None)
                except Exception: pass
                await query.answer("Queue empty")
                return

            process_queue_downloads(chat_id)
            try:
                file_path = await _resolve_file(chat_id, next_song)
            except Exception as e:
                await query.answer(f"❌ {e}", show_alert=True)
                return

            await call_py.play(chat_id, MediaStream(file_path))
            bar     = create_progress_bar(0, next_song["duration"])
            caption = make_now_playing_caption(next_song, bar)
            markup  = get_player_markup(chat_id)

            try:
                player_msg = await client.send_photo(
                    chat_id, photo=next_song["thumbnail"], caption=caption, reply_markup=markup)
            except Exception:
                player_msg = await client.send_message(chat_id, text=caption, reply_markup=markup)

            playing_chats[chat_id] = {
                "message": player_msg, "start_time": int(time.time()),
                "duration": next_song["duration"], "title": next_song["title"],
                "artist": next_song.get("artist", "Unknown"),
                "requester": next_song.get("requester", query.from_user.mention),
                "paused": False, "audio_url": next_song["audio_url"],
                "thumbnail": next_song["thumbnail"], "file_path": file_path,
            }
            updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
            try:
                await query.message.edit_caption(
                    make_skipped_caption(query.from_user.mention), reply_markup=None)
            except Exception: pass
            await query.answer("⏭  Skipped!")

    except Exception as e:
        print(f"[callbacks] Unhandled error: {e}")
        import traceback; traceback.print_exc()
        try: await query.answer(f"Error: {e}", show_alert=True)
        except Exception: pass
