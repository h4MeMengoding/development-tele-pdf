'''

█ █▄ █    █▄█ ▄▀▄ █▄ ▄█ ██▀    █▀▄ █▀▄ █▀ 
█ █ ▀█    █ █ █▀█ █ ▀ █ █▄▄    █▀  █▄▀ █▀ 
                        Dev : IlhamGUD

'''

from pyrogram import filters
from Configs.dm import Config
from pyrogram import Client as InHamePDF
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import InlineKeyboardMarkup




#--------------->
#--------> Config var.
#------------------->

BANNED_USERS = Config.BANNED_USERS
ADMIN_ONLY = Config.ADMIN_ONLY
ADMINS = Config.ADMINS

#--------------->
#--------> LOCAL VARIABLES
#------------------->

UCantUse = "Kamu telah di-BAN karena melanggar ketentuan"


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
#--------> PDF REPLY BUTTON
#------------------->


@InHamePDF.on_message(filters.private & ~filters.edited)
async def spam(bot, message):
    try:
        await message.reply_chat_action("typing")
        if (message.chat.id in BANNED_USERS) or (
            (ADMIN_ONLY) and (message.chat.id not in ADMINS)
        ):
            await message.reply_text(
                UCantUse, reply_markup=button
            )
            return
        await message.reply_text(
            f"`❗ - Perintah yang anda masukkan salah...\n\n`/menu `untuk melihat perintah yang tersedia`", quote=True
        )
    except Exception:
        pass


# Copyright InHame Dev
