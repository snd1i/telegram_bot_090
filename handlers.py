import logging
from telegram import Update
from telegram.ext import CallbackContext

from config import TOKEN, CHANNEL_ID, is_admin
from database import db
from languages import get_text
from keyboards import language_keyboard, subscribe_keyboard, main_menu_keyboard

# Admin modülünü import et
from admin import admin_command, admin_callback_handler

logger = logging.getLogger(__name__)

# ========== YARDIMCI FONKSİYONLAR ==========

def detect_language(language_code):
    """Telegram dil kodundan bot dilini belirle"""
    if language_code:
        if language_code.startswith('tr'):
            return "tr"
        elif language_code.startswith('ar'):
            return "ar"
        elif language_code in ['ku', 'ckb']:
            return "ckb"
        elif language_code.startswith('en'):
            return "en"
    return "en"

def check_subscription(user_id):
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
    try:
        from telegram.ext import Updater
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot
        member = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Abonelik kontrol hatası: {e}")
        return False

# ========== KOMUT HANDLER'LARI ==========

def start_command(update: Update, context: CallbackContext):
    """Start komutu handler"""
    user = update.effective_user
    user_id = user.id
    
    # Kullanıcıyı kontrol et
    existing_user = db.get_user(user_id)
    
    if not existing_user:
        # Yeni kullanıcı - Telegram diline göre varsayılan dil
        user_data = db.create_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            language_code=user.language_code
        )
        
        # Varsayılan dilde mesaj göster
        default_lang = user_data["language"]
        update.message.reply_text(
            get_text(default_lang, "welcome"),
            reply_markup=language_keyboard()
        )
        
    else:
        # Mevcut kullanıcı
        user_data = existing_user
        
        # Kullanıcı daha önce dil seçmiş mi?
        if user_data.get("first_start") or not user_data.get("selected_language"):
            # İlk defa veya dil seçmemiş - dil seçimi göster
            db.update_user(user_id, first_start=False)
            
            update.message.reply_text(
                get_text("en", "welcome"),
                reply_markup=language_keyboard()
            )
        else:
            # Daha önce dil seçmiş - direkt hoş geldin mesajı
            lang = user_data.get("language", "en")
            update.message.reply_text(
                get_text(lang, "welcome_back", name=user.first_name),
                reply_markup=main_menu_keyboard(lang)
            )

def help_command(update: Update, context: CallbackContext):
    """Help komutu"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data and user_data.get("language"):
        lang = user_data["language"]
        update.message.reply_text(get_text(lang, "help"))
    else:
        # Kullanıcı yoksa dil seçimi göster
        start_command(update, context)

def language_command(update: Update, context: CallbackContext):
    """Language komutu - dil değiştir"""
    update.message.reply_text(
        get_text("en", "select_language"),
        reply_markup=language_keyboard()
    )

# ========== BUTON HANDLER'LARI ==========

def button_handler(update: Update, context: CallbackContext):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    # Admin callback'leri admin modülüne yönlendir
    if data.startswith(("mb_", "admin_", "format_", "stats_", "setting_", "edit_", "broadcast_")):
        if is_admin(user_id):
            admin_callback_handler(update, context)
        else:
            query.edit_message_text("❌ Bu işlemi yapma yetkiniz yok!")
        return
    
    # Dil seçimi
    if data.startswith("lang_"):
        lang_code = data.replace("lang_", "")
        
        # Kullanıcıyı güncelle
        db.update_user(user_id,
            language=lang_code,
            selected_language=True,
            first_start=False
        )
        
        # Dil seçildi mesajı
        query.edit_message_text(get_text(lang_code, "welcome_selected"))
        
        # Abonelik kontrolüne yönlendir
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(lang_code, "subscribe"),
            reply_markup=subscribe_keyboard(lang_code)
        )
    
    # Abonelik kontrolü
    elif data == "check_sub":
        user_data = db.get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(get_text(lang, "checking"))
        
        # Abonelik kontrol et
        is_subscribed = check_subscription(user_id)
        
        if is_subscribed:
            # Abone ise - ana menü göster
            db.update_user(user_id, subscribed=True)
            
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text(lang, "subscribed"),
                reply_markup=main_menu_keyboard(lang)
            )
        else:
            # Abone değilse - tekrar abone ol
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_text(lang, "not_subscribed"),
                reply_markup=subscribe_keyboard(lang)
            )
    
    # Dil değiştir
    elif data == "change_lang":
        query.edit_message_text(
            get_text("en", "select_language"),
            reply_markup=language_keyboard()
        )
    
    # Yardım göster
    elif data == "show_help":
        user_data = db.get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(
            get_text(lang, "help"),
            reply_markup=main_menu_keyboard(lang)
        )
    
    # Ana menü
    elif data == "main_menu":
        user_data = db.get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(
            get_text(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )

def error_handler(update: Update, context: CallbackContext):
    """Hataları işle"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Kullanıcıya hata mesajı gönder
    if update and update.effective_user:
        try:
            user_id = update.effective_user.id
            user_data = db.get_user(user_id)
            lang = user_data.get("language", "en") if user_data else "en"
            
            update.effective_message.reply_text(get_text(lang, "error"))
        except:
            pass
