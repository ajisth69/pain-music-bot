import time
import sys
import os
import pytgcalls
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import IMG_START, IMG_HELP, IMG_PING, IMG_RELOAD, BOT_USERNAME, OWNER_USERNAME, OWNER_ID

@Client.on_message(filters.command(["start"]))
async def start_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("✧ ᴅᴇᴠᴇʟᴏᴘᴇʀ ✧", url=f"https://t.me/{OWNER_USERNAME}"), InlineKeyboardButton("✧ ʜᴏᴍᴇ ✧", url=f"https://t.me/{OWNER_USERNAME}")]
    ])
    text = f"""> ▣ **𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐏𝐀𝐈𝐍 !!** 🎵 ❞
>
> ๏ **𝐇ᴇʏ :** {message.from_user.mention} ❞
> ๏ **𝐀ʙᴏᴜᴛ :** 𝐀 𝐍ᴇxᴛ-𝐆ᴇɴ 𝐌ᴜsɪᴄ 𝐁ᴏᴛ !!
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
    await message.reply_photo(IMG_START, caption=text, reply_markup=buttons)

@Client.on_message(filters.command(["help"]))
async def help_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✧ ᴏᴡɴᴇʀ ✧", url=f"https://t.me/{OWNER_USERNAME}")]
    ])
    text = f"""> ▣ **𝐏𝐀𝐈𝐍 !! 𝐇ᴇʟᴘ 𝐌ᴇɴᴜ** 🛠 ❞
>
> ๏ /play - 𝐒ᴛʀᴇᴀᴍ 𝐌ᴜsɪᴄ
> ๏ /singer - 𝐀ʀᴛɪsᴛ 𝐋ᴏᴏᴘ
> ๏ /skip - 𝐒ᴋɪᴘ 𝐓ʀᴀᴄᴋ
> ๏ /stop - 𝐒ᴛᴏᴘ 𝐒ᴛʀᴇᴀᴍ
> ๏ /ping - 𝐒ʏsᴛᴇᴍ 𝐒ᴛᴀᴛs
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)

@Client.on_message(filters.command(["owner"]))
async def owner_cmd(client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✧ ꜱᴜᴘᴘᴏʀᴛ ✧", url=f"https://t.me/{OWNER_USERNAME}"),
            InlineKeyboardButton("✧ ʙᴜɢꜱ ✧", url=f"https://t.me/{OWNER_USERNAME}")
        ],
        [InlineKeyboardButton("✧ ʟᴇᴛᴍᴇꜱᴏʟᴏ_ʜᴇʀ ✧", url="https://t.me/letmesolo_her")]
    ])
    text = f"""> ▣ **𝐎ᴡɴᴇʀ 𝐈ɴꜰᴏ** 👑 ❞
>
> ๏ **𝐒ᴜᴘᴘᴏʀᴛ :** 𝐂ᴏɴᴛᴀᴄᴛ @{OWNER_USERNAME} !!
> ๏ **𝐁ᴜɢ𝐬 :** 𝐑ᴇᴘᴏʀᴛ 𝐓ᴏ @{OWNER_USERNAME} !!
> ๏ **𝐋ᴇᴛ𝐌ᴇ𝐒ᴏʟᴏ𝐇ᴇʀ :** 𝐓ʜᴇ 𝐋ᴇɢᴇɴᴅ ❞
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
    await message.reply_photo(IMG_HELP, caption=text, reply_markup=buttons)

@Client.on_message(filters.command(["ping"]))
async def ping_cmd(client, message: Message):
    start = time.time()
    msg = await message.reply_photo(IMG_PING, caption="⚡️ Pinging Core Modules...")
    end = time.time()
    latency = (end - start) * 1000
    
    text = f"""> ▣ **𝐒ʏsᴛᴇᴍ 𝐒ᴛᴀᴛs** 🏓 ❞
>
> ๏ **𝐇ᴏsᴛ 𝐋ᴀᴛᴇɴᴄʏ :** {latency:.2f} ᴍs ❞
> ๏ **𝐀ᴘɪ 𝐍ᴏᴅᴇ :** 𝐂ᴏɴɴᴇᴄᴛᴇᴅ ✅
> ๏ **𝐏ʏ𝐓ɢ𝐂ᴀʟʟs :** ᴠ{pytgcalls.__version__} 🟢
>
> ❖ ᴘᴏᴡᴇʀᴇᴅ» | 𝐋ᴇᴛ𝐌ᴇ 𝐒ᴏʟᴏ 𝐇ᴇʀ🥀 | ❞"""
    await msg.edit_caption(text)

@Client.on_message(filters.command(["reload", "restart"]))
async def reload_cmd(client, message: Message):
    if not message.from_user or message.from_user.id != OWNER_ID:
        return await message.reply(f"🚫 **Nice try! Only @{OWNER_USERNAME} can use this command.**")
    
    await message.reply_photo(IMG_RELOAD, caption="🔄 **Reloading modules and rebooting the engine...**\n*(This takes ~3 seconds)*")
    
    # Restarts the script safely across Windows and Linux
    import subprocess
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)
