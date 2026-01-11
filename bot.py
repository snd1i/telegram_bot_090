import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from config import TOKEN
from handlers import (
    start_command,
    help_command,
    language_command,
    button_handler,
    error_handler
)
from admin import admin_command, cancel_command, handle_admin_messages

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
    
    # ========== KOMUT HANDLER'LARI ==========
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("language", language_command))
    dp.add_handler(CommandHandler("lang", language_command))
    dp.add_handler(CommandHandler("admin", admin_command))
    dp.add_handler(CommandHandler("cancel", cancel_command))  # CANCEL KOMUTU
    
    # ========== CALLBACK HANDLER ==========
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # ========== ADMIN MESAJ HANDLER ==========
    # Admin duyuru mesajlarını yakala
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command, 
        handle_admin_messages
    ))
    
    # Admin fotoğraf/video mesajlarını da yakala
    dp.add_handler(MessageHandler(
        Filters.photo | Filters.video | Filters.document,
        handle_admin_messages
    ))
    
    # ========== HATA HANDLER ==========
    dp.add_error_handler(error_handler)
    
    # ========== BOTU BAŞLAT ==========
    print("=" * 50)
    print("🤖 MultiLanguage Bot Başlatılıyor...")
    print("✅ Tüm sistemler aktif")
    print("📢 Duyuru sistemi: ÇALIŞIYOR")
    print("❌ /cancel komutu: AKTİF")
    print("🔧 Admin paneli: HAZIR")
    print("=" * 50)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
