#!/usr/bin/env python3
import os
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# BOT TOKEN - Railway'da ayarlayacaksın
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    """Sadece /start komutu"""
    user = update.effective_user
    
    message = f"""
✅ *Bot Çalışıyor!*

👋 Merhaba *{user.first_name}*!

🤖 Bot başarıyla çalışıyor.
    
🚀 Her şey hazır!

📅 Test Tarihi: 2024
    """
    
    update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"Yeni kullanıcı: {user.id} - {user.first_name}")

def ping(update: Update, context: CallbackContext):
    """Bot'un çalışıp çalışmadığını test et"""
    update.message.reply_text("🏓 Pong! Bot aktif!")
    logger.info("Ping komutu çalıştı")

def main():
    """Botu başlat"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı!")
        logger.info("ℹ️ Railway'da Variables kısmına BOT_TOKEN ekle")
        return
    
    logger.info("🤖 Bot başlatılıyor...")
    logger.info(f"📦 Kullanılan sürüm: python-telegram-bot==13.15")
    
    try:
        # Updater oluştur
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Komutları ekle
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("ping", ping))
        
        # Botu başlat
        updater.start_polling()
        logger.info("🚀 Bot başladı! /start ve /ping komutlarını test et")
        logger.info("✅ ParseMode sorunu çözüldü")
        
        # Botu çalışır tut
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    main()
