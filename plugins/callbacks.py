# plugins/callbacks.py

import time
import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram import InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, ContextTypes

from config import (
    START_CAPTION,
    HELP_TEXT,
    STATUS_TEXT,
    BOT_UPTIME,
)

from helper.database import MongoDB
from config import DB_URL, DB_NAME
from plugins.commands import send_users_page

db = MongoDB(DB_URL, DB_NAME)

USERS_PER_PAGE = 9


# ──────────────────────────────
# Keyboards
# ──────────────────────────────

def main_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("⚡ sᴛᴀᴛᴜs", callback_data="status"),
            ],
            [
                InlineKeyboardButton("✖ ᴄʟᴏsᴇ", callback_data="close"),
            ]
        ]
    )


def back_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("◈ ʙᴀᴄᴋ", callback_data="back"),
                InlineKeyboardButton("✖ ᴄʟᴏsᴇ", callback_data="close"),
            ]
        ]
    )


# ──────────────────────────────
# Users Pagination Panel
# ──────────────────────────────

async def users_panel(query, page: int):

    all_users = await db.full_userbase()
    total = len(all_users)

    start = page * USERS_PER_PAGE
    end = start + USERS_PER_PAGE

    users_page = all_users[start:end]

    caption = (
        f"<blockquote><b>⚡ User Database Panel</b>\n\n"
        f"◇ Total Users: {total}\n"
        f"◇ Showing: {start+1} - {min(end, total)}</blockquote>\n\n"
    )

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

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton("« Prev", callback_data=f"users:{page-1}")
        )

    if end < total:
        nav.append(
            InlineKeyboardButton("Next »", callback_data=f"users:{page+1}")
        )

    if nav:
        buttons.append(nav)

    buttons.append(
        [InlineKeyboardButton("◈ ʙᴀᴄᴋ", callback_data="back")]
    )

    await query.message.edit_caption(
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ──────────────────────────────
# Single Callback Router
# ──────────────────────────────

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user = update.effective_user

    await query.answer()
    data = query.data

    # ───── HELP ─────
    if data == "help":
        await query.message.edit_caption(
            caption=HELP_TEXT.format(mention=user.mention_html()),
            parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard()
        )

    # ───── STATUS ─────
    elif data == "status":

        uptime_seconds = int(time.time() - BOT_UPTIME)
        uptime_formatted = str(datetime.timedelta(seconds=uptime_seconds))

        restart_time = datetime.datetime.utcnow().strftime(
            "%d-%m-%Y %H:%M:%S UTC"
        )

        total_users = await db.total_users()

        await query.message.edit_caption(
            caption=STATUS_TEXT.format(
                mention=user.mention_html(),
                uptime=uptime_formatted,
                restart=restart_time,
                users=total_users
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=back_keyboard()
        )

    # ───── USERS PANEL ─────
    elif data.startswith("users:"):
        page = int(data.split(":")[1])
        await send_users_page(update, context, page)
    
    # ───── USER INFO ─────
    # ───── USER INFO CALLBACK ─────
    elif data.startswith("userinfo:"):

        user_id = int(data.split(":")[1])

        # Fetch user object
        try:
            user_obj = await context.bot.get_chat(user_id)
        except:
            return await query.answer(
                "User not accessible.",
                show_alert=True
            )

        # Basic Info
        first_name = user_obj.first_name or "None"
        last_name = user_obj.last_name or "None"
        username = f"@{user_obj.username}" if user_obj.username else "None"

        permalink = (
            f"https://t.me/{user_obj.username}"
            if user_obj.username
            else "No Link"
        )

        # ───── DATABASE INFO ─────
        # Join Request History Count
        join_requests = await db.join_requests.count_documents(
            {"user_id": user_id}
        )

        # ───── Appraisal Text ─────
        text = (
            f"<blockquote><b>───【 Appraisal Results 】\n\n"
            f"ID: <code>{user_id}</code>\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"Username: {username}\n"
            f"Permalink: {permalink}\n\n"
            f"───【 Database Info 】\n"
            f"Join Requests: {join_requests}\n"
            f"</b></blockquote>"
        )

        # ───── Profile Photo Fetch ─────
        try:
            photos = await context.bot.get_user_profile_photos(
                user_id=user_id,
                limit=1
            )

            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id

                media = InputMediaPhoto(
                    media=file_id,
                    caption=text,
                    parse_mode=ParseMode.HTML
                )

                await query.message.edit_media(
                    media=media,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "◈ Back",
                                    callback_data="users:0"
                                ),
                                InlineKeyboardButton(
                                    "✖ Close",
                                    callback_data="close"
                                )
                            ]
                        ]
                    )
                )
                return

        except Exception as e:
            print("Profile Pic Error:", e)

        # If no profile photo → fallback text
        await query.message.edit_caption(
            caption=text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("◈ Back", callback_data="users:0")
                    ],
                    [
                        InlineKeyboardButton("✖ Close", callback_data="close")
                    ]
                ]
            )
        )

    # ───── BACK ─────
    elif data == "back":
        await query.message.edit_caption(
            caption=START_CAPTION.format(
                mention=user.mention_html()
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard()
        )

    # ───── CLOSE ─────
    elif data == "close":
        await query.message.delete()

    # ───── NOOP ─────
    elif data == "noop":
        await query.answer("👀")

    # ───── IGNORE ─────
    elif data == "ignore":
        await query.answer()

# ──────────────────────────────
# Setup Loader
# ──────────────────────────────

def setup_callbacks(application):

    application.add_handler(
        CallbackQueryHandler(cb_handler)
    )
