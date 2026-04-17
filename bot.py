# bot.py

import asyncio
import logging
import os
#from threading import Thread
#from flask import Flask

from telegram import Bot
from telegram.constants import ParseMode, ChatAction
from telegram.ext import Application

from config import BOT_TOKEN, OWNER_ID
from plugins.approver import setup_approver
from plugins.callbacks import setup_callbacks
from plugins.__init__ import setup_start, setup_commands

from helper.database import MongoDB
from config import DB_URL, DB_NAME


# ──────────────────────────────
# ✅ FLASK + THREAD (Render Support)
# ──────────────────────────────

#app = Flask(__name__)

#@app.route("/")
#def home():
#    return "Bot is running!", 200


#def run_flask():
#    app.run(
#        host="0.0.0.0",
#        port=int(os.environ.get("PORT", 10000))
#    )


# ──────────────────────────────
# Logging Setup (Production Style)
# ──────────────────────────────

logging.basicConfig(
    format="%(asctime)s │ %(levelname)s │ %(name)s → %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("BotifyX")

db = MongoDB(DB_URL, DB_NAME)


# ──────────────────────────────
# Restart Notification
# ──────────────────────────────

async def notify_restart(bot: Bot) -> None:
    """
    Sends an advanced restart notification to the owner.
    Includes Telegram styled message effects.
    """
    try:
        # Step 1: Initial boot message
        m = await bot.send_message(
            chat_id=OWNER_ID,
            text="...ʜᴇʏ sᴇɴᴘᴀɪ\nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ..."
        )

        await asyncio.sleep(0.6)

        # Step 2: Emoji pulse animation
        for emoji in ["🎊", "⚡", "✨", "🔥"]:
            await m.edit_text(emoji)
            await asyncio.sleep(0.8)

        # Step 3: Sticker choosing effect (premium vibe)
        await bot.send_chat_action(
            chat_id=OWNER_ID,
            action=ChatAction.CHOOSE_STICKER
        )

        await asyncio.sleep(1)

        # Step 4: Final restart confirmation
        restart_text = (
            "<blockquote><b>›› ʜᴇʏ sᴇɴᴘᴀɪ!!</b>\n"
            "<b>ɪ'ᴍ ᴀʟɪᴠᴇ ɴᴏᴡ 🍃...</b></blockquote>"
        )

        await m.edit_text(
            restart_text,
            parse_mode=ParseMode.HTML
        )

        logger.info("Restart notification sent to owner.")

    except Exception as err:
        logger.warning(f"Startup notify failed → {err}")


# ──────────────────────────────
# Main Entrypoint
# ──────────────────────────────

def main() -> None:
    """
    Professional bot entrypoint.
    Only bootstraps application + loads modules.
    """

    # ✅ Start Flask Server in Background (Render Needs Open Port)
    #Thread(target=run_flask, daemon=True).start()

    logger.info("Initializing BotifyX Core...")

    # Build Application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Load Feature Modules
    setup_approver(application)
    setup_callbacks(application)
    setup_start(application)
    setup_commands(application)

    # Notify Owner (Async Safe)
    application.post_init = lambda app: notify_restart(app.bot)

    # Startup Banner
    logger.info("BotifyX successfully started.")

    print(r"""
██████╗  ██████╗ ████████╗██╗███████╗██╗  ██╗
██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝╚██╗██╔╝
██████╔╝██║   ██║   ██║   ██║█████╗   ╚███╔╝ 
██╔══██╗██║   ██║   ██║   ██║██╔══╝   ██╔██╗ 
██████╔╝╚██████╔╝   ██║   ██║██║     ██╔╝ ██╗
╚═════╝  ╚═════╝    ╚═╝   ╚═╝╚═╝     ╚═╝  ╚═╝

        ⚡ BotifyX Pro Auto Approver ⚡
          >>> System Online & Stable <<<
""")

    # ✅ Correct Polling Method for PTB v20+
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "chat_join_request", "callback_query"],
    )


# ──────────────────────────────
# Runner
# ──────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
