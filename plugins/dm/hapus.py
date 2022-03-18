import os
import shutil
from pdf import PDF
from pyrogram import filters
from pyrogram import Client as InHamePDF

@InHamePDF.on_message(filters.command(["hapus"]))
async def _cancelI2P(bot, message):
    try:
        await message.reply_chat_action("typing")
        del PDF[message.chat.id]
        await message.reply_text("`Berhasil menghapus semua antrian`", quote=True)
        shutil.rmtree(f"{message.chat.id}")
    except Exception:
        await message.reply_text("`Tidak ada antrian`", quote=True)