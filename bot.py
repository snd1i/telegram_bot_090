import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Basit start komutu"""
    user = update.effective_user
    await update.message.reply_text(
        f"✅ *Bot Çalışıyor!*\n\nMerhaba {user.first_name}!\n\n"
        f"Komutlar:\n/start - Bu mesaj\n/ping - Test\n/id - ID göster\n/test - Duyuru test",
        parse_mode='Markdown'
    )
    logger.info(f"Start: {user.id}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping test"""
    await update.message.reply_text("🏓 Pong! Bot aktif!")
    logger.info("Ping komutu")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ID göster"""
    user = update.effective_user
    await update.message.reply_text(
        f"👤 *Kullanıcı Bilgisi*\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Ad: {user.first_name}",
        parse_mode='Markdown'
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test duyurusu"""
    await update.message.reply_text(
        "📢 *Test Duyurusu*\n\n"
        "Bu bir test mesajıdır. Bot çalışıyor! ✅\n\n"
        "🚀 Artık duyuru sistemi kurulabilir.",
        parse_mode='Markdown'
    )

def main():
    """Ana fonksiyon"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN yok!")
        return
    
    logger.info("Bot başlatılıyor...")
    
    try:
        # Basit application
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Komutlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("ping", ping))
        app.add_handler(CommandHandler("id", get_id))
        app.add_handler(CommandHandler("test", test))
        
        # Başlat
        logger.info("Bot çalışıyor...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Hata: {e}")

if __name__ == "__main__":
    main()
