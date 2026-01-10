#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

# ========== KONFİGÜRASYON ==========
TOKEN = os.getenv("TOKEN", "")
CHANNEL_ID = -1002072605977  # Kanal ID'niz
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"

# ========== VERİTABANI (Basit JSON) ==========
DB_FILE = "users.json"

def load_users():
    """Kullanıcıları yükle"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users():
    """Kullanıcıları kaydet"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, indent=2, ensure_ascii=False)
    except:
        pass

users_db = load_users()

def get_user(user_id):
    """Kullanıcıyı getir"""
    return users_db.get(str(user_id))

def save_user(user_id, data):
    """Kullanıcıyı kaydet"""
    users_db[str(user_id)] = data
    save_users()

# ========== DİL SİSTEMİ ==========
LANGUAGES = {
    "ckb": {
        "name": "Kürtçe Sorani",
        "flag": "🇹🇯",
        "welcome": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "welcome_selected": "🇹🇯 بەخێربێیت! زمانی کوردی سۆرانی هەڵبژێردرا.",
        "subscribe": "📢 تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوام بوون:",
        "not_subscribed": "❌ تۆ سەبسکرایبی کەناڵەکەت نەکردووە. تکایە سەبسکرایب بکە.",
        "checking": "⏳ سەبسکرایب چێک دەکرێت...",
        "check_again": "🔍 دووبارە چێک بکە",
        "subscribed": "✅ تۆ سەبسکرایبی کەناڵەکەیت کردووە! دەتوانی بەردەوام ببی.",
        "main_menu": "🏠 مێنیوی سەرەکی",
        "start": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "help": "📖 یارمەتی\n\nئەمە بۆتێکی تێلیگرامی فرە زمانەیە.\n\nفەرمانەکان:\n/start - دەستپێکردنی بۆت\n/help - پەیامی یارمەتی\n/language - گۆڕینی زمان\n/info - زانیاری بۆت",
    },
    "badini": {
        "name": "Kürtçe Badini",
        "flag": "🇹🇯",
        "welcome": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "welcome_selected": "🇹🇯 Bi xêr hatî! Zimanê Kurdî Badînî hate hilbijartin.",
        "subscribe": "📢 Ji bo domandinê ji kerema xwe li kanalê abone bibin:",
        "not_subscribed": "❌ Te li kanalê abone nebûye. Ji kerema xwe pêşî abone bibin.",
        "checking": "⏳ Aboneyî tê kontrolkirin...",
        "check_again": "🔍 Dîsa Kontrol Bike",
        "subscribed": "✅ Te berê abone bûye! Tu dikarî bidomînî.",
        "main_menu": "🏠 Meniya Sereke",
        "start": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "help": "📖 Alîkarî\n\nEv botekî Telegrama pirzimanî ye.\n\nFerman:\n/start - Destpêkirina bot\n/help - Peyama alîkariyê\n/language - Guherandina ziman\n/info - Agahiyên bot",
    },
    "tr": {
        "name": "Türkçe",
        "flag": "🇹🇷",
        "welcome": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "welcome_selected": "🇹🇷 Hoş geldiniz! Dil olarak Türkçe seçildi.",
        "subscribe": "📢 Devam etmek için lütfen kanala abone olun:",
        "not_subscribed": "❌ Kanala abone olmadınız. Lütfen önce abone olun.",
        "checking": "⏳ Abonelik kontrol ediliyor...",
        "check_again": "🔍 Tekrar Kontrol Et",
        "subscribed": "✅ Zaten abonesiniz! Devam edebilirsiniz.",
        "main_menu": "🏠 Ana Menü",
        "start": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "help": "📖 Yardım\n\nBu çok dilli bir Telegram botudur.\n\nKomutlar:\n/start - Botu başlat\n/help - Yardım mesajı\n/language - Dil değiştir\n/info - Bot bilgileri",
    },
    "en": {
        "name": "English",
        "flag": "🇬🇧",
        "welcome": "🤖 Welcome! Please select your language:",
        "welcome_selected": "🇬🇧 Welcome! English has been selected as language.",
        "subscribe": "📢 Please subscribe to the channel to continue:",
        "not_subscribed": "❌ You are not subscribed to the channel. Please subscribe first.",
        "checking": "⏳ Checking subscription...",
        "check_again": "🔍 Check Again",
        "subscribed": "✅ You are already subscribed! You can continue.",
        "main_menu": "🏠 Main Menu",
        "start": "🤖 Welcome! Please select your language:",
        "help": "📖 Help\n\nThis is a multi-language Telegram bot.\n\nCommands:\n/start - Start the bot\n/help - Help message\n/language - Change language\n/info - Bot information",
    },
    "ar": {
        "name": "العربية",
        "flag": "🇮🇶",
        "welcome": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "welcome_selected": "🇮🇶 أهلاً بك! تم اختيار العربية كلغة.",
        "subscribe": "📢 يرجى الاشتراك في القناة للمتابعة:",
        "not_subscribed": "❌ لم تشترك في القناة. يرجى الاشتراك أولاً.",
        "checking": "⏳ جاري التحقق من الاشتراك...",
        "check_again": "🔍 تحقق مرة أخرى",
        "subscribed": "✅ أنت مشترك بالفعل! يمكنك المتابعة.",
        "main_menu": "🏠 القائمة الرئيسية",
        "start": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "help": "📖 مساعدة\n\nهذا بوت تيليجرام متعدد اللغات.\n\nالأوامر:\n/start - بدء البوت\n/help - رسالة المساعدة\n/language - تغيير اللغة\n/info - معلومات البوت",
    }
}

