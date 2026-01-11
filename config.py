import os

# Bot Token
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Owner ID
OWNER_ID = 5541236874

# Zorunlu Kanal (bot panelinden değiştirilebilir)
FORCE_CHANNEL = "@snd_yatirim"

# Bot Durumu
BOT_ACTIVE = True
WELCOME_ACTIVE = True

# Dosya yolları
DB_FILE = "bot_database.db"
BANNED_USERS_FILE = "banned_users.json"
