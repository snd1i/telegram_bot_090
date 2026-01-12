# bot.py - ANA BAŞLANGIÇ DOSYASI
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
import os
from dotenv import load_dotenv

# ========== ÇEVRE DEĞİŞKENLERİ ==========
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== KULLANICI VERİ DOSYASI ==========
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return {}

def save_user_data(user_data):
    """Kullanıcı verilerini kaydet"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

# ========== TEMEL KOMUTLAR ==========
async def start(update, context):
    """Start komutu"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Kullanıcı verilerini yükle
    user_data = load_user_data()
    
    # Yeni kullanıcı ekle
    if user_id not in user_data:
        user_data[user_id] = {
            'first_name': user.first_name,
            'username': user.username,
            'lang': 'en',
            'joined_at': update.message.date.isoformat()
        }
        save_user_data(user_data)
        logger.info(f"New user registered: {user_id}")
    
    # Hoşgeldin mesajı
    welcome_text = (
        "🤖 **Welcome to Prompt Bot!**\n\n"
        "I'm here to help you with AI prompts and tools.\n\n"
        "📍 **Available Commands:**\n"
        "✅ /start - Start the bot\n"
        "🆘 /help - Get help\n"
        "⚙️ /settings - Admin panel (admin only)\n\n"
        "Use /help for more information!"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update, context):
    """Help komutu"""
    help_text = (
        "🤖 **Prompt Bot - Help**\n\n"
        "📍 **Main Commands:**\n"
        "✅ /start - Start the bot\n"
        "🆘 /help - This help message\n"
        "⚙️ /settings - Admin panel (admin only)\n\n"
        "📢 **Features:**\n"
        "• Multi-language support\n"
        "• Admin broadcast system\n"
        "• User management\n\n"
        "For any issues, contact the administrator."
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ========== EXTENSION YÜKLEYİCİ ==========
def load_extensions(app):
    """Extensions dosyalarını yükle"""
    extensions = ['basic', 'admin']
    
    for ext_name in extensions:
        try:
            # Extension modülünü import et
            if ext_name == 'basic':
                from extensions import basic
                basic.setup(app)
                logger.info(f"✅ Extension loaded: {ext_name}")
            elif ext_name == 'admin':
                from extensions import admin
                admin.setup(app)
                logger.info(f"✅ Extension loaded: {ext_name}")
        except ImportError as e:
            logger.error(f"❌ Failed to load extension {ext_name}: {e}")
        except Exception as e:
            logger.error(f"❌ Error in extension {ext_name}: {e}")

# ========== HATA YÖNETİCİ ==========
async def error_handler(update, context):
    """Hataları yönet"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Kullanıcıya hata mesajı gönder
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later."
            )
        except:
            pass

# ========== ANA FONKSİYON ==========
def main():
    """Bot'u başlat"""
    logger.info("Starting bot...")
    
    # Application oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Temel komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Extensions yükle
    load_extensions(application)
    
    # Hata yöneticisi
    application.add_error_handler(error_handler)
    
    # Bot'u başlat
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
