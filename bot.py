import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from config import TOKEN
from handlers import (
    start_command,
    help_command,
    language_command,
    button_handler,
    error_handler
)

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Botu başlat"""
    # Token kontrolü
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        return
    
    # Bot updater'ı oluştur
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Handler'ları ekle
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("language", language_command))
    dp.add_handler(CommandHandler("lang", language_command))
    
    # Buton handler'ını ekle
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # Hata handler'ını ekle
    dp.add_error_handler(error_handler)
    
    # Botu başlat
    print("=" * 50)
    print("🤖 MultiLanguage Bot Başlatılıyor...")
    print("📁 Modüler yapı aktif")
    print("🌍 5 dil destekli")
    print("=" * 50)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
