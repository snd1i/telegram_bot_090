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
        pass

def run_health_server():
    """Basit health check sunucusu"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"✅ Health server started on port {port}")
    server.serve_forever()

# Dosya yolları
USER_DATA_FILE = 'user_data.json'
CONFIG_FILE = 'config.json'

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
        'already_subscribed': '✅ شكراً! يمكنك الآن استخدام البوت.',
        'now_subscribed': '🎉 شكراً للانضمام إلى القناة! يمكنك الآن استخدام البوت.',
        'admin_only': '❌ فقط المدير يمكنه استخدام هذا الأمر!'
    }
}

# ========== KANAL KONTROLÜ ==========
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının kanala üye olup olmadığını kontrol et"""
    config = load_config()
    
    # Eğer kanal zorunlu değilse veya kanal ayarlanmamışsa true dön
    if not config.get('required_channel', False) or not config.get('channel_username'):
        return True
    
    # Admin için kanal kontrolünü atla
    if is_admin(user_id):
        return True
    
    try:
        channel_username = config['channel_username']
        # @ işaretini temizle
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        # Kanal ID'sini kullanarak kontrol et
        chat_id = config.get('channel_id')
        if chat_id:
            try:
                chat_member = await context.bot.get_chat_member(
                    chat_id=chat_id,
                    user_id=user_id
                )
            except:
                # ID ile olmazsa username ile dene
                chat_member = await context.bot.get_chat_member(
                    chat_id=f"@{channel_username}",
                    user_id=user_id
                )
        else:
            # Username ile kontrol et
            chat_member = await context.bot.get_chat_member(
                chat_id=f"@{channel_username}",
                user_id=user_id
            )
        
        # String bazlı kontrol (güvenli)
        status_str = str(chat_member.status).lower()
        return status_str in ['member', 'administrator', 'creator', 'owner']
            
    except Exception:
        # Herhangi bir hata durumunda kullanıcı kanalda değil say
        return False

