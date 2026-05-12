import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant
from core.clients import userbot
from core.player import call_py
from utils.jiosaavn import fetch_song, fetch_artist_songs
from utils.queue import (
    queued_songs, playing_chats, updater_tasks, add_to_queue,
    process_queue_downloads, resolve_song_file,
)
from utils.audio import make_audio_stream, should_stream_direct
from utils.formatters import (
    create_progress_bar, make_now_playing_caption, make_queued_caption, format_time,
    GLOW_LINE, THIN_LINE, FOOTER
)
from utils.fonts import bold_sans, bold_italic, smallcaps
from utils.ui import get_player_markup
from utils.updater import progress_updater
from config import OWNER_USERNAME


# ── Shared helpers ──────────────────────────────────────────────────────────────
PLAY_STATUS_SEARCHING = "🔍"
PLAY_STATUS_DOWNLOADING = "📥"
PLAY_STATUS_CONNECTING = "📡"

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


async def _send_player(client_or_msg, chat_id, song, file_path, *, is_message=True):
    """Stream the song and send the now-playing card. Returns player_msg."""
    await call_py.play(chat_id, make_audio_stream(file_path))

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
            f"⚠️  {bold_sans('Usage:')}\n"
            f"  `/play <song name>`\n\n"
            f"  _Example:_ `/play heat waves`"
        )

    query = " ".join(message.command[1:])
    status_msg = await message.reply(PLAY_STATUS_SEARCHING)
    try:
        await message.delete()
    except Exception:
        pass

    song = await fetch_song(query)
    if not song or not song.get("audio_url"):
        return await status_msg.edit(f"❌  {bold_sans('No results found.')}\n  _Try a different name._")

    song["requester"] = message.from_user.mention
    chat_id = message.chat.id

    try:
        await _join_vc(client, chat_id)

        # ── Already playing → queue it ─────────────────────────────────────────
        if chat_id in playing_chats:
            added = add_to_queue(chat_id, song)
            if not added:
                return await status_msg.edit(
                    f"⚠️  {bold_sans('Queue is full!')}\n"
                    f"  Max 20 songs. Use `/skip` or `/stop` to clear space."
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
        if should_stream_direct(song.get("duration")):
            await status_msg.edit(PLAY_STATUS_CONNECTING)
        else:
            await status_msg.edit(PLAY_STATUS_DOWNLOADING)

        file_path = await resolve_song_file(chat_id, song)

        await status_msg.edit(PLAY_STATUS_CONNECTING)
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
        await status_msg.edit(f"❌  {bold_sans('Stream failed:')}\n`{e}`")


# ── /singer ─────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("singer") & filters.group)
async def singer_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            f"⚠️  {bold_sans('Usage:')}\n"
            f"  `/singer <artist name>`\n\n"
            f"  _Example:_ `/singer arijit singh`"
        )

    query      = " ".join(message.command[1:])
    status_msg = await message.reply(f"🔍  {bold_italic('Looking up artist...')}")

    songs = await fetch_artist_songs(query, limit=5)
    if not songs:
        return await status_msg.edit(f"❌  {bold_sans('No songs found')} for that artist.")

    chat_id = message.chat.id

    try:
        await _join_vc(client, chat_id)
        await status_msg.edit(
            f"🎤  {bold_sans(f'Found top {len(songs)} tracks')} for **{query.title()}**\n"
            f"  ⬇️  _{bold_italic('Queuing them up...')}_"
        )

        for i, song in enumerate(songs):
            song["requester"] = message.from_user.mention

            if chat_id in playing_chats or i > 0:
                add_to_queue(chat_id, song)
            else:
                file_path = await resolve_song_file(chat_id, song)
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
        q_count = len(queued_songs.get(chat_id, []))
        await status_msg.edit(
            f"✅  {bold_sans(f'{len(songs)} tracks')} added for **{query.title()}**!\n"
            f"  📋  Queue: `{q_count}` song{'s' if q_count != 1 else ''} ahead."
        )

    except Exception as e:
        await status_msg.edit(f"❌  {bold_sans('Failed:')}\n`{e}`")
