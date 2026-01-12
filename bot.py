import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Log ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_ID = 5541236874
USER_FILE = "kullanicilar.txt"

def kaydet(user_id):
    """Kullanıcıyı kaydet"""
    try:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")
    except Exception as e:
        logger.error(f"Kayıt hatası: {e}")

def kullanicilari_oku():
    """Tüm kullanıcıları oku"""
    try:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as f:
                return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Okuma hatası: {e}")
    return []

def start(update: Update, context: CallbackContext):
    """/start komutu"""
    user_id = str(update.effective_user.id)
    kaydet(user_id)
    update.message.reply_text("Merhaba! Ben duyuru botuyum.\n/start yazarak kayıt olabilirsin.")

def duyuru(update: Update, context: CallbackContext):
    """/duyuru komutu (sadece admin)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        update.message.reply_text("Bu komutu sadece admin kullanabilir.")
        return
    
    update.message.reply_text("Duyuru mesajınızı yazın:")
    context.user_data["duyuru_gonder"] = True

def mesaj_al(update: Update, context: CallbackContext):
    """Gelen mesajları işle"""
    user_id = update.effective_user.id
    
    # Admin duyuru gönderiyor mu?
    if user_id == ADMIN_ID and context.user_data.get("duyuru_gonder"):
        mesaj = update.message.text
        kullanicilar = kullanicilari_oku()
        
        update.message.reply_text(f"Duyuru {len(kullanicilar)} kişiye gönderiliyor...")
        
        gonderilen = 0
        for kullanici in kullanicilar:
            try:
                context.bot.send_message(
                    chat_id=int(kullanici),
                    text=f"📢 **DUYURU**\n\n{mesaj}"
                )
                gonderilen += 1
            except Exception as e:
                logger.error(f"{kullanici} gönderilemedi: {e}")
        
        context.user_data["duyuru_gonder"] = False
        update.message.reply_text(f"Duyuru tamamlandı!\nBaşarılı: {gonderilen} kişi")

def main():
    """Botu başlat"""
    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        print("HATA: BOT_TOKEN bulunamadı!")
        print("Railway'de BOT_TOKEN environment variable ekleyin")
        return
    
    # Eski sürüme uygun şekilde
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Komutlar
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("duyuru", duyuru))
    
    # Mesajlar
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, mesaj_al))
    
    print("🤖 Bot başlatılıyor...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
