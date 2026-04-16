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


# ── /genlink ───────────────────────────────────────────────────────────────────

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def link_generator(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to any message with /genlink to generate a link.",
            quote=True
        )
        return

    msg_id = await get_message_id(client, message.reply_to_message)
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


# ── /batch ─────────────────────────────────────────────────────────────────────

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch(client: Client, message: Message):
    """
    Step 1: Reply to the FIRST message with /batch
    Step 2: Bot asks you to reply to the LAST message
    """
    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to the <b>first</b> message with /batch to start.",
            quote=True
        )
        return

    f_msg_id = await get_message_id(client, message.reply_to_message)
    if not f_msg_id:
        await message.reply_text(
            "❌ Could not get message ID from that message.",
            quote=True
        )
        return

    ask_msg = await message.reply_text(
        "✅ Got the <b>first</b> message!\n\n"
        "Now reply to the <b>last</b> message with /batch_end",
        quote=True
    )

    # Store first msg id in a simple in-memory dict keyed by user id
    batch._pending[message.from_user.id] = f_msg_id


batch._pending = {}


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch_end"))
async def batch_end(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in batch._pending:
        await message.reply_text(
            "❌ Start a batch first by replying to the first message with /batch",
            quote=True
        )
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ Reply to the <b>last</b> message with /batch_end",
            quote=True
        )
        return

    s_msg_id = await get_message_id(client, message.reply_to_message)
    if not s_msg_id:
        await message.reply_text(
            "❌ Could not get message ID from that message.",
            quote=True
        )
        return

    f_msg_id = batch._pending.pop(user_id)
    ch_id = abs(client.db_channel.id)
    base64_string = await encode(f"file-{f_msg_id * ch_id}-{s_msg_id * ch_id}")
    link = f"https://t.me/{client.username}?start={base64_string}"

    text = f"<b>Here is your link:</b>\n\n{link}"
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "➡️ SHARE URL",
            url=f"https://telegram.me/share/url?url={link}"
        )]
    ])
    await message.reply_text(text, reply_markup=markup, quote=True,
                              disable_web_page_preview=True)
