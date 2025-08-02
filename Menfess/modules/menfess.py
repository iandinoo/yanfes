from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.filters import command
from Menfess.helper.database import (
    increment_user_limit,
    get_target_channel,
    get_banned_words,
    get_all_hashtags,
    get_daily_limit,
    get_bonus_limit,
    queue_deletion,
    get_user_limit
)

from Menfess import bot
from datetime import datetime, timedelta

def detect_hashtag(text):
    if not text:
        return None
    text = text.lower()
    for tag in get_all_hashtags():
        if tag in text:
            return tag
    return None

def contains_banned_word(text: str) -> bool:
    text = text.lower()
    for word in get_banned_words():
        if word in text:
            return True
    return False
    
excluded_commands = ["start", "profile"]

@bot.on_message(
    filters.private &
    ~filters.command(excluded_commands) & 
    (filters.text | filters.photo)
)
async def menfess_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    count = get_user_limit(user_id)
    limit = get_daily_limit()
    bonus = get_bonus_limit(user_id)

    total_limit = limit + bonus
    
    if count >= total_limit:
        return await message.reply(f"⚠️ Kamu sudah mencapai batas menfess hari ini ({total_limit}/hari). Coba lagi besok.")
    
    if message.text:
        hashtag = detect_hashtag(message.text)
    elif message.caption:
        hashtag = detect_hashtag(message.caption)
    else:
        return await message.reply("❌ Harap sertakan hashtag #girl atau #boy di pesan kamu.")

    if not hashtag:
        return await message.reply("❌ Harap sertakan hashtag #girl atau #boy di pesan kamu.")
        
    target_channel = get_target_channel()
    if not target_channel:
        return await message.reply("❌ Channel tujuan belum diatur. Gunakan /setchannel dengan membalas pesan dari channel.")

    if message.text:
        content = message.text
    elif message.caption:
        content = message.caption
    else:
        content = ""
    
    if contains_banned_word(content):
        return await message.reply("<b>❌ Pesan kamu mengandung kata yang tidak diperbolehkan.</b>")
    
    try:
        if message.text:
            send = await client.send_message(
                chat_id=target_channel,
                text=message.text
            )
        elif message.photo:
            send = await client.send_photo(
                chat_id=target_channel,
                photo=message.photo.file_id,
                caption=message.caption or ""
            )

        username = (await bot.get_chat(target_channel)).username
        
        message_link = f"t.me/{username}/{send.id}"
        
        count = get_user_limit(user_id)
        limit = get_daily_limit() + get_bonus_limit(user_id)

        increment_user_limit(user_id)

        count = count + 1

        delete_time = datetime.utcnow() + timedelta(hours=1)
        queue_deletion(send.chat.id, send.id, delete_time)

        await message.reply(
            f"[Pesan anda berhasil terkirim.]({message_link})\n\n"
            f"Hari ini kamu telah mengirim pesan sebanyak {count}/{limit}.\n"
            f"Kamu dapat mengirim hingga {limit} pesan setiap harinya.\n\n"
            f"Waktu reset: setiap jam 00:00 pagi (WIB)."
        )
    except Exception as e:
        await message.reply(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")
