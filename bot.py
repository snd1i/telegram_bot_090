import logging
from telegram import Update
from telegram.ext import (
    Updater,  # 13.x sürümünde Updater kullanılıyor
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

# Kendi dosyalarımızı import ediyoruz
from config import TOKEN, BOT_NAME, BOT_VERSION, CHANNEL_ID
from database import db
from languages import get_text
from keyboards import (
    language_keyboard,
    subscribe_keyboard,
    main_menu_keyboard,
    back_to_menu_keyboard
)

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== YARDIMCI FONKSİYONLAR ==========

def check_subscription(user_id: int, context: CallbackContext) -> bool:
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
    try:
        member = context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )
        # Kullanıcı abone mi?
        if member.status in ["member", "administrator", "creator"]:
            db.set_subscribed(user_id, True)
            return True
        else:
            db.set_subscribed(user_id, False)
            return False
    except Exception as e:
        logger.error(f"Abonelik kontrol hatası: {e}")
        return False

def get_user_language(user_id: int) -> str:
    """Kullanıcının dilini al"""
    user = db.get_user(user_id)
    if user and user.get("language"):
        return user["language"]
    return "en"  # Varsayılan İngilizce

# ========== KOMUT HANDLER'LARI ==========

def start_command(update: Update, context: CallbackContext):
    """/start komutu handler"""
    user = update.effective_user
    user_id = user.id
    
    # Kullanıcıyı veritabanına ekle veya getir
    existing_user = db.get_user(user_id)
    
    if not existing_user:
        # Yeni kullanıcı - veritabanına ekle
        db.create_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        first_start = True
    else:
        first_start = existing_user.get("first_start", True)
    
    # Kullanıcı daha önce dil seçmiş mi?
    user_data = db.get_user(user_id)
    
    if first_start or not user_data.get("selected_language"):
        # İlk defa veya dil seçmemiş - dil seçimi göster
        db.set_first_start(user_id, False)
        update.message.reply_text(
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )
    else:
        # Daha önce dil seçmiş - direkt hoş geldin mesajı
        lang = get_user_language(user_id)
        update.message.reply_text(
            get_text(lang, "welcome_back", name=user.first_name),
            reply_markup=main_menu_keyboard(lang)
        )

def help_command(update: Update, context: CallbackContext):
    """/help komutu handler"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    update.message.reply_text(
        get_text(lang, "help"),
        reply_markup=back_to_menu_keyboard(lang)
    )

def language_command(update: Update, context: CallbackContext):
    """/language komutu - dil değiştirme"""
    update.message.reply_text(
        get_text("en", "select_language"),
        reply_markup=language_keyboard()
    )

def info_command(update: Update, context: CallbackContext):
    """/info komutu - bot bilgileri"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    update.message.reply_text(
        get_text(lang, "bot_info", name=BOT_NAME, version=BOT_VERSION),
        reply_markup=back_to_menu_keyboard(lang)
    )

# ========== CALLBACK QUERY HANDLER ==========

