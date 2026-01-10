#!/usr/bin/env python3
"""
TELEGRAM BOT - PYTHON 3.13 UYUMLU
"""

import os
import sys
import asyncio

print("=" * 60)
print("🤖 BOT BAŞLIYOR - PYTHON 3.13")
print("=" * 60)

# Token kontrol
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ HATA: BOT_TOKEN YOK!")
    print("Railway Variables'a ekleyin:")
    print("Name: BOT_TOKEN")
    print("Value: BotFather token'in")
    sys.exit(1)

print(f"✅ Token: {TOKEN[:15]}...")

# Async fonksiyonlar
async def main_async():
    try:
        # Kütüphaneleri import et
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        
        print("✅ Kütüphaneler yüklendi")
        
        # Application oluştur
        app = Application.builder().token(TOKEN).build()
        
        # Komutlar
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            print(f"✅ /start: {user.first_name}")
            
            await update.message.reply_text(
                f"🎉 SELAM {user.first_name}!\n\n"
                f"✅ BOT ÇALIŞIYOR! 🚀\n"
                f"👤 ID: {user.id}\n\n"
                f"Her şey mükemmel! 🏆"
            )
        
        async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "📖 YARDIM\n\n"
                "/start - Başla\n"
                "/help - Yardım\n"
                "/test - Test\n\n"
                "🤖 Aktif!"
            )
        
        async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("✅ TEST BAŞARILI!")
        
        # Handler'ları ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("test", test))
        
        print("""
✅ BOT KURULDU!

📱 TELEGRAM TESTİ:
1. Botu aç
2. /start yaz
3. Mesaj gelmeli

🎯 Başarılı olursa kanal zorunluluğunu ekleriz.
        """)
        
        # Botu başlat
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # Sonsuz döngü
        await asyncio.Event().wait()
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        print("requirements.txt kontrol et")
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

# Ana fonksiyon
def main():
    try:
        # Async main'i çalıştır
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu")
    except Exception as e:
        print(f"❌ Kritik hata: {e}")

if __name__ == "__main__":
    main()
