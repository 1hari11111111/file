from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"file-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]
    ])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
