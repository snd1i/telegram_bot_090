#!/usr/bin/env python3
import os
import logging

# Bot token'ı al
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ HATA: BOT_TOKEN bulunamadı!")
    print("Railway'da Variables kısmına BOT_TOKEN ekleyin")
    exit(1)

# Telegram modüllerini import et
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    print("✅ Telegram modülleri yüklendi")
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("requirements.txt kontrol edin")
    exit(1)

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sadece /start komutu"""
    user = update.effective_user
    
    message = f"""
🎉 *TELEGRAM BOT ÇALIŞIYOR!*

👤 Merhaba *{user.first_name}*

✅ Bot aktif ve çalışıyor
📱 Telegram Bot API: v20.7
🚀 Railway Hosting: Aktif
💯 Her şey hazır!

Komutlar:
/start - Bu mesajı gösterir
/ping - Bot aktif mi kontrol et
/id - Kullanıcı ID'ni göster
    """
    
    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"✅ /start komutu: {user.id} - {user.first_name}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot aktif mi kontrol et"""
    await update.message.reply_text("🏓 *Pong! Bot aktif ve çalışıyor!*", parse_mode='Markdown')
    logger.info("🏓 Ping komutu çalıştı")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcı ID'sini göster"""
    user = update.effective_user
    await update.message.reply_text(
        f"👤 *Kullanıcı Bilgileri*\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👤 Ad: {user.first_name}\n"
        f"📛 Kullanıcı ad: @{user.username if user.username else 'yok'}\n"
        f"📞 Premium: {'Evet' if user.is_premium else 'Hayır'}",
        parse_mode='Markdown'
    )
    logger.info(f"🆔 ID komutu: {user.id}")

async def test_duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test duyurusu gönder"""
    user = update.effective_user
    
    # Sadece yönetici için (ID'ni buraya yaz)
    YONETICI_ID = 123456789  # ⚠️ KENDİ ID'Nİ YAZ!
    
    if user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Yetkiniz yok!")
        return
    
    test_msg = "📢 *TEST DUYURUSU*\n\nBu bir test duyurusudur. Bot çalışıyor! ✅"
    
    try:
        # Kendine test mesajı gönder
        await update.message.reply_text(test_msg, parse_mode='Markdown')
        await update.message.reply_text(
            "✅ *Duyuru sistemi hazır!*\n\n"
            "Artık duyuru botunu kurabiliriz. Şimdi kullanıcı kaydı ve duyuru gönderme özelliklerini ekleyelim.",
            parse_mode='Markdown'
        )
        logger.info("✅ Test duyurusu gönderildi")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")
        logger.error(f"Test duyurusu hatası: {e}")

def main():
    """Botu başlat"""
    logger.info("🤖 BOT BAŞLATILIYOR...")
    logger.info(f"🔑 Token: {'***' + BOT_TOKEN[-5:] if BOT_TOKEN else 'YOK'}")
    
    try:
        # Application oluştur
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Komutları ekle
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("ping", ping))
        application.add_handler(CommandHandler("id", get_id))
        application.add_handler(CommandHandler("test", test_duyuru))
        
        # Botu başlat
        logger.info("🚀 Bot polling başlatılıyor...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ BOT BAŞLATMA HATASI: {str(e)}")
        print(f"\n❌ HATA DETAYI: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 TELEGRAM BOT BAŞLATILIYOR")
    print("=" * 50)
    main()
