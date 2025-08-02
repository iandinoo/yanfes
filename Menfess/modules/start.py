from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
from Menfess import bot
from Menfess.helper.database import get_user_limit, get_daily_limit

def get_time_until_reset():
    now_utc = datetime.utcnow()
    now_wib = now_utc + timedelta(hours=7)
    tomorrow = (now_wib + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = tomorrow - now_wib
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{hours} jam {minutes} menit"

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    user = message.from_user
    user_id = user.id
    mention = user.mention

    current = get_user_limit(user_id)
    maximum = get_daily_limit()
    reset_in = get_time_until_reset()

    text = (
        f"<b>👤 Profile Kamu:\n\n</b>"
        f"<b>🆔 ID:</b> `{user_id}`\n"
        f"<b>🙋 Nama:</b> {mention}\n"
        f"<b>📨 Menfess Hari Ini:</b> {current}/{maximum}\n"
        f"<b>⏳ Reset Limit:</b> {reset_in} lagi"
    )

    await message.reply(text)

@bot.on_message(filters.command("profile") & filters.private)
async def profile_handler(client: Client, message: Message):
    user = message.from_user
    user_id = user.id
    mention = user.mention

    current = get_user_limit(user_id)
    maximum = get_daily_limit()
    reset_in = get_time_until_reset()

    text = (
        f"<b>👤 Profile Kamu:\n\n</b>"
        f"<b>🆔 ID:</b> `{user_id}`\n"
        f"<b>🙋 Nama:</b> {mention}\n"
        f"<b>📨 Menfess Hari Ini:</b> {current}/{maximum}\n"
        f"<b>⏳ Reset Limit:</b> {reset_in} lagi"
    )

    await message.reply(text)
