import asyncio
import pyrogram.errors

# Monkey patch missing error for pytgcalls compatibility
if not hasattr(pyrogram.errors, 'GroupcallForbidden'):
    class GroupcallForbidden(Exception): pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pyrogram import idle
from core.clients import bot, userbot
from core.player import call_py
import core.events  # Registers the stream_end handler
from config import LOGGER_ID

async def main():
    print("Initializing Core Systems...")
    await bot.start()
    print("Bot Started!")
    
    await userbot.start()
    print("Userbot Started!")
    
    await call_py.start()
    print("PyTgCalls Started!")
    
    print("PAIN !! Engine is Fully Operational.")
    try:
        await bot.send_message(LOGGER_ID, "🔥 **PAIN !! Engine is Fully Operational.**")
    except Exception as e:
        print(f"Logger Error: {e}")
    await idle()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(main())
