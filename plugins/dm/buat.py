'''

█ █▄ █    █▄█ ▄▀▄ █▄ ▄█ ██▀    █▀▄ █▀▄ █▀ 
█ █ ▀█    █ █ █▀█ █ ▀ █ █▄▄    █▀  █▄▀ █▀ 
                        Dev : IlhamGUD

'''

import os
import shutil
from pdf import PDF
from time import sleep
from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as InHamePDF
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup





#--------------->
#--------> Config var.
#------------------->

BANNED_USERS=Config.BANNED_USERS
ADMIN_ONLY=Config.ADMIN_ONLY
ADMINS=Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "Kamu telah di-BAN karena melanggar ketentuan"


feedbackMsg = """
[Tulis feedback 📋](https://tellonym.me/Developer_InHame)
"""

caraMsg = """
[Cara Menyimpan PDF 💾](https://telegra.ph/Cara-Menyimpan-PDF-ke-Storage-02-20-2)
"""

button=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "CHAT DEV",
                    url="https://t.me/ilhamshff"
                )
            ]
       ]
    )

#--------------->
#--------> REPLY TO /buat MESSAGE
#------------------->


@InHamePDF.on_message(filters.private & filters.command(["buat"]) & ~filters.edited)
async def buat(bot, message):
    try:
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse,
                reply_markup=button
            )
            return
        
        # newName : new file name(/buat ___)
        newName = str(message.text.replace("/buat", ""))
        images = PDF.get(message.chat.id)
        
        if isinstance(images, list):
            pgnmbr = len(PDF[message.chat.id])
            del PDF[message.chat.id]
        
        # IF NO IMAGES SEND BEFORE
        if not images:
            await message.reply_chat_action("typing")
            imagesNotFounded = await message.reply_text(
                "`⛔️ - Silahkan kirim gambar`"
            )
            sleep(5)
            await message.delete()
            await imagesNotFounded.delete()
            return
        
        gnrtMsgId = await message.reply_text(
            f"`🖨️ - Membuat pdf`"
        )
        
        if newName == " name":
            fileName = f"{message.from_user.first_name}" + ".pdf"
        elif len(newName) > 1 and len(newName) <= 45:
            fileName = f"{newName}" + ".pdf"
        elif len(newName) > 45:
            fileName = f"{message.from_user.first_name}" + ".pdf"
        else:
            fileName = f"{message.chat.id}" + ".pdf"
        
        images[0].save(fileName, save_all = True, append_images = images[1:])
        await gnrtMsgId.edit(
             "`📤 - Mengirim pdf`",
        )
        await message.reply_chat_action("upload_document")
        generated = await bot.send_document(
            chat_id=message.chat.id,
            document=open(fileName, "rb"),
            thumb=Config.PDF_THUMBNAIL,
            caption = f"ℹ️ - Nama File: `{fileName}`\n\n📄 - Total halaman: `{pgnmbr}`"
        )
        await gnrtMsgId.edit(
            "`✅ - Berhasil mengirim pdf`",
        )
        os.remove(fileName)
        shutil.rmtree(f"{message.chat.id}")
        sleep(5)
        await message.reply_chat_action("typing")
        await message.reply_text(
            feedbackMsg, disable_web_page_preview = True
        )
        await bot.send_message(
            message.chat.id, caraMsg,
            disable_web_page_preview = True
        )
        
    except Exception:
        try:
            os.remove(fileName)
            shutil.rmtree(f"{message.chat.id}")
        except Exception:
            pass


# Copyright InHame Dev
