
from pyrogram import filters
from pyrogram import Client as InHamePDF


@InHamePDF.on_message(filters.command(["message"]))
async def _cancelI2P(bot, message):
    try:
        await message.reply_chat_action("typing")
        await message.reply_text(f"message_id: `{message.message_id}`", quote=True)
    except Exception:
        pass