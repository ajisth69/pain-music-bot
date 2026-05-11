import time
import asyncio
from pyrogram.errors import MessageNotModified, FloodWait
from utils.queue import playing_chats, updater_tasks
from utils.formatters import create_progress_bar, make_now_playing_caption
from utils.ui import get_player_markup


async def progress_updater(chat_id, message):
    """Periodically edits the now-playing message with a live progress bar."""
    try:
        while True:
            if chat_id not in playing_chats:
                break

            chat_data = playing_chats[chat_id]

            # Stop if the active message changed (song was skipped)
            if chat_data.get("message") is not message:
                break

            if not chat_data["paused"]:
                current_time = int(time.time())
                played_seconds = current_time - chat_data["start_time"]
                duration = chat_data["duration"]
                played_seconds = max(0, min(played_seconds, duration))

                bar = create_progress_bar(played_seconds, duration)
                caption = make_now_playing_caption(chat_data, bar)

                try:
                    await message.edit_caption(
                        caption=caption,
                        reply_markup=get_player_markup(chat_id),
                    )
                except MessageNotModified:
                    pass
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    print(f"[updater] Edit failed for {chat_id}: {e}")
                    break

            await asyncio.sleep(10)

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[updater] Unexpected error for {chat_id}: {e}")
    finally:
        if updater_tasks.get(chat_id) is asyncio.current_task():
            updater_tasks.pop(chat_id, None)
