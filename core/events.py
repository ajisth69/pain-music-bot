import time
import asyncio
from core.player import call_py
from pytgcalls.types import MediaStream, Update, StreamEnded
from utils.queue import playing_chats, updater_tasks, get_next, clear_queue
from utils.formatters import create_progress_bar
from utils.ui import get_player_markup
from utils.updater import progress_updater

@call_py.on_update()
async def stream_ended(client, update: Update):
    if not isinstance(update, StreamEnded):
        return
    chat_id = update.chat_id
    
    if chat_id in playing_chats:
        old_msg = playing_chats[chat_id]["message"]
        try:
            await old_msg.edit_caption("✅ **Song finished.**", reply_markup=None)
        except:
            pass
            
    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
        
    playing_chats.pop(chat_id, None)
    
    # Check queue for the next song
    next_song = get_next(chat_id)
    if next_song:
        try:
            await call_py.play(chat_id, MediaStream(next_song["audio_url"]))
            
            bar = create_progress_bar(0, next_song["duration"])
            caption = f"🎵 **Playing:** {next_song['title']}\n\n{bar}"
            
            from core.clients import bot
            player_msg = await bot.send_photo(
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
                "paused": False,
                "audio_url": next_song["audio_url"],
                "thumbnail": next_song["thumbnail"]
            }
            updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
        except Exception as e:
            print(f"Queue play error: {e}")
            clear_queue(chat_id)
            await call_py.leave_call(chat_id)
    else:
        await call_py.leave_call(chat_id)
