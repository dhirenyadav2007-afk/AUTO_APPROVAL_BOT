"""
Join Request Auto-Approver Plugin

This module listens for incoming join requests in private
channels where the bot has invite permissions enabled.

Workflow:
    • Detects user join request
    • Automatically approves the request
    • Logs approved user in MongoDB
    • Sends approval DM to the user

Used for private channel access via bot-generated
Request-To-Join invite links.

Independent of ForceSub system.
"""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ChatJoinRequestHandler, ContextTypes

from config import APPROVED_PIC, APPROVED_CAPTION
from datetime import datetime

from helper.database import MongoDB
from config import DB_URL, DB_NAME


# ──────────────────────────────
# MongoDB Initialization
# Stores approved join records
# ──────────────────────────────
db = MongoDB(DB_URL, DB_NAME)

approved_users = db.db["approved_join_users"]


# ──────────────────────────────
# Auto Approve Join Request
# ──────────────────────────────
async def auto_approve_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Automatically approves join requests in private
    channels/groups where bot has invite permission.

    Also:
        • Saves approval record in MongoDB
        • Sends approval DM to the user
    """

    join = update.chat_join_request
    if not join:
        return

    user = join.from_user
    chat = join.chat

    user_id = user.id
    chat_id = chat.id

    # ────────────────
    # Approve Request
    # ────────────────
    try:
        await join.approve()
    except:
        return


    # ────────────────
    # Log Approval
    # ────────────────
    try:
        approved_users.update_one(
            {"_id": f"{user_id}:{chat_id}"},
            {
                "$set": {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "approved": True,
                    "time": datetime.utcnow()
                }
            },
            upsert=True
        )
    except:
        pass


    # ────────────────
    # Send DM Message
    # ────────────────
    try:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=APPROVED_PIC,
            caption=APPROVED_CAPTION.format(
                mention=user.mention_html(),
                chat=chat.title
            ),
            parse_mode=ParseMode.HTML
        )
    except:
        pass


# ──────────────────────────────
# Plugin Loader
# Registers Handler to PTB App
# ──────────────────────────────
def setup_approver(application) -> None:
    """
    Registers join request handler into application.
    """

    application.add_handler(
        ChatJoinRequestHandler(auto_approve_request)
    )
