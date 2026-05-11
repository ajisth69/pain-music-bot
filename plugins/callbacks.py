import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from core.player import call_py
import os
from utils.queue import playing_chats, updater_tasks, get_next, clear_queue, process_queue_downloads
from utils.jiosaavn import download_file
from utils.ui import get_player_markup
from pytgcalls.types import MediaStream
from utils.formatters import create_progress_bar
from utils.updater import progress_updater
from config import OWNER_USERNAME


@Client.on_callback_query(filters.regex(r"^(pause_resume|skip|stop)_"))
async def callbacks(client, query: CallbackQuery):
    action, chat_id_str = query.data.split("_", 1)
    chat_id = int(chat_id_str)
    
    if chat_id not in playing_chats:
        return await query.answer("⚠️ No active stream found.", show_alert=True)
    
    chat_data = playing_chats[chat_id]
    
    try:
        if action == "pause_resume":
            if chat_data["paused"]:
                await call_py.resume_stream(chat_id)
                chat_data["paused"] = False
                pause_duration = int(time.time()) - chat_data.get("pause_start_time", int(time.time()))
                chat_data["start_time"] += pause_duration
                await query.answer("▶️ Resumed")
            else:
                await call_py.pause_stream(chat_id)
                chat_data["paused"] = True
                chat_data["pause_start_time"] = int(time.time())
                await query.answer("⏸ Paused")
            await query.message.edit_reply_markup(reply_markup=get_player_markup(chat_id))
            
        elif action == "stop":
            clear_queue(chat_id)
            await call_py.leave_call(chat_id)
            
            if chat_id in playing_chats:
                file_path = playing_chats[chat_id].get("file_path")
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting playing file on stop callback: {e}")
                playing_chats.pop(chat_id)
                
            if chat_id in updater_tasks:
                updater_tasks[chat_id].cancel()
            await query.message.edit_caption(f"🛑 **Stream stopped by {query.from_user.mention}**")
            await query.answer("Stopped")
            
        elif action == "skip":
            # Delete current song file
            if chat_id in playing_chats:
                file_path = playing_chats[chat_id].get("file_path")
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting playing file on skip callback: {e}")
                        
            next_song = get_next(chat_id)
            if next_song:
                process_queue_downloads(chat_id)
                
                file_path = next_song.get("file_path")
                if not file_path:
                    file_path = f"downloads/{chat_id}_{int(time.time())}.mp3"
                    os.makedirs("downloads", exist_ok=True)
                    
                    downloaded = await download_file(next_song["audio_url"], file_path)
                    if not downloaded:
                        return await query.answer("❌ Failed to download next song.", show_alert=True)
                        
                    # Try to convert
                    wav_path = file_path.replace(".mp3", ".wav")
                    try:
                        process = await asyncio.create_subprocess_exec(
                            "ffmpeg", "-i", file_path, "-ar", "48000", "-ac", "2", wav_path, "-y",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await process.communicate()
                        if process.returncode == 0:
                            os.remove(file_path)
                            file_path = wav_path
                    except Exception:
                        pass
                        
                await call_py.play(chat_id, MediaStream(file_path))
                
                if chat_id in updater_tasks:
                    updater_tasks[chat_id].cancel()
                
                await query.message.edit_caption(f"⏭ **Skipped by {query.from_user.mention}**")
                
                duration_min = f"{next_song['duration']//60}:{next_song['duration']%60:02d}"
                caption = f"""> ▣ 𝐒ᴛᴀʀᴛᴇᴅ 𝐒ᴛʀᴇᴀᴍɪɴɢ 🎵 ❞
>
> ๏ 𝐓ɪᴛʟᴇ : {next_song['title']} ❞
> ๏ 𝐀ʀᴛɪsᴛ : {next_song.get('artist', 'Unknown')}
> ๏ 𝐃ᴜʀᴀᴛɪᴏɴ : {duration_min} ᴍɪɴᴜᴛᴇs
> ๏ 𝐑ᴇǫᴜᴇsᴛᴇᴅ 𝐁ʏ : {next_song.get('requester', query.from_user.mention)} !!
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
                
                player_msg = await client.send_photo(
                    chat_id,
                    photo=next_song["thumbnail"],
                    caption=caption,
                    reply_markup=get_player_markup(chat_id)
                )
                
                playing_chats[chat_id] = {
                    "message": player_msg,
                    "start_time": int(time.time()),
                    "duration": next_song["duration"],
                    "title": next_song["title"],
                    "artist": next_song.get("artist", "Unknown"),
                    "requester": next_song.get("requester", query.from_user.mention),
                    "paused": False,
                    "audio_url": next_song["audio_url"],
                    "thumbnail": next_song["thumbnail"],
                    "file_path": file_path
                }
                updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
                await query.answer("Skipped")
            else:
                await call_py.leave_call(chat_id)
                playing_chats.pop(chat_id, None)
                if chat_id in updater_tasks:
                    updater_tasks[chat_id].cancel()
                await query.message.edit_caption(f"⏭ **Stream skipped by {query.from_user.mention}**\n*(Queue empty)*")
                await query.answer("Skipped")
            
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)
