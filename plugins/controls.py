import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from core.player import call_py
from utils.queue import playing_chats, updater_tasks, get_next, clear_queue
from pytgcalls.types import MediaStream
from utils.formatters import create_progress_bar
from utils.ui import get_player_markup
from utils.updater import progress_updater
from config import OWNER_USERNAME

@Client.on_message(filters.command(["pause"]))
async def pause_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply("⚠️ No active stream found.")
    
    chat_data = playing_chats[chat_id]
    if chat_data["paused"]:
        return await message.reply("⏸ Stream is already paused.")
        
    await call_py.pause_stream(chat_id)
    chat_data["paused"] = True
    chat_data["pause_start_time"] = int(time.time())
    await message.reply(f"> ▣ **𝐏ᴀᴜsᴇᴅ 𝐁ʏ :** {message.from_user.mention} ❞", reply_markup=get_player_markup(chat_id))

@Client.on_message(filters.command(["resume"]))
async def resume_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply("⚠️ No active stream found.")
        
    chat_data = playing_chats[chat_id]
    if not chat_data["paused"]:
        return await message.reply("▶️ Stream is already playing.")
        
    await call_py.resume_stream(chat_id)
    chat_data["paused"] = False
    pause_duration = int(time.time()) - chat_data.get("pause_start_time", int(time.time()))
    chat_data["start_time"] += pause_duration
    await message.reply(f"> ▣ **𝐑ᴇsᴜᴍᴇᴅ 𝐁ʏ :** {message.from_user.mention} ❞", reply_markup=get_player_markup(chat_id))

@Client.on_message(filters.command(["stop", "end"]))
async def stop_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply("⚠️ No active stream found.")
        
    clear_queue(chat_id)
    await call_py.leave_call(chat_id)
    playing_chats.pop(chat_id, None)
    if chat_id in updater_tasks:
        updater_tasks[chat_id].cancel()
    await message.reply(f"> ▣ **𝐒ᴛᴏᴘᴘᴇᴅ 𝐁ʏ :** {message.from_user.mention} ❞")

@Client.on_message(filters.command(["skip", "next"]))
async def skip_cmd(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in playing_chats:
        return await message.reply("⚠️ No active stream found.")
        
    next_song = get_next(chat_id)
    if next_song:
        await call_py.play(chat_id, MediaStream(next_song["audio_url"]))
        if chat_id in updater_tasks:
            updater_tasks[chat_id].cancel()
            
        duration_min = f"{next_song['duration']//60}:{next_song['duration']%60:02d}"
        caption = f"""> ▣ 𝐒ᴛᴀʀᴛᴇᴅ 𝐒ᴛʀᴇᴀᴍɪɴɢ 🎵 ❞
>
> ๏ 𝐓ɪᴛʟᴇ : {next_song['title']} ❞
> ๏ 𝐀ʀᴛɪsᴛ : {next_song.get('artist', 'Unknown')}
> ๏ 𝐃ᴜʀᴀᴛɪᴏɴ : {duration_min} ᴍɪɴᴜᴛᴇs
> ๏ 𝐑ᴇǫᴜᴇsᴛᴇᴅ 𝐁ʏ : {next_song.get('requester', message.from_user.mention)} !!
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
            "requester": next_song.get("requester", message.from_user.mention),
            "paused": False,
            "audio_url": next_song["audio_url"],
            "thumbnail": next_song["thumbnail"]
        }
        updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
        await message.reply(f"> ▣ **𝐒ᴋɪᴘᴘᴇᴅ 𝐁ʏ :** {message.from_user.mention} ❞", reply_markup=get_player_markup(chat_id))
    else:
        await call_py.leave_call(chat_id)
        playing_chats.pop(chat_id, None)
        if chat_id in updater_tasks:
            updater_tasks[chat_id].cancel()
        await message.reply(f"> ▣ **𝐒ᴋɪᴘᴘᴇᴅ 𝐁ʏ :** {message.from_user.mention} ❞\n> ๏ **𝐐ᴜᴇᴜᴇ 𝐄ᴍᴘᴛʏ, 𝐋ᴇᴀᴠɪɴɢ 𝐕𝐂**")
