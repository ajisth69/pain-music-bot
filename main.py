import asyncio
import pyrogram.errors
from aiohttp import web
import os

# Monkey patch missing error for pytgcalls compatibility
if not hasattr(pyrogram.errors, 'GroupcallForbidden'):
    class GroupcallForbidden(Exception): pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

from pyrogram import idle
from core.clients import bot, userbot
from core.player import call_py
import core.events  # Registers the stream_end handler
from config import LOGGER_ID

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()
    print("Web server started!")

async def main():
    try:
        print("Initializing Core Systems...")
        await start_web_server()
        
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
    except Exception as e:
        print(f"CRITICAL ERROR AT STARTUP: {e}")
        import traceback
        traceback.print_exc()
        raise e

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(main())
