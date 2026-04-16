"""
link_generator.py  –  /genlink and /batch commands

NEW /genlink flow (matches the screenshot):
  Admin sends:  /genlink   (alone, or the bot asks for the DB channel post)
  The bot accepts a forwarded message OR a DB-channel post URL as before,
  BUT it now also accepts the new "inline" format:

      LABEL  https://t.me/+xxxxx  /genlink

  i.e. the command message itself contains a t.me link, so no back-and-forth
  is needed.  The bot parses the link from the command message, resolves the
  message-id, encodes it, and replies immediately with:

      Here is your link:
      https://t.me/<bot_username>?start=<base64>
      [🔁 Share URL]

/batch works the same way: two links/forwards in two separate messages (unchanged).
"""

import re

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id


# ── helpers ────────────────────────────────────────────────────────────────────

def _extract_link_from_text(text: str):
    """Return the first https://t.me/… URL found in *text*, or None."""
    match = re.search(r"https://t\.me/\S+", text)
    return match.group(0) if match else None


async def _resolve_msg_id(client, message):
    """
    Try to resolve a DB-channel message-id from *message*.
    Works for:
      - forwarded messages
      - plain-text messages that contain a DB-channel post URL
      - the /genlink command message itself if it contains a t.me URL
    Returns the integer message-id, or None on failure.
    """
    # 1. Standard helper handles forwards + explicit post-URLs
    msg_id = await get_message_id(client, message)
    if msg_id:
        return msg_id

    # 2. Try to pull a URL out of the raw text (covers the inline format)
    raw = message.text or message.caption or ""
    url = _extract_link_from_text(raw)
    if not url:
        return None

    # Build a synthetic "text-only" message to hand to get_message_id
    class _FakeMsg:
        forward_from_chat = None
        forward_sender_name = None
        text = url

    return await get_message_id(client, _FakeMsg())


def _make_reply(link: str):
    text = f"<b>Here is your link:</b>\n\n{link}"
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share URL",
                              url=f"https://telegram.me/share/url?url={link}")]
    ])
    return text, markup


# ── /genlink ───────────────────────────────────────────────────────────────────

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def link_generator(client: Client, message: Message):
    """
    Usage (any of the three are accepted):

    1. Inline – send everything in ONE message:
           HARI https://t.me/+QEk0u-hr7Uo2M2Nl /genlink
       or
           /genlink https://t.me/c/1234567890/42

    2. Reply  – reply to a forwarded DB-channel post with /genlink.

    3. Interactive – send /genlink alone and the bot asks for the post.
    """

    # ── Case A: the command message itself contains a URL ─────────────────────
    msg_id = await _resolve_msg_id(client, message)
    if msg_id:
        base64_string = await encode(f"file-{msg_id * abs(client.db_channel.id)}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        text, markup = _make_reply(link)
        await message.reply_text(text, reply_markup=markup, quote=True,
                                  disable_web_page_preview=True)
        return

    # ── Case B: the command is a reply to a forwarded / URL message ───────────
    if message.reply_to_message:
        msg_id = await _resolve_msg_id(client, message.reply_to_message)
        if msg_id:
            base64_string = await encode(f"file-{msg_id * abs(client.db_channel.id)}")
            link = f"https://t.me/{client.username}?start={base64_string}"
            text, markup = _make_reply(link)
            await message.reply_text(text, reply_markup=markup, quote=True,
                                      disable_web_page_preview=True)
            return

    # ── Case C: interactive – ask the admin for the post ─────────────────────
    while True:
        try:
            channel_message = await client.ask(
                text=(
                    "📨 <b>Send the DB Channel post</b>\n\n"
                    "You can:\n"
                    "• Forward a message from the DB channel\n"
                    "• Paste the post link (e.g. <code>https://t.me/c/xxx/42</code>)\n"
                    "• Send  <code>NAME  https://t.me/+invite  /genlink</code>"
                ),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return

        msg_id = await _resolve_msg_id(client, channel_message)
        if msg_id:
            break

        await channel_message.reply(
            "❌ <b>Error</b>\n\n"
            "This doesn't seem to be from my DB channel. Please try again.",
            quote=True,
        )

    base64_string = await encode(f"file-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    text, markup = _make_reply(link)
    await channel_message.reply_text(text, reply_markup=markup, quote=True,
                                      disable_web_page_preview=True)


# ── /batch ─────────────────────────────────────────────────────────────────────

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch(client: Client, message: Message):
    """Generate a batch link covering a range of DB-channel posts."""

    # ── First message ─────────────────────────────────────────────────────────
    while True:
        try:
            first_message = await client.ask(
                text=(
                    "📨 <b>First post</b>\n\n"
                    "Forward the <u>first</u> message from the DB channel, "
                    "or paste its post link."
                ),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return

        f_msg_id = await _resolve_msg_id(client, first_message)
        if f_msg_id:
            break

        await first_message.reply(
            "❌ <b>Error</b>\n\nNot from my DB channel. Please try again.",
            quote=True,
        )

    # ── Second message ────────────────────────────────────────────────────────
    while True:
        try:
            second_message = await client.ask(
                text=(
                    "📨 <b>Last post</b>\n\n"
                    "Forward the <u>last</u> message from the DB channel, "
                    "or paste its post link."
                ),
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return

        s_msg_id = await _resolve_msg_id(client, second_message)
        if s_msg_id:
            break

        await second_message.reply(
            "❌ <b>Error</b>\n\nNot from my DB channel. Please try again.",
            quote=True,
        )

    ch_id = abs(client.db_channel.id)
    string = f"file-{f_msg_id * ch_id}-{s_msg_id * ch_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    text, markup = _make_reply(link)
    await second_message.reply_text(text, reply_markup=markup, quote=True,
                                     disable_web_page_preview=True)
