import os
import telebot
import logging

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable bulunamadı!")
    logger.info("Railway'de Settings > Variables'a BOT_TOKEN ekleyin")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "🤖 Merhaba! Bot çalışıyor!\n\nKomutlar:\n/start - Botu başlat\n/help - Yardım")
        logger.info(f"/start komutu: {message.from_user.id}")
    except Exception as e:
        logger.error(f"Hata: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"📝 Mesajınız: {message.text}\n\nSadece /start komutu aktif.")

if __name__ == '__main__':
    logger.info("Bot başlatılıyor...")
    logger.info(f"Python versiyonu: {os.sys.version}")
    
    try:
        bot_info = bot.get_me()
        logger.info(f"Bot başlatıldı: @{bot_info.username}")
        print(f"✅ Bot çalışıyor: @{bot_info.username}")
        print("📱 Telegram'da /start yazarak test edebilirsiniz")
        
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
    except Exception as e:
        logger.error(f"Bot başlatılamadı: {e}")
        print(f"❌ Hata: {e}")
