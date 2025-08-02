from pyrogram.types import Message
from pyrogram import Client, filters
from Menfess.helper.database import (
    get_target_channel,
    set_target_channel,
    remove_banned_word,
    get_banned_words,
    get_all_hashtags,
    reset_user_count,
    set_daily_limit,
    add_banned_word,
    add_user_limit,
    remove_hashtag,
    add_hashtag,
)

import asyncio
from Menfess import bot
from Menfess.config import OWNER_ID
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, WebAppInfo

C30 = """
<b>⚙️ Settings</b>

<b>• ꜱᴇᴛ_ᴄʜᴀɴɴᴇʟ</b>
Untuk Mengatur Channel Menfess Anda!

<b>• ꜱᴇᴛ_ʟɪᴍɪᴛ</b>
Untuk Mengatur Jumlah Limit - Default Nya 3!

<b>• ᴀᴅᴅ_ʟɪᴍɪᴛ</b>
Untuk Menambahkan Jumlah Limit Member Anda!

<b>• ᴅᴇʟ_ʟɪᴍɪᴛ</b>
Untuk Mengubah Limit Member Menjadi 0!

<b>• ʟɪꜱᴛ_ʙᴀɴ</b>
List Kata Terlarang Yang Tidak Dapat Dikirim Dimenfess! (Sudah Ada Tombol Add&Del)

<b>• ʟɪꜱᴛ_ᴛᴀɢ</b>
List Tag Yang Sudah Ditambahkan, Default Boy Atau Girl! (Sudah Ada Tombol Add&Del)
"""

@Client.on_message(filters.command("menu") & filters.private & filters.user(OWNER_ID))
async def menu(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ꜱᴇᴛ_ᴄʜᴀɴɴᴇʟ", callback_data="view_channel"),
            InlineKeyboardButton("ꜱᴇᴛ_ʟɪᴍɪᴛ", callback_data="set_limit"),
        ],
        [
            InlineKeyboardButton("ᴀᴅᴅ_ʟɪᴍɪᴛ", callback_data="add_limit"),
            InlineKeyboardButton("ᴅᴇʟ_ʟɪᴍɪᴛ", callback_data="del_limit"),
        ],
        [
            InlineKeyboardButton("ʟɪꜱᴛ_ʙᴀɴ", callback_data="listban"),
            InlineKeyboardButton("ʟɪꜱᴛ_ᴛᴀɢ", callback_data="listtag"),
        ],
    ])
    await message.delete()
    await message.reply_text(C30, reply_markup=keyboard)
    
@bot.on_callback_query(filters.regex("menu_callback"))
async def menu_callback(client: Client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ꜱᴇᴛ_ᴄʜᴀɴɴᴇʟ", callback_data="view_channel"),
            InlineKeyboardButton("ꜱᴇᴛ_ʟɪᴍɪᴛ", callback_data="set_limit"),
        ],
        [
            InlineKeyboardButton("ᴀᴅᴅ_ʟɪᴍɪᴛ", callback_data="add_limit"),
            InlineKeyboardButton("ᴅᴇʟ_ʟɪᴍɪᴛ", callback_data="del_limit"),
        ],
        [
            InlineKeyboardButton("ʟɪꜱᴛ_ʙᴀɴ", callback_data="listban"),
            InlineKeyboardButton("ʟɪꜱᴛ_ᴛᴀɢ", callback_data="listtag"),
        ],
    ])
    await callback_query.edit_message_text(C30, reply_markup=keyboard)

#// CHANNEL ADD MENFESS DATABASE

