# plugins/start.py

import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.constants import ParseMode
from telegram.constants import ChatAction
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)

from config import (
    START_PIC,
    START_CAPTION,
    START_STICKER,
    BOT_USERNAME,
    DB_URL,
    DB_NAME,
)

from helper.database import MongoDB

# DB Instance
db = MongoDB(DB_URL, DB_NAME)
# ──────────────────────────────
# /start Command Handler
# ──────────────────────────────

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Start command with animation + sticker + start panel.
    """

    message = update.effective_message
    user = update.effective_user

    # ✅ Save User in Database
    await db.add_user(user.id)

    # Step 1: Animated Loading Message
    m = await message.reply_text(
        "...ʜᴇʏ ᴛʜᴇʀᴇ 🍃\nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ..."
    )

    await asyncio.sleep(0.5)

    for emoji in ["🎉", "⚡", "🎊", "💥"]:
        await m.edit_text(emoji)
        await asyncio.sleep(0.8)

    await context.bot.send_chat_action(
        chat_id=message.chat_id,
        action=ChatAction.CHOOSE_STICKER
    )

    await asyncio.sleep(1)

    await m.edit_text(
        f"<b>◈ Hᴇʏ {user.mention_html()}× sᴇɴᴘᴀɪ"
        "!!!!!!!</b>",
        parse_mode=ParseMode.HTML
    )

    # Step 2: Send Sticker
    if START_STICKER:
        try:
            await message.reply_sticker(START_STICKER)
        except:
            pass

    # Step 3: Inline Buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴄʜᴀɴɴᴇʟ ❌",
                    url=f"https://t.me/{BOT_USERNAME}?startchannel=true"
                )
            ],
            [
                InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("⚡ sᴛᴀᴛᴜs", callback_data="status"),
            ],
        ]
    )

    # Step 4: Send Start Image + Caption Panel
    caption = START_CAPTION.format(
        mention=user.mention_html()
    )

    await message.reply_photo(
        photo=START_PIC,
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


# ──────────────────────────────
# Setup Function
# ──────────────────────────────

def setup_start(application) -> None:
    """
    Registers /start command handler.
    """

    application.add_handler(
        CommandHandler("start", start_command)
    )
