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
from utils.formatters import create_progress_bar, make_now_playing_caption, format_time
from utils.updater import progress_updater


# ── Shared helpers ──────────────────────────────────────────────────────────────

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

    wav = fp.replace(".mp3", ".wav")
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", fp, "-ar", "48000", "-ac", "2", wav, "-y",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode == 0:
            os.remove(fp)
            fp = wav
    except Exception as e:
        print(f"[callbacks] FFmpeg: {e}")
    return fp


# ── Callback router ─────────────────────────────────────────────────────────────
# Separator is "|" to avoid splitting "pause_resume" on "_"

@Client.on_callback_query(filters.regex(r"^(pause_resume|skip|stop|queue_info|back_player)\|"))
async def callbacks(client, query: CallbackQuery):
    action, chat_id_str = query.data.split("|", 1)
    chat_id = int(chat_id_str)

    # ── queue_info / back_player don't require active stream ───────────────────
    if action == "queue_info":
        q   = queued_songs.get(chat_id, [])
        now = playing_chats.get(chat_id)
        lines = ["📋  **Queue Info**\n━━━━━━━━━━━━━━━━━━━━━━"]
        if now:
            lines.append(
                f"▶️  **Now Playing**\n"
                f"    🎼  {now['title']}\n"
                f"    🎤  {now.get('artist','?')}  ·  `{format_time(now['duration'])}`"
            )
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        if q:
            for i, s in enumerate(q, 1):
                icon = "⬇️" if s.get("downloading") else ("✅" if s.get("file_path") else "🕐")
                lines.append(f"`{i}.` {icon}  **{s['title']}**  ·  `{format_time(s.get('duration',0))}`")
        else:
            lines.append("_Queue is empty._")
        lines.append("\n✦  **PAIN !!**  ·  _LᴇᴛMᴇ Sᴏʟᴏ Hᴇʀ_ 🥀")
        try:
            await query.answer()
            await query.message.edit_caption(
                "\n".join(lines),
                reply_markup=get_player_markup(chat_id),
            )
        except Exception:
            pass
        return

    if action == "back_player":
        now = playing_chats.get(chat_id)
        if now:
            played = int(time.time()) - now["start_time"]
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

    # ── All other actions need an active stream ─────────────────────────────────
    if chat_id not in playing_chats:
        return await query.answer("⚠️  No active stream found.", show_alert=True)

    data = playing_chats[chat_id]

    try:
        # ── PAUSE / RESUME ─────────────────────────────────────────────────────
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

        # ── STOP ───────────────────────────────────────────────────────────────
        elif action == "stop":
            clear_queue(chat_id)

            if chat_id in updater_tasks:
                updater_tasks[chat_id].cancel()
                updater_tasks.pop(chat_id, None)

            if chat_id in playing_chats:
                fp = playing_chats[chat_id].get("file_path")
                if fp and os.path.exists(fp):
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
                playing_chats.pop(chat_id, None)

            try:
                await call_py.leave_call(chat_id)
            except Exception:
                pass

            try:
                await query.message.edit_caption(
                    f"⏹  **Stopped** by {query.from_user.mention}\n_Voice chat left._",
                    reply_markup=None,
                )
            except Exception:
                pass
            await query.answer("Stopped")

        # ── SKIP ───────────────────────────────────────────────────────────────
        elif action == "skip":
            if chat_id in updater_tasks:
                updater_tasks[chat_id].cancel()
                updater_tasks.pop(chat_id, None)

            old_fp = playing_chats[chat_id].get("file_path")
            if old_fp and os.path.exists(old_fp):
                try:
                    os.remove(old_fp)
                except Exception:
                    pass

            playing_chats.pop(chat_id, None)

            next_song = get_next(chat_id)
            if not next_song:
                try:
                    await call_py.leave_call(chat_id)
                except Exception:
                    pass
                try:
                    await query.message.edit_caption(
                        f"⏭  **Skipped** by {query.from_user.mention}\n"
                        "_Queue empty — leaving voice chat._",
                        reply_markup=None,
                    )
                except Exception:
                    pass
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
                    chat_id, photo=next_song["thumbnail"], caption=caption, reply_markup=markup
                )
            except Exception as e:
                print(f"[callbacks] send_photo fallback: {e}")
                player_msg = await client.send_message(chat_id, text=caption, reply_markup=markup)

            playing_chats[chat_id] = {
                "message":    player_msg,
                "start_time": int(time.time()),
                "duration":   next_song["duration"],
                "title":      next_song["title"],
                "artist":     next_song.get("artist", "Unknown"),
                "requester":  next_song.get("requester", query.from_user.mention),
                "paused":     False,
                "audio_url":  next_song["audio_url"],
                "thumbnail":  next_song["thumbnail"],
                "file_path":  file_path,
            }
            updater_tasks[chat_id] = asyncio.create_task(
                progress_updater(chat_id, player_msg)
            )

            # Edit the old message to show skip notice
            try:
                await query.message.edit_caption(
                    f"⏭  **Skipped** by {query.from_user.mention}",
                    reply_markup=None,
                )
            except Exception:
                pass
            await query.answer("⏭  Skipped!")

    except Exception as e:
        print(f"[callbacks] Unhandled error: {e}")
        import traceback; traceback.print_exc()
        try:
            await query.answer(f"Error: {e}", show_alert=True)
        except Exception:
            pass
