import time
import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant
from core.clients import userbot
from core.player import call_py
from pytgcalls.types import MediaStream
from utils.jiosaavn import fetch_song, fetch_artist_songs, download_file
from utils.queue import queued_songs, playing_chats, updater_tasks, add_to_queue, process_queue_downloads
from utils.formatters import create_progress_bar, make_now_playing_caption, make_queued_caption, format_time
from utils.ui import get_player_markup
from utils.updater import progress_updater
from config import OWNER_USERNAME


# ── Shared helpers ──────────────────────────────────────────────────────────────

async def _join_vc(client, chat_id):
    """Ensure userbot is in the group."""
    try:
        await userbot.get_chat(chat_id)
    except Exception:
        try:
            chat = await client.get_chat(chat_id)
            link = chat.invite_link or await client.export_chat_invite_link(chat_id)
            await userbot.join_chat(link)
        except UserAlreadyParticipant:
            pass


async def _convert_to_wav(mp3_path: str) -> str:
    """Convert mp3 → wav (48 kHz stereo). Returns final usable path."""
    wav_path = mp3_path.replace(".mp3", ".wav")
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", mp3_path, "-ar", "48000", "-ac", "2", wav_path, "-y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode == 0:
            os.remove(mp3_path)
            return wav_path
    except Exception as e:
        print(f"[play] FFmpeg failed: {e}")
    return mp3_path


async def _send_player(client_or_msg, chat_id, song, file_path, *, is_message=True):
    """Stream the song and send the now-playing card. Returns player_msg."""
    await call_py.play(chat_id, MediaStream(file_path))

    bar = create_progress_bar(0, song["duration"])
    caption = make_now_playing_caption(song, bar)
    markup = get_player_markup(chat_id)

    try:
        if is_message:
            player_msg = await client_or_msg.reply_photo(
                photo=song["thumbnail"], caption=caption, reply_markup=markup
            )
        else:
            player_msg = await client_or_msg.send_photo(
                chat_id, photo=song["thumbnail"], caption=caption, reply_markup=markup
            )
    except Exception as e:
        print(f"[play] send_photo failed, falling back to text: {e}")
        if is_message:
            player_msg = await client_or_msg.reply_text(text=caption, reply_markup=markup)
        else:
            player_msg = await client_or_msg.send_message(chat_id, text=caption, reply_markup=markup)

    return player_msg


# ── /play ───────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("play") & filters.group)
async def play_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "**⚠️  Usage:** `/play <song name>`\n"
            "_Example:_ `/play heat waves`"
        )

    query = " ".join(message.command[1:])
    status_msg = await message.reply("🔍  **Searching JioSaavn…**")
    try:
        await message.delete()
    except Exception:
        pass

    song = await fetch_song(query)
    if not song or not song.get("audio_url"):
        return await status_msg.edit("❌  **No results found.** Try a different name.")

    song["requester"] = message.from_user.mention
    chat_id = message.chat.id

    try:
        await _join_vc(client, chat_id)

        # ── Already playing → queue it ─────────────────────────────────────────
        if chat_id in playing_chats:
            added = add_to_queue(chat_id, song)
            if not added:
                return await status_msg.edit(
                    "⚠️  **Queue is full!**\n"
                    "Max 20 songs. Use /skip or /stop to clear space."
                )
            process_queue_downloads(chat_id)
            position = len(queued_songs[chat_id])
            caption  = make_queued_caption(song, position)
            await status_msg.delete()
            return await message.reply_photo(
                photo=song["thumbnail"],
                caption=caption,
                reply_markup=get_player_markup(chat_id),
            )

        # ── Nothing playing → start now ────────────────────────────────────────
        await status_msg.edit("⬇️  **Downloading…**")
        file_path = f"downloads/{chat_id}_{int(time.time())}.mp3"
        os.makedirs("downloads", exist_ok=True)

        if not await download_file(song["audio_url"], file_path):
            return await status_msg.edit("❌  **Download failed.** Try again.")

        await status_msg.edit("🔄  **Converting audio…**")
        file_path = await _convert_to_wav(file_path)

        await status_msg.edit("📡  **Connecting to Voice Chat…**")
        player_msg = await _send_player(message, chat_id, song, file_path, is_message=True)
        await status_msg.delete()

        if chat_id in updater_tasks:
            updater_tasks[chat_id].cancel()

        playing_chats[chat_id] = {
            "message":    player_msg,
            "start_time": int(time.time()),
            "duration":   song["duration"],
            "title":      song["title"],
            "artist":     song.get("artist", "Unknown"),
            "requester":  song["requester"],
            "paused":     False,
            "audio_url":  song["audio_url"],
            "thumbnail":  song["thumbnail"],
            "file_path":  file_path,
        }
        updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))

    except Exception as e:
        await status_msg.edit(f"❌  **Stream failed:**\n`{e}`")


# ── /singer ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("singer") & filters.group)
async def singer_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "**⚠️  Usage:** `/singer <artist name>`\n"
            "_Example:_ `/singer arijit singh`"
        )

    query      = " ".join(message.command[1:])
    status_msg = await message.reply("🔍  **Looking up artist on JioSaavn…**")

    songs = await fetch_artist_songs(query, limit=5)
    if not songs:
        return await status_msg.edit("❌  **No songs found** for that artist.")

    chat_id = message.chat.id

    try:
        await _join_vc(client, chat_id)
        await status_msg.edit(
            f"🎤  **Found top {len(songs)} tracks** for **{query.title()}**\n"
            f"⬇️  _Queuing them up…_"
        )

        for i, song in enumerate(songs):
            song["requester"] = message.from_user.mention

            if chat_id in playing_chats or i > 0:
                add_to_queue(chat_id, song)
            else:
                file_path = f"downloads/{chat_id}_{int(time.time())}.mp3"
                os.makedirs("downloads", exist_ok=True)
                if not await download_file(song["audio_url"], file_path):
                    continue

                file_path  = await _convert_to_wav(file_path)
                player_msg = await _send_player(message, chat_id, song, file_path, is_message=True)

                if chat_id in updater_tasks:
                    updater_tasks[chat_id].cancel()

                playing_chats[chat_id] = {
                    "message":    player_msg,
                    "start_time": int(time.time()),
                    "duration":   song["duration"],
                    "title":      song["title"],
                    "artist":     song.get("artist", "Unknown"),
                    "requester":  song["requester"],
                    "paused":     False,
                    "audio_url":  song["audio_url"],
                    "thumbnail":  song["thumbnail"],
                    "file_path":  file_path,
                }
                updater_tasks[chat_id] = asyncio.create_task(progress_updater(chat_id, player_msg))

        process_queue_downloads(chat_id)
        await asyncio.sleep(2)
        await status_msg.edit(
            f"✅  **{len(songs)} tracks** added for **{query.title()}**!\n"
            f"📋  Queue: `{len(queued_songs.get(chat_id, []))}` song(s) ahead."
        )

    except Exception as e:
        await status_msg.edit(f"❌  **Failed:**\n`{e}`")
