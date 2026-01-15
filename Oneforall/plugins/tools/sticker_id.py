from pyrogram import filters
from Oneforall import app

@app.on_message(filters.sticker)
async def sticker_id(_, message):
    sticker = message.sticker

    text = (
        "🎯 **sᴛɪᴄᴋᴇʀ ɪᴅ ғᴏᴜɴᴅ!**\n\n"
        f"📌 **ғɪʟᴇ ɪᴅ:**\n"
        f"`{sticker.file_id}`\n\n"
        f"📦 **ғɪʟᴇ ᴜɴɪǫᴜᴇ ɪᴅ:**\n"
        f"`{sticker.file_unique_id}`"
    )

    await message.reply_text(text)
