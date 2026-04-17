# config.py
import os
import time


# ──────────────────────────────
# Core Bot Config
# ──────────────────────────────
BOT_UPTIME = time.time()
BOT_TOKEN = os.getenv("BOT_TOKEN", "8599022127:AAHszpC9oRH0sIrtyT720R0uYLSxRmu45kM")
OWNER_ID = int(os.getenv("OWNER_ID", "7156099919"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "Waifu_approval_bot")
DB_URL = os.getenv("DB_URL", "mongodb+srv://ANI_OTAKU:ANI_OTAKU@cluster0.t3frstc.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "Waifu_approval_bot")
START_PIC = os.getenv("START_PIC", "https://i.ibb.co/3Lf2Vts/image.png")
APPROVED_PIC = os.getenv("APPROVED_PIC", "https://i.ibb.co/FLL0drcZ/neuralpony-61.png")
USERS_PIC = os.getenv("USERS_PIC", "https://i.ibb.co/TJrHrCm/download-49.jpg")
START_STICKER = os.getenv("START_STICKER", "CAACAgUAAxkBAAKiwGmP9N5enA5ZBmbI_EVik5qaS-Y0AAJSGwACFuwBVoVvP5pgWVF6HgQ")


if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing in environment variables!")


# ──────────────────────────────
# Messages & Text Constants
# ──────────────────────────────

WELCOME_TEXT = (
    "🎉 <b>Your join request has been approved!</b>\n"
    "Welcome to the community 🍃"
)

# Auto-Approval Message Content

APPROVED_CAPTION = (
        "<blockquote>◈ Hᴇʏ {mention}× sᴇɴᴘᴀɪ\n\n"
        "›› ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ {chat} "
        "ʜᴀs ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ.</blockquote>"
    )

START_CAPTION = (
    "<blockquote><b>◈ Hᴇʏ {mention}× sᴇɴᴘᴀɪ\n\n"
    "›› ɪ ᴀᴍ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇʀ ʙᴏᴛ 🍃\n"
    "ɪ ᴄᴀɴ ɪɴsᴛᴀɴᴛʟʏ ᴀᴘᴘʀᴏᴠᴇ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs "
    "ɪɴ ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.</b></blockquote>"
)



HELP_TEXT = (
    "<blockquote>◈ Hᴇʏ {mention} ×\n"
    "›› ᴛʜɪs ʙᴏᴛ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇs ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs "
    "ɪɴ ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs 🍃\n"
    "➲ Add me as admin\n"
    "➲ Enable Join Requests\n"
    "➲ I will approve instantly</blockquote>"
)

STATUS_TEXT = (
    "<blockquote>⚡ <b>Bot Status</b>\n"
    "›› User: {mention}\n"
    "›› Uptime: <code>{uptime}</code>\n"
    "›› Last Restarted: <code>{restart}</code>\n"
    "›› Total Users: <code>{users}</code>\n"
    "›› System: Stable 🍃</blockquote>"
)

# ─────────────────────────────
# Database Settings (Optional)
# ─────────────────────────────


