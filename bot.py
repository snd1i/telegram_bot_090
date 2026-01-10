import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Log ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token (Railway'dan alınacak)
TOKEN = os.getenv("TOKEN", "")

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot çalışıyor! /start komutu çalıştı.")

# Ana fonksiyon
def main():
    # Token kontrolü
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        print("Railway'da TOKEN değişkenini ekleyin")
        return
    
    # Bot uygulamasını oluştur
    app = Application.builder().token(TOKEN).build()
    
    # Sadece /start komutu ekleyelim
    app.add_handler(CommandHandler("start", start))
    
    # Botu başlat
    print("🤖 TEST BOTU BAŞLATILIYOR...")
    print(f"Token: {TOKEN[:10]}...")
    
    try:
        app.run_polling()
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()
