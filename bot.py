#!/usr/bin/env python3
"""
TELEGRAM BOT - KESİN ÇALIŞAN SÜRÜM
python-telegram-bot 13.15
"""

import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

print("=" * 60)
print("🤖 BOT BAŞLIYOR - SÜRÜM 13.15")
print("=" * 60)

# Token kontrol
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ HATA: BOT_TOKEN YOK!")
    print("Railway Variables'a ekleyin:")
    print("Name: BOT_TOKEN")
    print("Value: BotFather'dan aldığınız token")
    exit()

print(f"✅ Token: {TOKEN[:15]}...")

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Komut fonksiyonları
def start(update: Update, context: CallbackContext):
    """Kullanıcı /start yazdığında"""
    user = update.effective_user
    print(f"📞 /start komutu: {user.first_name}")
    
    update.message.reply_text(
        f"🎉 MERHABA {user.first_name}!\n\n"
        f"✅ BOT ÇALIŞIYOR! 🚀\n"
        f"👤 Senin ID: {user.id}\n\n"
        f"🏆 Başarılı!"
    )

def help_command(update: Update, context: CallbackContext):
    """/help komutu"""
    update.message.reply_text(
        "📖 YARDIM\n\n"
        "/start - Botu başlat\n"
        "/help - Yardım mesajı\n"
        "/ping - Bot aktif mi?\n\n"
        "🤖 Her şey yolunda!"
    )

def ping(update: Update, context: CallbackContext):
    """/ping komutu"""
    update.message.reply_text("🏓 PONG! Bot aktif ✅")

# Ana fonksiyon
def main():
    print("🚀 Bot başlatılıyor...")
    
    try:
        # Updater oluştur (13.15 sürümüne uygun)
        updater = Updater(TOKEN, use_context=True)
        
        # Dispatcher al
        dp = updater.dispatcher
        
        # Komutları ekle
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("ping", ping))
        
        print("""
✅ BOT HAZIR!

📱 TELEGRAM TESTİ:
1. Botunu aç
2. /start yaz
3. "MERHABA" mesajı gelmeli

🎯 Eğer çalışırsa kanal zorunluluğunu ekleriz.
        """)
        
        # Botu başlat
        updater.start_polling()
        
        # Botu çalışır tut
        updater.idle()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        print("⏳ 10 saniye sonra kapanıyor...")
        import time
        time.sleep(10)

if __name__ == "__main__":
    main()
