#!/usr/bin/env python3
"""
BASİT TELEGRAM BOT TEST
"""

import os
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

print("=" * 50)
print("🤖 BOT TEST SÜRÜM 1.0")
print("=" * 50)

# Token kontrolü
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ HATA: BOT_TOKEN bulunamadı!")
    print("Railway'da Variables'a ekleyin:")
    print("1. Railway projene git")
    print("2. Variables sekmesi")
    print("3. New Variable: BOT_TOKEN")
    print("4. Value: BotFather token'in")
    time.sleep(10)
    exit()

print(f"✅ Token alındı")
print("⏳ 3 saniye bekle...")
time.sleep(3)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"✅ /start komutu: {user.first_name}")
    
    await update.message.reply_text(
        f"🎉 SELAM {user.first_name}!\n\n"
        f"✅ Bot ÇALIŞIYOR!\n"
        f"👤 Senin ID: {user.id}\n\n"
        f"Bir sorun yok, her şey yolunda! 🚀"
    )

# /help komutu
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ YARDIM\n\n"
        "/start - Botu başlat\n"
        "/help - Bu mesajı göster\n"
        "/ping - Bot aktif mi?\n\n"
        "🎯 Test başarılı!"
    )

# /ping komutu
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 PONG! Bot aktif! ✅")

# Ana program
def main():
    print("🚀 Bot başlatılıyor...")
    
    try:
        # Bot uygulaması
        app = Application.builder().token(TOKEN).build()
        
        # Komutları ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("ping", ping))
        
        print("""
✅ BOT HAZIR!
        
📱 TELEGRAM'DA TEST ET:
1. Botunu aç
2. /start yaz
3. Mesaj gelmeli
        
🎯 Eğer çalışırsa sırayla diğer özellikleri ekleriz.
        """)
        
        # Botu başlat
        app.run_polling(
            drop_pending_updates=True,
            timeout=30
        )
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        print("⏳ 10 saniye sonra kapanıyor...")
        time.sleep(10)

if __name__ == "__main__":
    main()