@bot.on_callback_query(filters.regex("view_channel"))
async def view_channel(client: Client, callback_query):
    try:
        target_channel = get_target_channel()

        chat = await client.get_chat(target_channel)
        
        delete_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👀 View Channel", url=f"t.me/{chat.username}")],
            [InlineKeyboardButton("✏️ Edit Channel", callback_data="add_channel")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
        ])

        start_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Tambahkan Channel", callback_data="add_channel")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
        ])

        if target_channel is not None:

            await callback_query.edit_message_text(
                f"<b>💬 Informasi Channel</b>\n"
                f"> `{chat.id}`\n\n"
                f"<b>👤 Nama:</b> {chat.title}\n"
                f"<b>🔔 Username:</b> @{chat.username}",
                reply_markup=delete_keyboard
            )
        else:
            await callback_query.edit_message_text(
                "<b>❌ Anda Belum Memasang Channel Menfess - Silahkan Pasang Terlebih Dahulu!</b>",
                reply_markup=start_keyboard
            )
    except Exception as e:
        return await callback_query.edit_message_text(
            f"<b>Terjadi kesalahan:</b> `{str(e)}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )

@bot.on_callback_query(filters.regex("add_channel"))
async def add_channel(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Bot: Silakan masukkan chat_id atau @username channel Anda.\n\n/cancel - Untuk membatalkan!"
    )

    while True:
        try:
            response = await bot.listen(user_id, filters.text)
            text = response.text.strip()

            if text.startswith("/"):
                await response.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan!</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            chat_input = text if text.startswith("@") else int(text)

            try:
                chat = await bot.get_chat(chat_input)
            except Exception as e:
                await response.delete()
                notif = await callback_query.message.reply(f"<b>❌ Gagal mengambil chat:</b> `Pastikan Bot Anda Adalah Admin.`")
                await asyncio.sleep(2)
                await notif.delete()
                continue

            await response.delete()
            set_target_channel(chat.id)

            return await msg.edit(
                f"<b>✅ Channel berhasil disimpan!</b>\n\n<b>👤 Nama:</b> {chat.title}\n<b>🆔 chat_id:</b> `{chat.id}`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="view_channel")]
                ])
            )

        except Exception as e:
            await response.delete()
            return await msg.edit(
                f"<b>❌ Gagal menyimpan channel:</b> `Pastikan Bot Anda Adalah Admin.`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )
            
@bot.on_callback_query(filters.regex("set_limit"))
async def set_limit(client: Client, callback_query):
    user_id = callback_query.from_user.id

    callback = await callback_query.edit_message_text(
        "<b>🤖 Bot:</b> Silakan masukan jumlah limit yang ingin diubah default adalah 3?\n\n"
        "/cancel - Untuk Membatalkan!"
    )

    while True:
        try:
            user_response = await bot.listen(user_id, filters.text)
            user_input = user_response.text.strip()
            
            if user_response.text.startswith("/"):
                await user_response.delete()
                return await callback.edit(
                    "<b>❌ Proses Input Dibatalkan!</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            if not user_input.isdigit() or int(user_input) <= 0:
                await user_response.delete()
                clbk = await user_response.reply("❌ Input harus berupa angka lebih dari 0.")
                await asyncio.sleep(2)
                await clbk.delete()
                continue
                
            if int(user_input) <= 0:
                await user_response.delete()
                clbk = await user_response.reply("<b>❌ Limit harus lebih dari 0.</b>")
                await asyncio.sleep(2)
                await clbk.delete()
                continue

            await user_response.delete()
            set_daily_limit(user_input)
            return await callback.edit(
                f"✅ Limit harian berhasil diubah menjadi `{user_input}`.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )
        except Exception as e:
            await user_response.delete()
            
            await callback.edit(
                f"❌ Gagal menyimpan limit:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("add_limit"))
async def add_limit(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Silakan masukkan user_id atau @username target.\n\n/cancel - untuk membatalkan"
    )

    while True:
        try:
            target_msg = await bot.listen(user_id, filters.text)
            target_text = target_msg.text.strip()

            if target_text.startswith("/"):
                await target_msg.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            if target_text.startswith("@"):
                try:
                    user = await client.get_users(target_text)
                    target_id = user.id
                except Exception:
                    await target_msg.delete()
                    notif = await callback_query.message.reply("❌ Username tidak ditemukan.")
                    await asyncio.sleep(2)
                    await notif.delete()
                    continue
            else:
                try:
                    target_id = int(target_text)
                except ValueError:
                    await target_msg.delete()
                    notif = await callback_query.message.reply("❌ User ID tidak valid.")
                    await asyncio.sleep(2)
                    await notif.delete()
                    continue

            await target_msg.delete()
            break

        except Exception as e:
            return await msg.edit(f"❌ Terjadi kesalahan:\n{e}")

    await msg.edit("✅ Target ditemukan. Sekarang kirim jumlah limit yang ingin ditambahkan.\n\n/cancel - untuk membatalkan")

    while True:
        try:
            jumlah_msg = await bot.listen(user_id, filters.text)
            jumlah_text = jumlah_msg.text.strip()

            if jumlah_text.startswith("/"):
                await jumlah_msg.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            try:
                jumlah = int(jumlah_text)
                if jumlah <= 0:
                    await jumlah_msg.delete()
                    notif = await callback_query.message.reply("❌ Jumlah harus lebih dari 0.")
                    await asyncio.sleep(2)
                    await notif.delete()
                    continue
            except ValueError:
                await jumlah_msg.delete()
                notif = await callback_query.message.reply("❌ Jumlah tidak valid.")
                await asyncio.sleep(2)
                await notif.delete()
                continue

            await jumlah_msg.delete()
            add_user_limit(target_id, jumlah)
            return await msg.edit(
                f"✅ <b>Berhasil menambahkan limit sebanyak {jumlah} ke user {target_id}.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        except Exception as e:
            return await msg.edit(
                f"❌ Terjadi kesalahan:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("del_limit"))
async def del_limit(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Silakan masukkan user_id atau @username target yang ingin direset.\n\n/cancel - untuk membatalkan"
    )

    while True:
        try:
            response = await bot.listen(user_id, filters.text)
            target_text = response.text.strip()

            if target_text.startswith("/"):
                await response.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            if target_text.startswith("@"):
                try:
                    user = await client.get_users(target_text)
                    target_id = user.id
                except Exception:
                    await response.delete()
                    notif = await callback_query.message.reply("❌ Username tidak ditemukan.")
                    await asyncio.sleep(2)
                    await notif.delete()
                    continue
            else:
                try:
                    target_id = int(target_text)
                except ValueError:
                    await response.delete()
                    notif = await callback_query.message.reply("❌ User ID tidak valid.")
                    await asyncio.sleep(2)
                    await notif.delete()
                    continue

            await response.delete()
            reset_user_count(target_id)
            return await msg.edit(
                f"✅ Jumlah kirim {target_id} berhasil direset jadi 0.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        except Exception as e:
            return await msg.edit(
                f"❌ Terjadi kesalahan:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("addtag"))
async def add_tag(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Silakan kirim hashtag yang ingin ditambahkan, contoh: #crush\n\n/cancel - untuk membatalkan"
    )

    while True:
        try:
            response = await bot.listen(user_id, filters.text)
            tag_text = response.text.strip().lower()

            if tag_text.startswith("/"):
                await response.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            if not tag_text.startswith("#"):
                await response.delete()
                notif = await callback_query.message.reply("❌ Hashtag harus diawali dengan tanda `#`.")
                await asyncio.sleep(2)
                await notif.delete()
                continue

            await response.delete()
            add_hashtag(tag_text)
            return await msg.edit(
                f"<b>✅ Hashtag {tag_text} berhasil ditambahkan.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        except Exception as e:
            return await msg.edit(
                f"❌ Terjadi kesalahan:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("deltag"))
async def delete_tag(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Silakan kirim hashtag yang ingin dihapus, contoh: #crush\n\n/cancel - untuk membatalkan"
    )

    while True:
        try:
            response = await bot.listen(user_id, filters.text)
            tag_text = response.text.strip().lower()

            if tag_text.startswith("/"):
                await response.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            if not tag_text.startswith("#"):
                await response.delete()
                notif = await callback_query.message.reply("❌ Hashtag harus diawali dengan tanda `#`.")
                await asyncio.sleep(2)
                await notif.delete()
                continue

            await response.delete()
            remove_hashtag(tag_text)
            return await msg.edit(
                f"<b>✅ Hashtag {tag_text} berhasil dihapus.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        except Exception as e:
            return await msg.edit(
                f"❌ Terjadi kesalahan:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("listtag"))
async def list_tags(client: Client, callback_query):
    tags = get_all_hashtags()
    if not tags:
        return await callback_query.edit_message_text(
            "<b>ℹ️ Belum ada hashtag yang ditambahkan.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴀᴅᴅ_ᴛᴀɢ", callback_data="addtag")],
                [InlineKeyboardButton("ᴅᴇʟ_ᴛᴀɢ", callback_data="deltag")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )

    await callback_query.edit_message_text(
        "<b>📌 Daftar hashtag aktif:</b>\n\n" + "\n".join(tags),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴀᴅᴅ_ᴛᴀɢ", callback_data="addtag")],
            [InlineKeyboardButton("ᴅᴇʟ_ᴛᴀɢ", callback_data="deltag")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
        ])
    )

@bot.on_callback_query(filters.regex("addban"))
async def add_ban(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Silakan kirim kata yang ingin dilarang.\n\n/cancel - untuk membatalkan"
    )

    while True:
        try:
            response = await bot.listen(user_id, filters.text)
            word = response.text.strip()

            if word.startswith("/"):
                await response.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            await response.delete()
            add_banned_word(word)
            return await msg.edit(
                f"<b>✅ Kata {word} ditambahkan ke daftar terlarang.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        except Exception as e:
            return await msg.edit(
                f"❌ Terjadi kesalahan:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("delban"))
async def del_ban(client: Client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🤖 Silakan kirim kata yang ingin dihapus dari daftar terlarang.\n\n/cancel - untuk membatalkan"
    )

    while True:
        try:
            response = await bot.listen(user_id, filters.text)
            word = response.text.strip()

            if word.startswith("/"):
                await response.delete()
                return await msg.edit(
                    "<b>❌ Proses dibatalkan.</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                    ])
                )

            await response.delete()
            remove_banned_word(word)
            return await msg.edit(
                f"<b>✅ Kata {word} telah dihapus dari daftar terlarang.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        except Exception as e:
            return await msg.edit(
                f"❌ Terjadi kesalahan:\n{e}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

@bot.on_callback_query(filters.regex("listban"))
async def list_ban(client: Client, callback_query):
    words = get_banned_words()
    if not words:
        return await callback_query.edit_message_text(
            "<b>ℹ️ Belum ada kata terlarang.</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴀᴅᴅ_ʙᴀɴ", callback_data="addban")],
                [InlineKeyboardButton("ᴅᴇʟ_ʙᴀɴ", callback_data="delban")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )

    return await callback_query.edit_message_text(
        "<b>🚫 Daftar kata terlarang:</b>\n\n" + "\n".join(f"- {w}" for w in words),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴀᴅᴅ_ʙᴀɴ", callback_data="addban")],
            [InlineKeyboardButton("ᴅᴇʟ_ʙᴀɴ", callback_data="delban")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
        ])
    )

@Client.on_callback_query(filters.regex("addban") & filters.user(OWNER_ID))
async def add_ban_callback(client, callback_query):                                       
    user_id = callback_query.from_user.id
    
    msg = await callback_query.edit_message_text(
        "🤖 Silakan kirim kata yang ingin diblokir?\n\n/cancel - Untuk Membatalkan!"
    )

    try:
        response = await bot.listen(user_id)
        word = response.text.strip()

        if word.startswith("/"):
            await response.delete()
            return await msg.edit(
                "<b>❌ Proses dibatalkan.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )
            
        add_banned_word(word)

        await callback_query.edit_message_text(
            f"✅ Kata `{word}` berhasil ditambahkan ke daftar terlarang.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )
    except Exception as e:
        return await msg.edit(
            f"❌ Terjadi kesalahan:\n{e}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )

@bot.on_callback_query(filters.regex("delban") & filters.user(OWNER_ID))
async def del_ban_callback(client, callback_query):
    user_id = callback_query.from_user.id

    msg = await callback_query.edit_message_text(
        "🗑️ Silakan kirim kata yang ingin dihapus dari daftar terlarang.\n\n/cancel - Untuk Membatalkan!"
    )

    try:
        response = await bot.listen(user_id)
        word = response.text.strip()

        if word.startswith("/"):
            await response.delete()
            return await msg.edit(
                "<b>❌ Proses dibatalkan.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        if word not in get_banned_words():
            return await msg.edit(
                f"❌ Kata `{word}` tidak ditemukan dalam daftar terlarang.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
                ])
            )

        remove_banned_word(word)

        await callback_query.edit_message_text(
            f"✅ Kata `{word}` berhasil dihapus dari daftar terlarang.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )

    except Exception as e:
        return await msg.edit(
            f"❌ Terjadi kesalahan:\n{e}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="menu_callback")]
            ])
        )
        
@Client.on_message(filters.command("addban") & filters.user(OWNER_ID))
async def add_banned(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Contoh: `/addban kata`")
    word = message.command[1]
    add_banned_word(word)
    await message.reply(f"✅ Kata `{word}` ditambahkan ke daftar terlarang.")

@Client.on_message(filters.command("delban") & filters.user(OWNER_ID))
async def del_banned(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Contoh: `/delban kata`")
    word = message.command[1]
    remove_banned_word(word)
    await message.reply(f"✅ Kata `{word}` telah dihapus dari daftar terlarang.")
