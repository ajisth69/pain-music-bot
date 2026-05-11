import time
import asyncio
from pyrogram.errors import MessageNotModified
from utils.queue import playing_chats
from utils.formatters import create_progress_bar
from utils.ui import get_player_markup

async def progress_updater(chat_id, message):
    while chat_id in playing_chats:
        try:
            chat_data = playing_chats[chat_id]
            if not chat_data["paused"]:
                current_time = int(time.time())
                played_seconds = current_time - chat_data["start_time"]
                if played_seconds >= chat_data["duration"]:
                    break
                duration_min = f"{chat_data['duration']//60}:{chat_data['duration']%60:02d}"
                bar = create_progress_bar(played_seconds, chat_data["duration"])
                caption = f"""> ▣ 𝐒ᴛᴀʀᴛᴇᴅ 𝐒ᴛʀᴇᴀᴍɪɴɢ 🎵 ❞
>
> ๏ 𝐓ɪᴛʟᴇ : {chat_data['title']} ❞
> ๏ 𝐀ʀᴛɪsᴛ : {chat_data.get('artist', 'Unknown')}
> ๏ 𝐃ᴜʀᴀᴛɪᴏɴ : {duration_min} ᴍɪɴᴜᴛᴇs
> ๏ 𝐑ᴇǫᴜᴇsᴛᴇᴅ 𝐁ʏ : {chat_data.get('requester', '𝐀ᴅᴍɪɴ')} !!
>
> {bar}
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
                await message.edit_caption(
                    caption=caption,
                    reply_markup=get_player_markup(chat_id)
                )
            await asyncio.sleep(10)
        except MessageNotModified:
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Updater Error for {chat_id}: {e}")
            break
