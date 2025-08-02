import sys
import asyncio
import importlib

from Menfess import bot
from pyrogram import idle
from Menfess.config import LOGGER
from Menfess.helper.database import add_hashtag, get_all_hashtags, get_expired_messages, remove_from_queue, remove_from_queue

async def auto_delete_task():
    while True:
        expired = get_expired_messages()
        for msg in expired:
            try:
                await bot.delete_messages(msg["chat_id"], msg["message_id"])
            except:
                pass
            finally:
                remove_from_queue(msg["chat_id"], msg["message_id"])
        await asyncio.sleep(60)
        
async def ensure_default_hashtags():
    defaults = ["#boy", "#girl"]
    current = get_all_hashtags()
    for tag in defaults:
        if tag not in current:
            add_hashtag(tag)
            
async def main():
    try:
        await bot.start()
        ex = await bot.get_me()
        LOGGER("INFO").info(f"{ex.first_name} | [ @{ex.username} ] | 🔥 BERHASIL DIAKTIFKAN! 🔥")
        asyncio.create_task(auto_delete_task())
        await ensure_default_hashtags()
        await idle()
    except Exception as a:
        print(a)

if __name__ == "__main__":
    LOGGER("INFO").info("Starting Bot...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
