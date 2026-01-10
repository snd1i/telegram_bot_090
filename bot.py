#!/usr/bin/env python3
"""
TELEGRAM BOT - MODERN SÜRÜM
python-telegram-bot 20.7
"""

import os
import sys
import logging

print("=" * 60)
print("🤖 BOT BAŞLIYOR - SÜRÜM 20.7")
print("=" * 60)

# Önce token kontrolü
TOKEN = os.getenv("BOT_TOKEN")
print(f"Token durumu: {'✅ VAR' if TOKEN else '❌ YOK'}")

if not TOKEN:
    print("""
❌ HATA: BOT_TOKEN YOK!

Railway'da ekle:
1. Projene git
2. Variables sekmesi
3. New Variable
4. Name: BOT_TOKEN
5. Value: BotFather token'in
    """)
    sys.exit(1)

print(f"✅ Token: {TOKEN[:15]}...")

# Gerekli kütüphaneleri import et
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    print("✅ Kütüphaneler yüklendi")
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("requirements.txt kontrol et: python-telegram-bot==20.7")
    sys.exit(1)

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Komutlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    user = update.effective_user
    print(f"📞 /start: {user.first_name}")
    
    await update.message.reply_text(
        f"🎉 MERHABA {user.first_name}!\n\n"
        f"✅ BOT ÇALIŞIYOR! 🚀\n"
        f"👤 Senin ID: {user.id}\n\n"
        f"🏆 Başarılı!"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help komutu"""
    await update.message.reply_text(
        "📖 YARDIM\n\n"
        "/start - Botu başlat\n"
        "/help - Yardım\n"
        "/ping - Bot aktif mi?\n\n"
        "🤖 Her şey yolunda!"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ping komutu"""
    await update.message.reply_text("🏓 PONG! Bot aktif ✅")

# Ana fonksiyon
def main():
    print("🚀 Bot kuruluyor...")
    
    try:
        # Application oluştur
        application = Application.builder().token(TOKEN).build()
        
        # Komutları ekle
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_cmd))
        application.add_handler(CommandHandler("ping", ping))
        
        print("""
✅ BOT HAZIR!

📱 TELEGRAM TESTİ:
1. Botu aç
2. /start yaz
3. "MERHABA" mesajı gelmeli

🎯 Başarılı!
        """)
        
        # Botu başlat
        application.run_polling(
            drop_pending_updates=True,
            timeout=30,
            pool_timeout=30
        )
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
