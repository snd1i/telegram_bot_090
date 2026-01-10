import os
import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)

# Kendi dosyalarımızı import ediyoruz
from config import TOKEN, CHANNEL_ID
from languages import get_text
from keyboards import language_keyboard, subscribe_keyboard

# Log ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basit kullanıcı veritabanı (hafızada)
users_db = {}

def check_subscription(user_id):
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
    try:
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot
        member = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Abonelik kontrol hatası: {e}")
        return False

def start(update: Update, context: CallbackContext):
    """/start komutu"""
    user = update.effective_user
    user_id = user.id
    
    # Kullanıcıyı kaydet
    if user_id not in users_db:
        users_db[user_id] = {
            "language": None,
            "selected": False,
            "subscribed": False
        }
    
    # İlk defa mı geliyor?
    user_data = users_db[user_id]
    
    if not user_data["selected"]:
        # İlk defa - dil seçimi göster
        update.message.reply_text(
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )
    else:
        # Daha önce gelmiş - ana menü
        lang = user_data["language"] or "en"
        update.message.reply_text(
            get_text(lang, "main_menu"),
            reply_markup=language_keyboard()
        )

def button_handler(update: Update, context: CallbackContext):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    # Dil seçimi
    if data.startswith("lang_"):
        lang_code = data.replace("lang_", "")
        
        # Kullanıcıyı güncelle
        if user_id in users_db:
            users_db[user_id]["language"] = lang_code
            users_db[user_id]["selected"] = True
        
        # Dil seçildi mesajı
        query.edit_message_text(get_text(lang_code, "welcome_selected"))
        
        # Abonelik kontrolüne yönlendir
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(lang_code, "subscribe"),
            reply_markup=subscribe_keyboard(lang_code)
        )
    
    # Abonelik kontrolü
    elif data == "check_subscription":
        user_data = users_db.get(user_id, {})
        lang = user_data.get("language", "en")
        
        query.edit_message_text(get_text(lang, "checking"))
        
        # Abonelik kontrol et
        is_subscribed = check_subscription(user_id)
        
        if is_subscribed:
            # Abone ise
            if user_id in users_db:
                users_db[user_id]["subscribed"] = True
            
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text(lang, "subscribed")
            )
        else:
            # Abone değilse
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text(lang, "not_subscribed"),
                reply_markup=subscribe_keyboard(lang)
            )

def help_command(update: Update, context: CallbackContext):
    """/help komutu"""
    user_id = update.effective_user.id
    user_data = users_db.get(user_id, {})
    lang = user_data.get("language", "en")
    
    update.message.reply_text(get_text(lang, "help"))

def main():
    """Botu başlat"""
    # Token kontrolü
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        return
    
    # Bot updater'ı oluştur
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Handler'ları ekle
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    # Botu başlat
    print("🤖 Bot başlatılıyor...")
    print(f"🌍 Diller: Türkçe, İngilizce, Arapça, Kürtçe (Sorani/Badini)")
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
