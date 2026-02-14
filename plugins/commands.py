# plugins/commands.py

import asyncio
import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)

from config import OWNER_ID
from helper.database import MongoDB
from config import DB_URL, DB_NAME, USERS_PIC

# DB Instance
db = MongoDB(DB_URL, DB_NAME)

# Pagination Limit
USERS_PER_PAGE = 9


# ──────────────────────────────
# Helper: Owner Check
# ──────────────────────────────

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID



# ──────────────────────────────
# ✅ /users Command
# ──────────────────────────────

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    await send_users_page(update, context, page=0)


async def send_users_page(update, context, page: int):
    all_users = await db.full_userbase()
    total = len(all_users)

    if total == 0:
        return await update.message.reply_text(
            "<blockquote>No users found in database.</blockquote>",
            parse_mode=ParseMode.HTML
        )

    start = page * USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    users_page = all_users[start:end]

    caption = (
        f"<blockquote>⚡ <b>User Database Panel</b>\n"
        f"›› Total Users: <b>{total}</b>\n"
        f"›› Showing: <b>{start+1} - {min(end, total)}</b></blockquote>"
    )

    # Buttons in 3x3 format
    buttons = []
    row = []

    for user_id in users_page:
        row.append(
            InlineKeyboardButton(
                text=str(user_id),
                callback_data=f"userinfo:{user_id}"
            )
        )

        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # Pagination Buttons
    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton("« Prev", callback_data=f"users:{page-1}")
        )

    if end < total:
        nav_buttons.append(
            InlineKeyboardButton("Next »", callback_data=f"users:{page+1}")
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append(
        [InlineKeyboardButton("✖ Close", callback_data="close")]
    )

    markup = InlineKeyboardMarkup(buttons)

    # First send
    if update.message:
        await update.message.reply_photo(
            photo=USERS_PIC,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=markup
        )

    # Pagination edit
    elif update.callback_query:
        await update.callback_query.message.edit_caption(
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=markup
        )

# ──────────────────────────────
# ✅ /broadcast Command (Permanent)
# ──────────────────────────────

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "Reply to a message to broadcast it."
        )

    msg = update.message.reply_to_message
    users = await db.full_userbase()

    total = len(users)

    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    status = await update.message.reply_text("🚀 Broadcasting...")

    for user_id in users:
        try:
            await msg.copy(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.05)

        except Exception as e:
            err = str(e).lower()

            if "blocked" in err:
                blocked += 1
            elif "deleted" in err or "deactivated" in err:
                deleted += 1
            else:
                failed += 1

    unsuccessful = blocked + deleted + failed

    await status.edit_text(
        f"<blockquote><b>Broadcast Completed</b>\n\n"
        f"◇ Total Users: {total}\n"
        f"◇ Successful: {success}\n"
        f"◇ Blocked Users: {blocked}\n"
        f"◇ Deleted Accounts: {deleted}\n"
        f"◇ Unsuccessful: {unsuccessful}</blockquote>",
        parse_mode=ParseMode.HTML
    )

# ──────────────────────────────
# Plugin Loader
# ──────────────────────────────

def setup_commands(application):

    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
