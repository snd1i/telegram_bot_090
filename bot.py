import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
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

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
    try:
        member = await context.bot.get_chat_member(
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )
    else:
        # Daha önce dil seçmiş - direkt hoş geldin mesajı
        lang = get_user_language(user_id)
        await update.message.reply_text(
            get_text(lang, "welcome_back", name=user.first_name),
            reply_markup=main_menu_keyboard(lang)
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help komutu handler"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    await update.message.reply_text(
        get_text(lang, "help"),
        reply_markup=back_to_menu_keyboard(lang)
    )

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/language komutu - dil değiştirme"""
    await update.message.reply_text(
        get_text("en", "select_language"),
        reply_markup=language_keyboard()
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/info komutu - bot bilgileri"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    await update.message.reply_text(
        get_text(lang, "bot_info", name=BOT_NAME, version=BOT_VERSION),
        reply_markup=back_to_menu_keyboard(lang)
    )

# ========== CALLBACK QUERY HANDLER ==========

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()  # Callback query'yi cevapla
    
    user_id = update.effective_user.id
    data = query.data
    
    # Dil seçimi butonları
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]  # lang_tr -> tr, lang_ckb -> ckb
        
        # Kullanıcının dilini kaydet
        db.set_language(user_id, lang_code)
        
        # Dil seçildi mesajını gönder
        await query.edit_message_text(
            get_text(lang_code, "welcome_selected")
        )
        
        # Şimdi abonelik kontrolüne yönlendir
        await query.message.reply_text(
            get_text(lang_code, "subscribe"),
            reply_markup=subscribe_keyboard(lang_code)
        )
    
    # Abonelik kontrol butonu
    elif data == "check_subscription":
        lang = get_user_language(user_id)
        
        await query.edit_message_text(
            get_text(lang, "checking")
        )
        
        # Abonelik kontrolü yap
        is_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            # Abone ise ana menüye yönlendir
            await query.message.reply_text(
                get_text(lang, "subscription_success"),
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            # Abone değilse tekrar abone olmasını iste
            await query.message.reply_text(
                get_text(lang, "not_subscribed"),
                reply_markup=subscribe_keyboard(lang)
            )
    
    # Ana menü butonu
    elif data == "main_menu":
        lang = get_user_language(user_id)
        await query.edit_message_text(
            get_text(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )
    
    # Dil değiştir butonu
    elif data == "change_language":
        await query.edit_message_text(
            get_text("en", "select_language"),
            reply_markup=language_keyboard()
        )
    
    # Bot bilgileri butonu
    elif data == "bot_info":
        lang = get_user_language(user_id)
        await query.edit_message_text(
            get_text(lang, "bot_info", name=BOT_NAME, version=BOT_VERSION),
            reply_markup=back_to_menu_keyboard(lang)
        )
    
    # Yardım butonu
    elif data == "help":
        lang = get_user_language(user_id)
        await query.edit_message_text(
            get_text(lang, "help"),
            reply_markup=back_to_menu_keyboard(lang)
        )

# ========== MESAJ HANDLER ==========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Normal mesajları işle"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    # Kullanıcının abone olup olmadığını kontrol et
    is_subscribed = await check_subscription(user_id, context)
    
    if not is_subscribed:
        # Abone değilse abone olmasını iste
        await update.message.reply_text(
            get_text(lang, "not_subscribed"),
            reply_markup=subscribe_keyboard(lang)
        )
        return
    
    # Abone ise normal işlemler
    user_message = update.message.text
    
    # Basit echo yap
    await update.message.reply_text(
        f"{get_text(lang, 'main_menu')}\n\n"
        f"Sen: {user_message}\n\n"
        f"Komutlar: /start /help /language /info",
        reply_markup=main_menu_keyboard(lang)
    )

# ========== HATA HANDLER ==========

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hataları işle"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Kullanıcıya hata mesajı gönder
    if update and update.effective_user:
        try:
            lang = get_user_language(update.effective_user.id)
            await update.effective_message.reply_text(
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
        # Bot uygulamasını oluştur - DÜZELTİLDİ
        app = Application.builder().token(TOKEN).build()
        
        # Komut handler'larını ekle
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("language", language_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(CommandHandler("lang", language_command))
        
        # Callback query handler ekle (buton tıklamaları)
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # Mesaj handler ekle
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Hata handler ekle
        app.add_error_handler(error_handler)
        
        # Botu başlat
        logger.info("🤖 Bot başlatılıyor...")
        print("=" * 50)
        print("🤖 MultiLanguage Bot Başlatılıyor...")
        print(f"📊 Kayıtlı kullanıcı sayısı: {len(db.users)}")
        print(f"🌍 Desteklenen diller: Türkçe, İngilizce, Arapça, Kürtçe (Sorani/Badini)")
        print(f"🔑 Token: {TOKEN[:10]}...{TOKEN[-10:] if len(TOKEN) > 20 else ''}")
        print("=" * 50)
        
        # Polling'i başlat
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Bot başlatılırken hata: {e}")
        print(f"❌ Bot başlatılırken hata: {type(e).__name__}: {e}")
        print("\n⚠️  Olası sorunlar:")
        print("1. Token yanlış olabilir")
        print("2. python-telegram-bot sürümü uyumsuz")
        print("3. Railway'da internet bağlantısı sorunu")

if __name__ == "__main__":
    main()
