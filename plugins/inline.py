import aiohttp
from pyrogram import Client
from pyrogram.types import (
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from config import JIOSAAVN_API_PRIMARY, BOT_USERNAME
from utils.fonts import bold_sans, smallcaps
from utils.formatters import FOOTER


@Client.on_inline_query()
async def inline_search(client: Client, query: InlineQuery):
    text = query.query.strip()
    if not text:
        return await query.answer([
            InlineQueryResultArticle(
                title=f"🔍 {bold_sans('Search Music')}",
                description="Type a song name to search music",
                input_message_content=InputTextMessageContent(
                    f"🔍  {bold_sans('Search Music')}\n"
                    f"Type a song name after @{BOT_USERNAME} to search!"
                )
            )
        ])

    url = f"{JIOSAAVN_API_PRIMARY}{text}"
    results = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    songs = data.get("data", {}).get("results", [])[:10]

                    for song in songs:
                        title = song.get("name", "Unknown")
                        artists = ", ".join(
                            a.get("name", "") for a in song.get("artists", {}).get("primary", [])
                        ) or "Unknown"
                        images = song.get("image", [])
                        thumb = images[-1].get("url") if images else ""

                        btn = InlineKeyboardMarkup([
                            [InlineKeyboardButton(
                                "▶️ 𝗣𝗹𝗮𝘆 𝗶𝗻 𝗩𝗼𝗶𝗰𝗲 𝗖𝗵𝗮𝘁",
                                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                            )],
                            [InlineKeyboardButton(
                                "📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹",
                                url="https://t.me/letmesolo_her"
                            )],
                        ])

                        msg_text = (
                            f"🎧  {bold_sans(title)}\n"
                            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
                            f"  🎤  {artists}\n\n"
                            f"  To play in your Voice Chat:\n"
                            f"  `/play {title}`\n"
                            f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
                            f"{FOOTER}"
                        )

                        results.append(
                            InlineQueryResultArticle(
                                title=f"🎵 {title}",
                                description=f"🎤 {artists}",
                                thumb_url=thumb,
                                input_message_content=InputTextMessageContent(msg_text),
                                reply_markup=btn,
                            )
                        )
    except Exception as e:
        print(f"Inline error: {e}")

    if results:
        await query.answer(results, cache_time=5)
    else:
        await query.answer([
            InlineQueryResultArticle(
                title=f"❌ {bold_sans('No Results Found')}",
                description="Try a different search term",
                input_message_content=InputTextMessageContent(
                    f"❌  {bold_sans('No results found.')}\n_Try a different song name._"
                )
            )
        ])
