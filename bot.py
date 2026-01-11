from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatMemberStatus
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Bot token'ınızı Railway environment variable'dan alın
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Basit Healthcheck Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Logları sustur

def run_health_server():
    """Basit health check sunucusu"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"✅ Health server started on port {port}")
    server.serve_forever()

# Dosya yolları
USER_DATA_FILE = 'user_data.json'
CONFIG_FILE = 'config.json'

# Kullanıcı kontrol cache'i
user_check_cache = {}

# ========== DOSYA İŞLEMLERİ ==========
def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    """Kullanıcı verilerini kaydet"""
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_config():
    """Config dosyasını yükle"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        default_config = {
            "admin_id": "5541236874",
            "channel_username": "",
            "channel_invite_link": "",
            "required_channel": False,
            "channel_id": None
        }
        save_config(default_config)
        return default_config

def save_config(config):
    """Config dosyasını kaydet"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    """Kullanıcının admin olup olmadığını kontrol et"""
    config = load_config()
    return str(user_id) == config.get('admin_id', "5541236874")

# ========== MESAJLAR ==========
LANGUAGES = {
    'ku': {
        'name': 'Kürtçe Sorani 🇹🇯',
        'welcome': '👋 بەخێربێیت! بۆتەکەمان بەکاربهێنە بۆ دەستکەوتنی پرۆمپتە باشەکان.',
        'prompts_button': 'پرۆمپتەکان 🔥',
        'change_lang_button': 'زمان بگۆڕە',
        'help_button': 'یارمەتی',
        'choose_lang': '👋 تکایە زمانێک هەڵبژێرە:',
        'lang_selected': '✅ زمانی تۆ دیاری کرا!',
        'help_text': 'یارمەتی: ئەم بۆتە پرۆمپتەکانت پێدەدات...',
        'not_subscribed': '⚠️ پێویستە سەبسکرایبی کەناڵەکەمان بیت بۆ بەکارهێنانی بۆتەکە!',
        'subscribe_button': 'چوونە ناو کەناڵەکە',
        'check_button': '✅ پشکنین',
        'already_subscribed': '✅ سوپاس! ئێستا دەتوانیت بۆتەکە بەکاربهێنیت.',
        'now_subscribed': '🎉 سوپاس بۆ چوونە ناو کەناڵەکە! ئێستا دەتوانیت بۆتەکە بەکاربهێنیت.',
        'admin_only': '❌ تەنیا بەڕێوەبەر دەتوانێت ئەم فرمانە بەکاربهێنێت!'
    },
    'en': {
        'name': 'English 🇬🇧',
        'welcome': '👋 Welcome! Use our bot to get great prompts.',
        'prompts_button': 'Prompts 🔥',
        'change_lang_button': 'Change Language',
        'help_button': 'Help',
        'choose_lang': '👋 Please choose a language:',
        'lang_selected': '✅ Your language has been set!',
        'help_text': 'Help: This bot provides you with prompts...',
        'not_subscribed': '⚠️ You must subscribe to our channel to use the bot!',
        'subscribe_button': 'Join Channel',
        'check_button': '✅ Check',
        'already_subscribed': '✅ Thank you! You can now use the bot.',
        'now_subscribed': '🎉 Thank you for joining the channel! You can now use the bot.',
        'admin_only': '❌ Only admin can use this command!'
    },
    'ar': {
        'name': 'Arabic 🇮🇶',
        'welcome': '👋 أهلاً وسهلاً! استخدم بوتنا للحصول على نصوص رائعة.',
        'prompts_button': 'النصوص 🔥',
        'change_lang_button': 'تغيير اللغة',
        'help_button': 'مساعدة',
        'choose_lang': '👋 الرجاء اختيار لغة:',
        'lang_selected': '✅ تم تحديد لغتك!',
        'help_text': 'مساعدة: هذا البوت يزودك بالنصوص...',
        'not_subscribed': '⚠️ يجب عليك الاشتراك في قناتنا لاستخدام البوت!',
        'subscribe_button': 'انضم إلى القناة',
        'check_button': '✅ تحقق',
        'already_subscribed': '✅ شكراً! يمكنك الآن استخدام البوت.',
        'now_subscribed': '🎉 شكراً للانضمام إلى القناة! يمكنك الآن استخدام البوت.',
        'admin_only': '❌ فقط المدير يمكنه استخدام هذا الأمر!'
    }
}

# ========== KANAL KONTROLÜ ==========
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE, force_check=False):
    """Kullanıcının kanala üye olup olmadığını kontrol et"""
    config = load_config()
    
    if not config.get('required_channel', False) or not config.get('channel_username'):
        return True
    
    if is_admin(user_id):
        return True
    
    # Cache kontrolü (2 dakika)
    cache_key = str(user_id)
    current_time = time.time()
    
    if not force_check and cache_key in user_check_cache:
        cached_time, cached_result = user_check_cache[cache_key]
        if current_time - cached_time < 120:  # 2 dakika
            return cached_result
    
    try:
        channel_username = config['channel_username']
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        chat_id = config.get('channel_id')
        if chat_id:
            try:
                chat_member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            except:
                chat_member = await context.bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
        else:
            chat_member = await context.bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
        
        is_member = chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, 
                                         ChatMemberStatus.OWNER, ChatMemberStatus.CREATOR]
        
        # Cache'e kaydet
        user_check_cache[cache_key] = (current_time, is_member)
        return is_member
            
    except Exception:
        return False

async def show_subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE, user_lang='en'):
    """Abonelik gerekli mesajını göster"""
    config = load_config()
    lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
    
    if not config.get('channel_invite_link'):
        if update.message:
            await update.message.reply_text("❌ Davet linki ayarlanmamış!")
        return
    
    keyboard = [[InlineKeyboardButton(lang_data['subscribe_button'], url=config.get('channel_invite_link'))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(lang_data['not_subscribed'], reply_markup=reply_markup)

async def auto_check_and_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Otomatik kontrol ve onay"""
    config = load_config()
    if not config.get('required_channel', False) or not config.get('channel_username'):
        return True
    
    user_id = update.effective_user.id
    is_member = await check_channel_membership(user_id, context, force_check=True)
    
    if is_member:
        # Kullanıcı abone oldu, onayla
        user_data = load_user_data()
        user_lang = user_data.get(str(user_id), {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        
        # Otomatik onay mesajı
        if update.message:
            await update.message.reply_text(lang_data['now_subscribed'])
        return True
    else:
        # Abone değil, mesaj göster
        user_data = load_user_data()
        user_lang = user_data.get(str(user_id), {}).get('lang', 'en')
        await show_subscription_required(update, context, user_lang)
        return False

# ========== ANA KOMUTLAR ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Önce kanal kontrolü
    config = load_config()
    if config.get('required_channel', False) and config.get('channel_username'):
        approved = await auto_check_and_approve(update, context)
        if not approved:
            return
    
    # Dil kontrolü
    if user_id not in user_data or 'lang' not in user_data[user_id]:
        await show_language_selection(update)
    else:
        await show_welcome_message(update, user_data[user_id]['lang'])

async def show_language_selection(update: Update):
    """Dil seçimi göster"""
    keyboard = [
        [InlineKeyboardButton(LANGUAGES['ku']['name'], callback_data='lang_ku')],
        [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en')],
        [InlineKeyboardButton(LANGUAGES['ar']['name'], callback_data='lang_ar')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Please choose a language / تكایە زمانێک هەڵبژێرە / الرجاء اختيار لغة:",
        reply_markup=reply_markup
    )

async def show_welcome_message(update: Update, lang_code='en'):
    """Hoşgeldin mesajı göster"""
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])
    
    keyboard = [
        [InlineKeyboardButton(lang_data['prompts_button'], url='https://t.me/PrompttAI_bot/Prompts')],
        [
            InlineKeyboardButton(lang_data['change_lang_button'], callback_data='change_lang'),
            InlineKeyboardButton(lang_data['help_button'], callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(lang_data['welcome'], reply_markup=reply_markup)

# ========== MESAJ İŞLEYİCİ ==========
async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm mesajları işle (otomatik kontrol)"""
    if update.message and not update.message.text.startswith('/'):
        config = load_config()
        if config.get('required_channel', False) and config.get('channel_username'):
            await auto_check_and_approve(update, context)

# ========== ADMIN KOMUTLARI ==========
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/join komutu"""
    user_id = str(update.effective_user.id)
    
    if not is_admin(user_id):
        user_data = load_user_data()
        user_lang = user_data.get(user_id, {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        await update.message.reply_text(lang_data['admin_only'])
        return
    
    config = load_config()
    
    if not context.args:
        current_settings = (
            "🛠️ **Admin Panel**\n\n"
            f"👑 Admin: {config.get('admin_id')}\n"
            f"📢 Kanal: {config.get('channel_username', 'Yok')}\n"
            f"🔗 Link: {config.get('channel_invite_link', 'Yok')}\n"
            f"📌 Zorunlu: {'✅ Evet' if config.get('required_channel') else '❌ Hayır'}\n\n"
            "**Komutlar:**\n"
            "/join @kanal - Kanal ayarla\n"
            "/join on - Zorunlu abonelik aç\n"
            "/join off - Zorunlu abonelik kapat\n"
            "/join status - Durum"
        )
        await update.message.reply_text(current_settings)
        return
    
    command = context.args[0].lower()
    
    if command == "on":
        if not config.get('channel_username'):
            await update.message.reply_text("❌ Önce kanalı ayarla: /join @kanal")
            return
        config['required_channel'] = True
        save_config(config)
        await update.message.reply_text("✅ Zorunlu abonelik açıldı!")
        
    elif command == "off":
        config['required_channel'] = False
        save_config(config)
        await update.message.reply_text("✅ Zorunlu abonelik kapatıldı!")
        
    elif command == "status":
        status_text = (
            f"📊 **Durum**\n"
            f"Kanal: {config.get('channel_username', 'Yok')}\n"
            f"Zorunlu: {'✅ Evet' if config.get('required_channel') else '❌ Hayır'}\n"
            f"Cache: {len(user_check_cache)} kayıt"
        )
        await update.message.reply_text(status_text)
        
    elif command.startswith('@'):
        channel_username = command
        try:
            chat = await context.bot.get_chat(chat_id=channel_username)
            config['channel_username'] = channel_username
            config['channel_id'] = chat.id
            if not config.get('channel_invite_link'):
                channel_name = channel_username[1:]
                config['channel_invite_link'] = f"https://t.me/{channel_name}"
            save_config(config)
            await update.message.reply_text(f"✅ Kanal ayarlandı: {chat.title}")
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
        
    elif command == "link" and len(context.args) > 1:
        link = context.args[1]
        if link.startswith('https://t.me/'):
            config['channel_invite_link'] = link
            save_config(config)
            await update.message.reply_text(f"✅ Link güncellendi: {link}")
        else:
            await update.message.reply_text("❌ Link https://t.me/ ile başlamalı")
        
    else:
        await update.message.reply_text("❌ Geçersiz komut!")

# ========== BUTON İŞLEMLERİ ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton işlemleri"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    # Önce kanal kontrolü
    config = load_config()
    if config.get('required_channel', False) and config.get('channel_username'):
        approved = await auto_check_and_approve(update, context)
        if not approved:
            return
    
    if query.data.startswith('lang_'):
        lang_code = query.data.split('_')[1]
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['lang'] = lang_code
        save_user_data(user_data)
        lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])
        await query.edit_message_text(text=lang_data['lang_selected'])
        await show_welcome_message(update, lang_code)
        
    elif query.data == 'change_lang':
        await show_language_selection(update)
        
    elif query.data == 'help':
        user_lang = user_data.get(user_id, {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        await query.message.reply_text(lang_data['help_text'])

# ========== BOT BAŞLATMA ==========
def main():
    """Ana fonksiyon"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN ayarlanmamış!")
        return
    
    # Health server'ı başlat
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Botu başlat
    print("🤖 Bot başlatılıyor...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handler'ları ekle
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('join', join_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_any_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Config yükle
    config = load_config()
    print(f"✅ Bot çalışıyor! Admin: {config.get('admin_id')}")
    
    # Polling başlat
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
