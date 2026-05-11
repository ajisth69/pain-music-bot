import time
import asyncio
import os
from core.player import call_py
from pytgcalls.types import MediaStream, Update, StreamEnded
from utils.queue import playing_chats, updater_tasks, get_next, clear_queue
from utils.formatters import create_progress_bar
from utils.ui import get_player_markup
from utils.updater import progress_updater
from utils.jiosaavn import download_file

@call_py.on_update()
async def stream_ended(client, update: Update):
    if not isinstance(update, StreamEnded):
        return
    chat_id = update.chat_id
    
    if chat_id in playing_chats:
        old_msg = playing_chats[chat_id]["message"]
        file_path = playing_chats[chat_id].get("file_path")
        try:
            await old_msg.edit_caption("✅ **Song finished.**", reply_markup=None)
        except:
            pass
            
        # Delete the file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file: {e}")
            
    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
        
    playing_chats.pop(chat_id, None)
    
    # Check queue for the next song
    next_song = get_next(chat_id)
    if next_song:
        try:
            file_path = f"downloads/{chat_id}_{int(time.time())}.mp3"
            os.makedirs("downloads", exist_ok=True)
            downloaded = await download_file(next_song["audio_url"], file_path)
            if not downloaded:
                raise Exception("Failed to download song")
                
            wav_path = file_path.replace(".mp3", ".wav")
            try:
                import asyncio
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
            
            bar = create_progress_bar(0, next_song["duration"])
            caption = f"🎵 **Playing:** {next_song['title']}\n\n{bar}"
            
            try:
                player_msg = await bot.send_photo(
                    chat_id,
                    photo=next_song["thumbnail"],
                    caption=caption,
                    reply_markup=get_player_markup(chat_id)
                )
            except Exception as e:
                print(f"Failed to send photo in queue, sending text: {e}")
                player_msg = await bot.send_message(
                    chat_id,
                    text=caption,
                    reply_markup=get_player_markup(chat_id)
                )
            
            playing_chats[chat_id] = {
                "message": player_msg,
                "start_time": int(time.time()),
                "duration": next_song["duration"],
                "title": next_song["title"],
                "paused": False,
                "audio_url": next_song["audio_url"],
                "thumbnail": next_song["thumbnail"],
                "file_path": file_path
            }
            updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
        except Exception as e:
            print(f"Queue play error: {e}")
            clear_queue(chat_id)
            await call_py.leave_call(chat_id)
    else:
        await call_py.leave_call(chat_id)
