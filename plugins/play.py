import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant
from core.clients import userbot
from core.player import call_py
from pytgcalls.types import MediaStream
from utils.jiosaavn import fetch_song, fetch_artist_songs
from utils.queue import queued_songs, playing_chats, updater_tasks, add_to_queue
from utils.formatters import create_progress_bar
from utils.ui import get_player_markup
from utils.updater import progress_updater
from config import OWNER_USERNAME


@Client.on_message(filters.command("play") & filters.group)
async def play_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Provide a song name. Example: `/play heat waves`")
    
    query = " ".join(message.command[1:])
    status_msg = await message.reply("🔍")
    
    song = await fetch_song(query)
    if not song or not song["audio_url"]:
        return await status_msg.edit("❌")
        
    song["requester"] = message.from_user.mention
    
    chat_id = message.chat.id
    
    try:
        try:
            await userbot.get_chat(chat_id)
        except Exception:
            try:
                chat = await client.get_chat(chat_id)
                if chat.invite_link:
                    await userbot.join_chat(chat.invite_link)
                else:
                    invite = await chat.export_invite_link()
                    await userbot.join_chat(invite)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await status_msg.edit(f"❌")

        if chat_id in playing_chats:
            add_to_queue(chat_id, song)
            position = len(queued_songs[chat_id])
            duration_min = f"{song['duration']//60}:{song['duration']%60:02d}"
            await status_msg.delete()
            return await message.reply_photo(
                photo=song["thumbnail"],
                caption=f"""> ▣ 𝐀ᴅᴅᴇᴅ 𝐓ᴏ 𝐐ᴜᴇᴜᴇ 𝐀ᴛ #{position} ❞
>
> ๏ 𝐓ɪᴛʟᴇ : {song['title']} ❞
> ๏ 𝐀ʀᴛɪsᴛ : {song.get('artist', 'Unknown')}
> ๏ 𝐃ᴜʀᴀᴛɪᴏɴ : {duration_min} ᴍɪɴᴜᴛᴇs
> ๏ 𝐑ᴇǫᴜᴇsᴛᴇᴅ 𝐁ʏ : {song['requester']} !!
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞""",
                reply_markup=get_player_markup(chat_id)
            )

        await call_py.play(chat_id, MediaStream(song["audio_url"]))
        
        duration_min = f"{song['duration']//60}:{song['duration']%60:02d}"
        caption = f"""> ▣ 𝐒ᴛᴀʀᴛᴇᴅ 𝐒ᴛʀᴇᴀᴍɪɴɢ 🎵 ❞
>
> ๏ 𝐓ɪᴛʟᴇ : {song['title']} ❞
> ๏ 𝐀ʀᴛɪsᴛ : {song.get('artist', 'Unknown')}
> ๏ 𝐃ᴜʀᴀᴛɪᴏɴ : {duration_min} ᴍɪɴᴜᴛᴇs
> ๏ 𝐑ᴇǫᴜᴇsᴛᴇᴅ 𝐁ʏ : {song['requester']} !!
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
        
        await status_msg.delete()
        player_msg = await message.reply_photo(
            photo=song["thumbnail"],
            caption=caption,
            reply_markup=get_player_markup(chat_id)
        )
        
        if chat_id in updater_tasks:
            updater_tasks[chat_id].cancel()
            
        playing_chats[chat_id] = {
            "message": player_msg,
            "start_time": int(time.time()),
            "duration": song["duration"],
            "title": song["title"],
            "artist": song.get("artist", "Unknown"),
            "requester": song["requester"],
            "paused": False,
            "audio_url": song["audio_url"],
            "thumbnail": song["thumbnail"]
        }
        
        updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
        
    except Exception as e:
        await status_msg.edit(f"❌ **Failed to stream:**\n`{str(e)}`")

@Client.on_message(filters.command("singer") & filters.group)
async def singer_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Provide a singer name. Example: `/singer arijit singh`")
        
    query = " ".join(message.command[1:])
    status_msg = await message.reply("🔍")
    
    songs = await fetch_artist_songs(query, limit=5)
    if not songs:
        return await status_msg.edit("❌ **Error:** No songs found for this singer.")
        
    chat_id = message.chat.id
    
    try:
        try:
            await userbot.get_chat(chat_id)
        except Exception:
            try:
                chat = await client.get_chat(chat_id)
                if chat.invite_link:
                    await userbot.join_chat(chat.invite_link)
                else:
                    invite = await chat.export_invite_link()
                    await userbot.join_chat(invite)
            except Exception:
                return await status_msg.edit(f"❌")

        await status_msg.edit(f"✅ **Found Top {len(songs)} songs for {query.title()}! Adding to loop...**")
        
        for i, song in enumerate(songs):
            song["requester"] = message.from_user.mention
            if chat_id in playing_chats or i > 0:
                add_to_queue(chat_id, song)
            else:
                await call_py.play(chat_id, MediaStream(song["audio_url"]))
                
                duration_min = f"{song['duration']//60}:{song['duration']%60:02d}"
                caption = f"""> ▣ 𝐒ᴛᴀʀᴛᴇᴅ 𝐒ᴛʀᴇᴀᴍɪɴɢ 🎵 ❞
>
> ๏ 𝐓ɪᴛʟᴇ : {song['title']} ❞
> ๏ 𝐀ʀᴛɪsᴛ : {song.get('artist', 'Unknown')}
> ๏ 𝐃ᴜʀᴀᴛɪᴏɴ : {duration_min} ᴍɪɴᴜᴛᴇs
> ๏ 𝐑ᴇǫᴜᴇsᴛᴇᴅ 𝐁ʏ : {song['requester']} !!
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
                
                player_msg = await message.reply_photo(
                    photo=song["thumbnail"],
                    caption=caption,
                    reply_markup=get_player_markup(chat_id)
                )
                
                if chat_id in updater_tasks:
                    updater_tasks[chat_id].cancel()
                    
                playing_chats[chat_id] = {
                    "message": player_msg,
                    "start_time": int(time.time()),
                    "duration": song["duration"],
                    "title": song["title"],
                    "artist": song.get("artist", "Unknown"),
                    "requester": song["requester"],
                    "paused": False,
                    "audio_url": song["audio_url"],
                    "thumbnail": song["thumbnail"]
                }
                
                updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))
                
        await asyncio.sleep(2)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit(f"❌ **Failed to start loop:**\n`{str(e)}`")
