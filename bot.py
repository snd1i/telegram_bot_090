#!/usr/bin/env python3
"""
TELEGRAM BOT - ÇALIŞAN VERSİYON
Sürüm: python-telegram-bot 13.15
"""

import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🤖 BOT BAŞLIYOR - SÜRÜM 13.15")
print("=" * 60)

# Token kontrol
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ HATA: BOT_TOKEN YOK!")
    print("Lütfen Railway Variables'a BOT_TOKEN ekleyin")
    print("1. Railway projen → Variables")
    print("2. New Variable: BOT_TOKEN")
    print("3. Value: BotFather token'in")
    exit()

print(f"✅ Token alındı: {TOKEN[:15]}...")

# Komutlar
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    print(f"✅ /start: {user.first_name} ({user.id})")
    
    update.message.reply_text(
        f"🎉 MERHABA {user.first_name}!\n\n"
        f"✅ BOT ÇALIŞIYOR!\n"
        f"👤 ID: {user.id}\n\n"
        f"🚀 Her şey yolunda!"
    )

def help(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📖 YARDIM\n\n"
        "/start - Botu başlat\n"
        "/help - Yardım\n"
        "/test - Test komutu\n\n"
        "🤖 Bot aktif!"
    )

def test(update: Update, context: CallbackContext):
    update.message.reply_text("✅ TEST BAŞARILI! Bot çalışıyor.")

# Ana fonksiyon
def main():
    print("🚀 Bot başlatılıyor...")
    
    try:
        # Updater oluştur (eski sürüm formatı)
        updater = Updater(TOKEN, use_context=True)
        
        # Dispatcher al
        dp = updater.dispatcher
        
        # Komutları ekle
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help))
        dp.add_handler(CommandHandler("test", test))
        
        print("""
✅ BOT KURULDU!
        
📱 TELEGRAM TESTİ:
1. Botu aç
2. /start yaz
3. Mesaj gelmeli
        
🎯 Başarılı olursa diğer özellikleri ekleriz.
        """)
        
        # Polling başlat
        updater.start_polling()
        
        # Botu çalışır tut
        updater.idle()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("⏳ 5 saniye sonra kapanıyor...")
        import time
        time.sleep(5)

if __name__ == "__main__":
    main()
