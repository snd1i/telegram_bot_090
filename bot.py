import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)

# Log ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token (Railway'dan alınacak)
TOKEN = os.getenv("TOKEN", "")

# Kanal bilgileri
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"
CHANNEL_ID = -1002072605977

# ========== VERİTABANI ==========
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

def save_users(users):
    """Kullanıcıları kaydet"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Kaydetme hatası: {e}")

users_db = load_users()

def get_user(user_id):
    """Kullanıcıyı getir"""
    return users_db.get(str(user_id))

def update_user(user_id, data):
    """Kullanıcıyı güncelle"""
    user_id_str = str(user_id)
    
    if user_id_str in users_db:
        users_db[user_id_str].update(data)
    else:
        users_db[user_id_str] = data
    
    users_db[user_id_str]["last_seen"] = datetime.now().isoformat()
    save_users(users_db)

def create_user(user_id, username, first_name, language_code=None):
    """Yeni kullanıcı oluştur"""
    default_lang = detect_language(language_code)
    
    user_data = {
        "id": user_id,
        "username": username,
        "first_name": first_name,
        "language": default_lang,  # Telegram diline göre otomatik
        "selected_language": False,  # Henüz dil seçmedi
        "subscribed": False,
        "first_start": True,  # İlk defa /start yapıyor
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat()
    }
    
    update_user(user_id, user_data)
    return user_data

def detect_language(language_code):
    """Telegram dil kodundan bot dilini belirle"""
    if language_code:
        # Telegram dil kodlarını bizim dil kodlarımıza çevir
        if language_code.startswith('tr'):
            return "tr"
        elif language_code.startswith('ar'):
            return "ar"
        elif language_code in ['ku', 'ckb']:
            return "ckb"  # Kürtçe Sorani varsayılan
        elif language_code.startswith('en'):
            return "en"
    
    return "en"  # Varsayılan İngilizce

# ========== DİL SİSTEMİ ==========
TEXTS = {
    "tr": {
        "welcome": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "welcome_back": "🇹🇷 Tekrar hoş geldin {name}!",
        "welcome_selected": "🇹🇷 Hoş geldiniz! Dil olarak Türkçe seçildi.",
        "subscribe": "📢 Devam etmek için lütfen kanala abone olun:",
        "not_subscribed": "❌ Kanala abone olmadınız. Lütfen önce abone olun.",
        "checking": "⏳ Abonelik kontrol ediliyor...",
        "check_again": "🔍 Tekrar Kontrol Et",
        "subscribed": "✅ Zaten abonesiniz! Devam edebilirsiniz.",
        "main_menu": "🏠 Ana Menü",
        "help": "📖 Yardım\n\nKomutlar:\n/start - Botu başlat\n/help - Yardım\n/language - Dil değiştir",
        "select_language": "🌍 Dil Seçimi",
    },
    "en": {
        "welcome": "🤖 Welcome! Please select your language:",
        "welcome_back": "🇬🇧 Welcome back {name}!",
        "welcome_selected": "🇬🇧 Welcome! English has been selected as language.",
        "subscribe": "📢 Please subscribe to the channel to continue:",
        "not_subscribed": "❌ You are not subscribed to the channel. Please subscribe first.",
        "checking": "⏳ Checking subscription...",
        "check_again": "🔍 Check Again",
        "subscribed": "✅ You are already subscribed! You can continue.",
        "main_menu": "🏠 Main Menu",
        "help": "📖 Help\n\nCommands:\n/start - Start bot\n/help - Help\n/language - Change language",
        "select_language": "🌍 Language Selection",
    },
    "ckb": {
        "welcome": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "welcome_back": "🇹🇯 بەخێربێیت دووبارە {name}!",
        "welcome_selected": "🇹🇯 بەخێربێیت! زمانی کوردی سۆرانی هەڵبژێردرا.",
        "subscribe": "📢 تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوام بوون:",
        "not_subscribed": "❌ تۆ سەبسکرایبی کەناڵەکەت نەکردووە. تکایە سەبسکرایب بکە.",
        "checking": "⏳ سەبسکرایب چێک دەکرێت...",
        "check_again": "🔍 دووبارە چێک بکە",
        "subscribed": "✅ تۆ سەبسکرایبی کەناڵەکەیت کردووە! دەتوانی بەردەوام ببی.",
        "main_menu": "🏠 مێنیوی سەرەکی",
        "help": "📖 یارمەتی\n\nفەرمانەکان:\n/start - دەستپێکردنی بۆت\n/help - یارمەتی\n/language - گۆڕینی زمان",
        "select_language": "🌍 هەڵبژاردنی زمان",
    },
    "badini": {
        "welcome": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "welcome_back": "🇹🇯 Bi xêr hatî dîsa {name}!",
        "welcome_selected": "🇹🇯 Bi xêr hatî! Zimanê Kurdî Badînî hate hilbijartin.",
        "subscribe": "📢 Ji bo domandinê ji kerema xwe li kanalê abone bibin:",
        "not_subscribed": "❌ Te li kanalê abone nebûye. Ji kerema xwe pêşî abone bibin.",
        "checking": "⏳ Aboneyî tê kontrolkirin...",
        "check_again": "🔍 Dîsa Kontrol Bike",
        "subscribed": "✅ Te berê abone bûye! Tu dikarî bidomînî.",
        "main_menu": "🏠 Meniya Sereke",
        "help": "📖 Alîkarî\n\nFerman:\n/start - Destpêkirina bot\n/help - Alîkarî\n/language - Guherandina ziman",
        "select_language": "🌍 Hilbijartina Ziman",
    },
    "ar": {
        "welcome": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "welcome_back": "🇮🇶 أهلاً بك مرة أخرى {name}!",
        "welcome_selected": "🇮🇶 أهلاً بك! تم اختيار العربية كلغة.",
        "subscribe": "📢 يرجى الاشتراك في القناة للمتابعة:",
        "not_subscribed": "❌ لم تشترك في القناة. يرجى الاشتراك أولاً.",
        "checking": "⏳ جاري التحقق من الاشتراك...",
        "check_again": "🔍 تحقق مرة أخرى",
        "subscribed": "✅ أنت مشترك بالفعل! يمكنك المتابعة.",
        "main_menu": "🏠 القائمة الرئيسية",
        "help": "📖 مساعدة\n\nالأوامر:\n/start - بدء البوت\n/help - مساعدة\n/language - تغيير اللغة",
        "select_language": "🌍 اختيار اللغة",
    }
}

def get_text(lang_code, text_key, **kwargs):
    """Dil metnini getir (formatlama destekli)"""
    if lang_code in TEXTS and text_key in TEXTS[lang_code]:
        text = TEXTS[lang_code][text_key]
        # Formatlama varsa uygula
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text
    return TEXTS["en"].get(text_key, "")

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
            InlineKeyboardButton("İngilizce 🇬🇧", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton("Arapça 🇮🇶", callback_data="lang_ar"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def subscribe_keyboard(lang="en"):
    """Abone ol butonları"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang, "subscribe"), 
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                get_text(lang, "check_again"), 
                callback_data="check_sub"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(lang="en"):
    """Ana menü butonları"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang, "select_language"),
                callback_data="change_lang"
            )
        ],
        [
            InlineKeyboardButton("📖 " + get_text(lang, "help").split("\n")[0], callback_data="show_help"),
            InlineKeyboardButton("🏠 " + get_text(lang, "main_menu"), callback_data="main_menu"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== YARDIMCI FONKSİYONLAR ==========
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

# ========== HANDLER'LAR ==========
def start(update: Update, context: CallbackContext):
    """/start komutu"""
    user = update.effective_user
    user_id = user.id
    
    # Kullanıcıyı kontrol et
    existing_user = get_user(user_id)
    
    if not existing_user:
        # Yeni kullanıcı - Telegram diline göre varsayılan dil
        user_data = create_user(
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
            user_data["first_start"] = False
            update_user(user_id, {"first_start": False})
            
            update.message.reply_text(
                get_text("en", "welcome"),  # Varsayılan İngilizce dil seçimi
                reply_markup=language_keyboard()
            )
        else:
            # Daha önce dil seçmiş - direkt hoş geldin mesajı
            lang = user_data.get("language", "en")
            update.message.reply_text(
                get_text(lang, "welcome_back", name=user.first_name),
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
        lang_code = data.replace("lang_", "")
        
        # Kullanıcıyı güncelle
        update_user(user_id, {
            "language": lang_code,
            "selected_language": True,
            "first_start": False
        })
        
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
        user_data = get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(get_text(lang, "checking"))
        
        # Abonelik kontrol et
        is_subscribed = check_subscription(user_id)
        
        if is_subscribed:
            # Abone ise - ana menü göster
            update_user(user_id, {"subscribed": True})
            
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
        user_data = get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(
            get_text(lang, "help"),
            reply_markup=main_menu_keyboard(lang)
        )
    
    # Ana menü
    elif data == "main_menu":
        user_data = get_user(user_id)
        lang = user_data.get("language", "en") if user_data else "en"
        
        query.edit_message_text(
            get_text(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang)
        )

def help_command(update: Update, context: CallbackContext):
    """/help komutu"""
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if user_data and user_data.get("language"):
        lang = user_data["language"]
        update.message.reply_text(get_text(lang, "help"))
    else:
        # Kullanıcı yoksa dil seçimi göster
        start(update, context)

def language_command(update: Update, context: CallbackContext):
    """/language komutu - dil değiştir"""
    update.message.reply_text(
        get_text("en", "select_language"),
        reply_markup=language_keyboard()
    )

# ========== ANA FONKSİYON ==========
def main():
    """Botu başlat"""
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        return
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("language", language_command))
    dp.add_handler(CommandHandler("lang", language_command))
    
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot başlatılıyor...")
    print(f"📊 Kayıtlı kullanıcı: {len(users_db)}")
    print(f"🌍 Diller: Türkçe, İngilizce, Arapça, Kürtçe (Sorani/Badini)")
    print("✅ Özellikler:")
    print("  • Telegram diline göre varsayılan dil")
    print("  • Sadece ilk /start'ta dil seçimi")
    print("  • Sonraki /start'larda direkt hoşgeldin")
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
