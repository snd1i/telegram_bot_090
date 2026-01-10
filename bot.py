import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Log ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token (Railway'dan alınacak)
TOKEN = os.getenv("TOKEN", "")

# /start komutu
def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ TEST: Bot çalışıyor! /start komutu başarılı.")

# Ana fonksiyon
def main():
    # Token kontrolü
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        print("Railway'da TOKEN değişkenini ekleyin")
        return
    
    # Bot updater'ı oluştur (13.15 sürümü için)
    updater = Updater(TOKEN, use_context=True)
    
    # Dispatcher'ı al
    dp = updater.dispatcher
    
    # Sadece /start komutu ekleyelim
    dp.add_handler(CommandHandler("start", start))
    
    # Botu başlat
    print("🤖 TEST BOTU BAŞLATILIYOR (Python 3.11)...")
    print(f"Token: {TOKEN[:10]}...")
    print("python-telegram-bot sürümü: 13.15")
    
    try:
        updater.start_polling()
        print("✅ Bot başarıyla başlatıldı!")
        updater.idle()
    except Exception as e:
        print(f"❌ Hata: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
