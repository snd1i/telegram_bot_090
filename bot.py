# bot.py - ESKİ ÇALIŞAN VERSİYONUNUZ
import logging
from telegram.ext import Application
from extensions.basic import setup as basic_setup
from extensions.admin import setup as admin_setup

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token (Railway'dan gelecek)
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    """Bot'u başlat"""
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN environment variable not set!")
        return
    
    # Application oluştur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Extensions yükle
    basic_setup(app)
    admin_setup(app)
    
    # Bot'u başlat
    logging.info("Bot başlatılıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