def button_handler(update: Update, context: CallbackContext):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    query.answer()  # Callback query'yi cevapla
    
    user_id = update.effective_user.id
    data = query.data
    
    # Dil seçimi butonları
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]  # lang_tr -> tr, lang_ckb -> ckb
        
        # Kullanıcının dilini kaydet
        db.set_language(user_id, lang_code)
        
        # Dil seçildi mesajını gönder
        query.edit_message_text(
            get_text(lang_code, "welcome_selected")
        )
        
        # Şimdi abonelik kontrolüne yönlendir
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(lang_code, "subscribe"),
            reply_markup=subscribe_keyboard(lang_code)
        )
    
    # Abonelik kontrol butonu
    elif data == "check_subscription":
        lang = get_user_language(user_id)
        
        query.edit_message_text(
            get_text(lang, "checking")
        )
        
        # Abonelik kontrolü yap
        is_subscribed = check_subscription(user_id, context)
        
        if is_subscribed:
            # Abone ise ana menüye yönlendir
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text(lang, "subscription_success"),
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            # Abone değilse tekrar abone olmasını iste
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text(lang, "not_subscribed"),
                reply_markup=subscribe_keyboard(lang)
            )
    
    # Ana menü butonu
    elif data == "main_menu":
        lang = get_user_language(user_id)
        query.edit_message_text(
            get_text(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )
    
    # Dil değiştir butonu
    elif data == "change_language":
        query.edit_message_text(
            get_text("en", "select_language"),
            reply_markup=language_keyboard()
        )
    
    # Bot bilgileri butonu
    elif data == "bot_info":
        lang = get_user_language(user_id)
        query.edit_message_text(
            get_text(lang, "bot_info", name=BOT_NAME, version=BOT_VERSION),
            reply_markup=back_to_menu_keyboard(lang)
        )
    
    # Yardım butonu
    elif data == "help":
        lang = get_user_language(user_id)
        query.edit_message_text(
            get_text(lang, "help"),
            reply_markup=back_to_menu_keyboard(lang)
        )

# ========== MESAJ HANDLER ==========

def handle_message(update: Update, context: CallbackContext):
    """Normal mesajları işle"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    # Kullanıcının abone olup olmadığını kontrol et
    is_subscribed = check_subscription(user_id, context)
    
    if not is_subscribed:
        # Abone değilse abone olmasını iste
        update.message.reply_text(
            get_text(lang, "not_subscribed"),
            reply_markup=subscribe_keyboard(lang)
        )
        return
    
    # Abone ise normal işlemler
    user_message = update.message.text
    
    # Basit echo yap
    update.message.reply_text(
        f"{get_text(lang, 'main_menu')}\n\n"
        f"Sen: {user_message}\n\n"
        f"Komutlar: /start /help /language /info",
        reply_markup=main_menu_keyboard(lang)
    )

# ========== HATA HANDLER ==========

def error_handler(update: Update, context: CallbackContext):
    """Hataları işle"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Kullanıcıya hata mesajı gönder
    if update and update.effective_user:
        try:
            lang = get_user_language(update.effective_user.id)
            update.effective_message.reply_text(
                get_text(lang, "error"),
                reply_markup=main_menu_keyboard(lang)
            )
        except:
            pass

# ========== ANA FONKSİYON ==========

def main():
    """Botu başlat"""
    # Token kontrolü
    if not TOKEN:
        logger.error("❌ HATA: TOKEN bulunamadı!")
        print("=" * 50)
        print("❌ HATA: TOKEN bulunamadı!")
        print("Lütfen Railway'da TOKEN variable ekleyin:")
        print("Name: TOKEN")
        print("Value: BotFather'dan aldığınız token")
        print("=" * 50)
        return
    
    try:
        # Bot updater'ı oluştur - 13.x sürümü için
        updater = Updater(TOKEN, use_context=True)
        
        # Dispatcher'ı al
        dp = updater.dispatcher
        
        # Komut handler'larını ekle
        dp.add_handler(CommandHandler("start", start_command))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("language", language_command))
        dp.add_handler(CommandHandler("info", info_command))
        dp.add_handler(CommandHandler("lang", language_command))
        
        # Callback query handler ekle (buton tıklamaları)
        dp.add_handler(CallbackQueryHandler(button_handler))
        
        # Mesaj handler ekle
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        # Hata handler ekle
        dp.add_error_handler(error_handler)
        
        # Botu başlat
        logger.info("🤖 Bot başlatılıyor...")
        print("=" * 50)
        print("🤖 MultiLanguage Bot Başlatılıyor...")
        print(f"📊 Kayıtlı kullanıcı sayısı: {len(db.users)}")
        print(f"🌍 Desteklenen diller: Türkçe, İngilizce, Arapça, Kürtçe (Sorani/Badini)")
        print(f"🔑 Token: {TOKEN[:10]}...{TOKEN[-10:] if len(TOKEN) > 20 else ''}")
        print(f"📦 python-telegram-bot sürümü: 13.15 (stabil)")
        print("=" * 50)
        
        # Botu başlat
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"Bot başlatılırken hata: {e}")
        print(f"❌ Bot başlatılırken hata: {type(e).__name__}: {e}")
        print("\n⚠️  Olası sorunlar:")
        print("1. Token yanlış olabilir")
        print("2. Internet bağlantısı sorunu")

if __name__ == "__main__":
    main()
