import re

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


def _make_reply(link: str):
    text = f"<b>Here is your link:</b>\n\n{link}"
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "➡️ SHARE URL",
            url=f"https://telegram.me/share/url?url={link}"
        )]
    ])
    return text, markup


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def link_generator(client: Client, message: Message):
    # Must be a reply
    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to any message with /genlink to generate a link.",
            quote=True
        )
        return

    replied = message.reply_to_message
    msg_id = await get_message_id(client, replied)

    if not msg_id:
        await message.reply_text(
            "❌ Could not generate a link from that message.",
            quote=True
        )
        return

    base64_string = await encode(f"file-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    text, markup = _make_reply(link)
    await message.reply_text(text, reply_markup=markup, quote=True,
                              disable_web_page_preview=True)
