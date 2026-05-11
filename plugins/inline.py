import aiohttp
from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from config import JIOSAAVN_API_PRIMARY, BOT_USERNAME

@Client.on_inline_query()
async def inline_search(client: Client, query: InlineQuery):
    text = query.query.strip()
    if not text:
        return await query.answer([
            InlineQueryResultArticle(
                title="🔍 Search Music...",
                description="Type a song name to search on JioSaavn.",
                input_message_content=InputTextMessageContent("Please enter a song name to search.")
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
                        images = song.get("image", [])
                        thumb = images[-1].get("url") if images else ""
                        
                        btn = InlineKeyboardMarkup([[
                            InlineKeyboardButton("▶️ 𝖯𝗅𝖺𝗒 𝖲𝗈𝗇𝗀 𝗂𝗇 𝖵𝖢", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
                        ]])
                        
                        results.append(
                            InlineQueryResultArticle(
                                title=title,
                                description="Tap to share & play this song!",
                                thumb_url=thumb,
                                input_message_content=InputTextMessageContent(
                                    f"🎧 **{title}**\n\nTo play this song in your Voice Chat, add me and type:\n`/play {title}`"
                                ),
                                reply_markup=btn
                            )
                        )
    except Exception as e:
        print(f"Inline error: {e}")
        
    if results:
        await query.answer(results, cache_time=5)
    else:
        await query.answer([
            InlineQueryResultArticle(
                title="❌ No Results Found",
                input_message_content=InputTextMessageContent("Could not find that song.")
            )
        ])