async def show_subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE, user_lang='en'):
    """Abonelik gerekli mesajını göster"""
    config = load_config()
    lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
    
    invite_link = config.get('channel_invite_link', 'https://t.me')
    
    # Mesajı ve butonu göster
    keyboard = [[InlineKeyboardButton(lang_data['subscribe_button'], url=invite_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"{lang_data['not_subscribed']}\n{invite_link}"
    
    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(message_text, reply_markup=reply_markup)

async def check_user_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının erişimini kontrol et"""
    user_id = update.effective_user.id
    user_data = load_user_data()
    config = load_config()
    
    # Kanal kontrolü
    if config.get('required_channel', False) and config.get('channel_username'):
        is_member = await check_channel_membership(user_id, context)
        
        if not is_member:
            # Kullanıcının dilini bul
            user_lang = user_data.get(str(user_id), {}).get('lang', 'en')
            await show_subscription_required(update, context, user_lang)
            return False
    
    return True

# ========== ANA KOMUTLAR ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Önce erişim kontrolü
    has_access = await check_user_access(update, context)
    if not has_access:
        return
    
    # Dil kontrolü
    if user_id not in user_data or 'lang' not in user_data[user_id]:
        # Dil seçimi göster
        await show_language_selection(update, context)
    else:
        # Hoşgeldin mesajı göster
        await show_welcome_message(update, context, user_data[user_id]['lang'])

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dil seçimi göster"""
    keyboard = [
        [InlineKeyboardButton(LANGUAGES['ku']['name'], callback_data='lang_ku')],
        [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en')],
        [InlineKeyboardButton(LANGUAGES['ar']['name'], callback_data='lang_ar')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            LANGUAGES['en']['choose_lang'],
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            LANGUAGES['en']['choose_lang'],
            reply_markup=reply_markup
        )

async def show_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, lang_code='en'):
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
    
    if update.message:
        await update.message.reply_text(
            lang_data['welcome'],
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            lang_data['welcome'],
            reply_markup=reply_markup
        )

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
            f"👑 Admin ID: {config.get('admin_id')}\n"
            f"📢 Channel: {config.get('channel_username', 'Not set')}\n"
            f"🔗 Invite Link: {config.get('channel_invite_link', 'Not set')}\n"
            f"📌 Required: {'✅ YES' if config.get('required_channel') else '❌ NO'}\n\n"
            "**Commands:**\n"
            "/join @channelname - Set channel\n"
            "/join link https://t.me/... - Set invite link\n"
            "/join on - Enable required subscription\n"
            "/join off - Disable required subscription\n"
            "/join status - Show current status"
        )
        await update.message.reply_text(current_settings)
        return
    
    command = context.args[0].lower()
    
    if command == "on":
        if not config.get('channel_username'):
            await update.message.reply_text("❌ First set a channel with /join @channelname")
            return
            
        config['required_channel'] = True
        save_config(config)
        await update.message.reply_text("✅ Required channel subscription ENABLED!")
        
    elif command == "off":
        config['required_channel'] = False
        save_config(config)
        await update.message.reply_text("✅ Required channel subscription DISABLED!")
        
    elif command == "status":
        status_text = (
            f"📊 **Status Report**\n\n"
            f"Admin: {config.get('admin_id')}\n"
            f"Channel: {config.get('channel_username', 'Not set')}\n"
            f"Required: {'✅ ENABLED' if config.get('required_channel') else '❌ DISABLED'}\n"
            f"Invite Link: {config.get('channel_invite_link', 'Not set')}"
        )
        await update.message.reply_text(status_text)
        
    elif command == "link" and len(context.args) > 1:
        link = context.args[1]
        if not link.startswith('https://t.me/'):
            await update.message.reply_text("❌ Invalid link! Must start with https://t.me/")
            return
        config['channel_invite_link'] = link
        save_config(config)
        await update.message.reply_text(f"✅ Invite link updated: {link}")
        
    elif command.startswith('@'):
        # Kanal kullanıcı adı
        channel_username = command
        
        try:
            # Kanalı kontrol et
            chat = await context.bot.get_chat(chat_id=channel_username)
            config['channel_username'] = channel_username
            config['channel_id'] = chat.id
            
            # Varsayılan davet linki oluştur
            if not config.get('channel_invite_link'):
                channel_name = channel_username[1:]  # @ işaretini kaldır
                config['channel_invite_link'] = f"https://t.me/{channel_name}"
            
            save_config(config)
            await update.message.reply_text(
                f"✅ Channel set successfully!\n"
                f"📢 Name: {chat.title}\n"
                f"👤 Username: {channel_username}\n"
                f"📎 Invite link: {config['channel_invite_link']}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error setting channel: {str(e)}")
        
    else:
        await update.message.reply_text("❌ Invalid command! Type /join for help.")

# ========== BUTON İŞLEMLERİ ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    
    # BUTON TÜRÜNE GÖRE İŞLEM
    if query.data.startswith('lang_'):
        # DİL SEÇİMİ BUTONU
        # Önce erişim kontrolü
        has_access = await check_user_access(update, context)
        if not has_access:
            return
        
        # Dil seçimi
        lang_code = query.data.split('_')[1]
        
        # Kullanıcı verisini kaydet
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['lang'] = lang_code
        save_user_data(user_data)
        
        # Seçilen dilin mesajını göster
        lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])
        await query.edit_message_text(text=lang_data['lang_selected'])
        
        # Hoşgeldin mesajını göster
        await show_welcome_message(update, context, lang_code)
        
    elif query.data == 'change_lang':
        # DİL DEĞİŞTİRME BUTONU
        # Önce erişim kontrolü
        has_access = await check_user_access(update, context)
        if not has_access:
            return
        
        # Dil değiştirme
        await show_language_selection(update, context)
        
    elif query.data == 'help':
        # YARDIM BUTONU
        # Önce erişim kontrolü
        has_access = await check_user_access(update, context)
        if not has_access:
            return
        
        # Yardım butonu
        user_lang = user_data.get(user_id, {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        await query.message.reply_text(lang_data['help_text'])

# ========== EKLENTİ YÜKLEYİCİ ==========
def load_extensions(application):
    """Extensions klasöründeki komutları yükler"""
    print("🔄 Loading extensions...")
    
    try:
        import os
        
        # extensions klasörü var mı kontrol et
        if os.path.exists("extensions"):
            print("📁 Found extensions folder")
            
            # 1. basic.py'yi yükle
            basic_path = os.path.join("extensions", "basic.py")
            if os.path.exists(basic_path):
                try:
                    from extensions import basic
                    if hasattr(basic, "setup"):
                        basic.setup(application)
                        print("✅ Loaded: basic.py")
                    else:
                        print("⚠️ basic.py has no setup() function")
                except Exception as e:
                    print(f"❌ Error loading basic.py: {e}")
            
            # 2. admin.py'yi yükle
            admin_path = os.path.join("extensions", "admin.py")
            if os.path.exists(admin_path):
                try:
                    from extensions import admin
                    if hasattr(admin, "setup"):
                        admin.setup(application)
                        print("✅ Loaded: admin.py")
                    else:
                        print("⚠️ admin.py has no setup() function")
                except Exception as e:
                    print(f"❌ Error loading admin.py: {e}")
            else:
                print("ℹ️ admin.py not found in extensions/")
                
        else:
            print("ℹ️ No extensions folder found")
            
    except Exception as e:
        print(f"⚠️ Extension loader error: {e}")
    
    print("✅ Extension loading completed!")

# ========== BOT BAŞLATMA ==========
def main():
    """Botu başlat"""
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN environment variable not set!")
        print("Go to Railway → Variables → Add BOT_TOKEN")
        return
    
    # Health server'ı başlat
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Config dosyasını yükle
    config = load_config()
    
    # Bot uygulamasını oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ANA komut işleyicileri
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('join', join_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # EKLENTİLERİ YÜKLE
    load_extensions(application)
    
    # Botu başlat
    print("🤖 Bot başlatılıyor...")
    print(f"👑 Admin ID: {config.get('admin_id')}")
    print(f"📢 Channel: {config.get('channel_username', 'Not set')}")
    print(f"🔒 Required Subscription: {config.get('required_channel', False)}")
    print("✅ Healthcheck endpoint: /health")
    
    # Polling'i başlat
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