def get_text(lang, key):
    """Dil metnini getir"""
    if lang in LANGUAGES and key in LANGUAGES[lang]:
        return LANGUAGES[lang][key]
    return LANGUAGES["en"][key]  # Varsayılan İngilizce

# ========== BUTONLAR ==========
def language_keyboard():
    """Dil seçim butonları"""
    keyboard = [
        [
            InlineKeyboardButton("Kürtçe Sorani 🇹🇯", callback_data="lang_ckb"),
            InlineKeyboardButton("Kürtçe Badini 🇹🇯", callback_data="lang_badini"),
        ],
        [
            InlineKeyboardButton("Türkçe 🇹🇷", callback_data="lang_tr"),
            InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton("العربية 🇮🇶", callback_data="lang_ar"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def subscribe_keyboard(lang="en"):
    """Abone ol butonları"""
    keyboard = [
        [
            InlineKeyboardButton(get_text(lang, "subscribe"), url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(get_text(lang, "check_again"), callback_data="check_sub")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(lang="en"):
    """Ana menü butonları"""
    keyboard = [
        [
            InlineKeyboardButton("🌍 Dil Değiştir", callback_data="change_lang"),
            InlineKeyboardButton("📖 Yardım", callback_data="show_help"),
        ],
        [
            InlineKeyboardButton("ℹ️ Bot Bilgisi", callback_data="bot_info"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== YARDIMCI FONKSİYONLAR ==========
def check_subscription(user_id):
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
    try:
        from telegram.error import BadRequest
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot
        
        member = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Abonelik kontrol hatası: {e}")
        return False

# ========== HANDLER'LAR ==========
def start(update: Update, context: CallbackContext):
    """Start komutu handler"""
    user = update.effective_user
    user_id = user.id
    
    # Kullanıcıyı kontrol et
    user_data = get_user(user_id)
    
    if not user_data:
        # Yeni kullanıcı - dil seçimi göster
        save_user(user_id, {
            "id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "language": None,
            "selected_language": False,
            "subscribed": False,
            "first_start": True,
            "created_at": datetime.now().isoformat()
        })
        
        update.message.reply_text(
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )
    else:
        # Mevcut kullanıcı
        if user_data.get("first_start") or not user_data.get("selected_language"):
            # İlk defa veya dil seçmemiş
            user_data["first_start"] = False
            save_user(user_id, user_data)
            
            update.message.reply_text(
                get_text("en", "welcome"),
                reply_markup=language_keyboard()
            )
        else:
            # Dil seçmiş - direkt ana menü
            lang = user_data.get("language", "en")
            update.message.reply_text(
                get_text(lang, "main_menu"),
                reply_markup=main_menu_keyboard(lang)
            )

def button_handler(update: Update, context: CallbackContext):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    # Dil seçimi
    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        
        # Kullanıcıyı güncelle
        user_data = get_user(user_id)
        if user_data:
            user_data["language"] = lang
            user_data["selected_language"] = True
            save_user(user_id, user_data)
        
        # Dil seçildi mesajı
        query.edit_message_text(get_text(lang, "welcome_selected"))
        
        # Abonelik kontrolüne yönlendir
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(lang, "subscribe"),
            reply_markup=subscribe_keyboard(lang)
        )
    
    # Abonelik kontrolü
    elif data == "check_sub":
        user_data = get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(get_text(lang, "checking"))
        
        # Abonelik kontrol et
        is_subscribed = check_subscription(user_id)
        
        if is_subscribed:
            # Abone ise - ana menü göster
            if user_data:
                user_data["subscribed"] = True
                save_user(user_id, user_data)
            
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
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )
    
    # Yardım
    elif data == "show_help":
        user_data = get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(
            get_text(lang, "help"),
            reply_markup=main_menu_keyboard(lang)
        )
    
    # Bot bilgisi
    elif data == "bot_info":
        user_data = get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        bot_info = f"🤖 Bot Bilgileri\n\n"
        bot_info += f"Toplam Kullanıcı: {len(users_db)}\n"
        bot_info += f"Diliniz: {get_text(lang, 'name')}\n"
        bot_info += f"Kanal: @KurdceBotlar"
        
        query.edit_message_text(
            bot_info,
            reply_markup=main_menu_keyboard(lang)
        )

def help_command(update: Update, context: CallbackContext):
    """Help komutu"""
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data and user_data.get("language"):
        lang = user_data["language"]
        update.message.reply_text(get_text(lang, "help"))
    else:
        update.message.reply_text(
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )

def language_command(update: Update, context: CallbackContext):
    """Language komutu - dil değiştir"""
    update.message.reply_text(
        get_text("en", "welcome"),
        reply_markup=language_keyboard()
    )

def handle_message(update: Update, context: CallbackContext):
    """Normal mesajları işle"""
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if not user_data or not user_data.get("selected_language"):
        update.message.reply_text(
            get_text("en", "welcome"),
            reply_markup=language_keyboard()
        )
        return
    
    lang = user_data.get("language", "en")
    
    # Abonelik kontrolü
    if not user_data.get("subscribed", False):
        is_subscribed = check_subscription(user_id)
        if not is_subscribed:
            update.message.reply_text(
                get_text(lang, "not_subscribed"),
                reply_markup=subscribe_keyboard(lang)
            )
            return
        else:
            user_data["subscribed"] = True
            save_user(user_id, user_data)
    
    # Normal mesaj işleme
    user_message = update.message.text
    
    if user_message.lower() in ['merhaba', 'selam', 'hello', 'hi']:
        update.message.reply_text(
            f"{get_text(lang, 'main_menu')}\n\nMerhaba! 👋",
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        update.message.reply_text(
            f"{get_text(lang, 'main_menu')}\n\nMesajınız: {user_message}",
            reply_markup=main_menu_keyboard(lang)
        )

def error_handler(update: Update, context: CallbackContext):
    """Hataları işle"""
    logging.error(f"Update {update} caused error {context.error}")

# ========== ANA FONKSİYON ==========
def main():
    """Botu başlat"""
    # Token kontrolü
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        print("Lütfen Railway'da TOKEN variable ekleyin")
        return
    
    # Updater oluştur
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Handler'ları ekle
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("language", language_command))
    dp.add_handler(CommandHandler("lang", language_command))
    
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    dp.add_error_handler(error_handler)
    
    # Botu başlat
    print("=" * 50)
    print("🤖 Bot başlatılıyor...")
    print(f"📊 Kayıtlı kullanıcı: {len(users_db)}")
    print(f"🌍 Diller: Türkçe, İngilizce, Arapça, Kürtçe")
    print("=" * 50)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()
