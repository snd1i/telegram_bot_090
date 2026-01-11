from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatMemberStatus
import json
import os
import time
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import traceback

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

# Debug log için
DEBUG = True

def debug_log(message):
    """Debug mesajı yazdır"""
    if DEBUG:
        print(f"🔍 DEBUG: {message}")

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
            config = json.load(f)
            debug_log(f"Config loaded: {config}")
            return config
    except:
        default_config = {
            "admin_id": "5541236874",
            "channel_username": "",
            "channel_invite_link": "",
            "required_channel": False,
            "channel_id": None,
            "channel_title": ""
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
    is_admin_user = str(user_id) == config.get('admin_id', "5541236874")
    debug_log(f"Admin check for {user_id}: {is_admin_user}")
    return is_admin_user

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
        'admin_only': '❌ تەنیا بەڕێوەبەر دەتوانێت ئەم فرمانە بەکاربهێنێت!',
        'join_first': '📢 لەپێش هەموو شتێك، تکایە بچۆرە ناو کەناڵەکە:'
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
        'admin_only': '❌ Only admin can use this command!',
        'join_first': '📢 First, please join our channel:'
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
        'admin_only': '❌ فقط المدير يمكنه استخدام هذا الأمر!',
        'join_first': '📢 أولاً، يرجى الانضمام إلى قناتنا:'
    }
}

# ========== KANAL KONTROLÜ - DÜZELTİLMİŞ VERSİYON ==========
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının kanala üye olup olmadığını kontrol et - DÜZELTİLDİ"""
    config = load_config()
    
    debug_log(f"Checking membership for user {user_id}")
    debug_log(f"Config: required={config.get('required_channel')}, channel={config.get('channel_username')}")
    
    # Eğer kanal zorunlu değilse veya kanal ayarlanmamışsa true dön
    if not config.get('required_channel', False):
        debug_log("Required channel is disabled")
        return True
    
    channel_username = config.get('channel_username')
    if not channel_username:
        debug_log("No channel username set")
        return True
    
    # Admin için kanal kontrolünü atla
    if is_admin(user_id):
        debug_log(f"User {user_id} is admin, skipping check")
        return True
    
    try:
        # @ işaretini temizle
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        debug_log(f"Checking channel: {channel_username}")
        
        # Önce kanal bilgilerini al
        try:
            chat = await context.bot.get_chat(chat_id=f"@{channel_username}")
            debug_log(f"Channel info: {chat.title}, ID: {chat.id}, Type: {chat.type}")
        except Exception as e:
            debug_log(f"Error getting channel info: {e}")
            return False
        
        # Kullanıcının kanal durumunu kontrol et
        try:
            chat_member = await context.bot.get_chat_member(
                chat_id=f"@{channel_username}",
                user_id=user_id
            )
            
            debug_log(f"User {user_id} status in channel: {chat_member.status}")
            
            # DÜZELTME: ChatMemberStatus.OWNER kullan, CREATOR değil
            # Telegram API'de geçerli statüler:
            # creator, administrator, member, restricted, left, kicked, owner
            is_member = chat_member.status in [
                ChatMemberStatus.MEMBER, 
                ChatMemberStatus.ADMINISTRATOR, 
                ChatMemberStatus.OWNER  # BU DÜZELDİ: CREATOR yerine OWNER
            ]
            
            # Alternatif olarak string kontrolü de yapabiliriz
            status_str = str(chat_member.status).lower()
            debug_log(f"Status string: {status_str}")
            
            # String bazlı kontrol (daha güvenli)
            if status_str in ['member', 'administrator', 'creator', 'owner']:
                is_member = True
            else:
                is_member = False
            
            debug_log(f"Is member (string check): {is_member}")
            
            return is_member
            
        except Exception as e:
            debug_log(f"Error checking membership: {e}")
            # "User not found" hatası, kullanıcı kanalda değil demektir
            error_str = str(e).lower()
            if "user not found" in error_str or "chat not found" in error_str:
                debug_log("User not found in channel")
                return False
            elif "bot is not a member" in error_str:
                debug_log("❌ ERROR: Bot is not a member of the channel!")
                return False
            else:
                debug_log(f"Unknown error: {e}")
                # Hata durumunda daha detaylı log
                debug_log(traceback.format_exc())
                return False
            
    except Exception as e:
        debug_log(f"General error in check_channel_membership: {e}")
        debug_log(traceback.format_exc())
        return False

async def show_subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE, user_lang='en'):
    """Abonelik gerekli mesajını göster"""
    config = load_config()
    lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
    
    debug_log(f"Showing subscription required for user {update.effective_user.id}")
    
    invite_link = config.get('channel_invite_link')
    if not invite_link:
        # Varsayılan link oluştur
        channel_username = config.get('channel_username', '')
        if channel_username and channel_username.startswith('@'):
            channel_name = channel_username[1:]
            invite_link = f"https://t.me/{channel_name}"
        else:
            invite_link = "https://t.me"
    
    debug_log(f"Invite link: {invite_link}")
    
    # Önce "öncelikle katılın" mesajı
    join_first_msg = await update.message.reply_text(
        f"{lang_data['join_first']}\n{invite_link}"
    )
    
    # 2 saniye bekle
    await asyncio.sleep(2)
    
    # Sonra kontrol butonlu mesaj
    keyboard = [[InlineKeyboardButton(lang_data['subscribe_button'], url=invite_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    main_msg = await update.message.reply_text(
        lang_data['not_subscribed'],
        reply_markup=reply_markup
    )
    
    # Mesaj ID'lerini kaydet
    context.user_data['join_first_msg_id'] = join_first_msg.message_id
    context.user_data['subscription_msg_id'] = main_msg.message_id

async def auto_check_and_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Otomatik kontrol ve onay"""
    user_id = update.effective_user.id
    config = load_config()
    
    debug_log(f"Auto checking for user {user_id}")
    
    if not config.get('required_channel', False) or not config.get('channel_username'):
        debug_log("Channel check not required")
        return True
    
    # Kontrol et
    is_member = await check_channel_membership(user_id, context)
    
    debug_log(f"Check result for user {user_id}: {is_member}")
    
    if is_member:
        debug_log(f"User {user_id} is a member, approving...")
        
        # Eski mesajları sil
        try:
            if 'join_first_msg_id' in context.user_data:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['join_first_msg_id']
                )
                debug_log("Deleted join_first message")
        except Exception as e:
            debug_log(f"Error deleting join_first message: {e}")
        
        try:
            if 'subscription_msg_id' in context.user_data:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['subscription_msg_id']
                )
                debug_log("Deleted subscription message")
        except Exception as e:
            debug_log(f"Error deleting subscription message: {e}")
        
        # Onay mesajı gönder
        user_data = load_user_data()
        user_lang = user_data.get(str(user_id), {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        
        debug_log(f"Sending approval message in {user_lang}")
        await update.message.reply_text(lang_data['now_subscribed'])
        return True
    else:
        debug_log(f"User {user_id} is NOT a member")
        return False

# ========== ANA KOMUTLAR ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    user_id = str(update.effective_user.id)
    debug_log(f"/start from user {user_id}")
    
    user_data = load_user_data()
    config = load_config()
    
    # Önce kanal kontrolü
    if config.get('required_channel', False) and config.get('channel_username'):
        debug_log("Channel check required, checking...")
        approved = await auto_check_and_approve(update, context)
        if not approved:
            debug_log("User not approved, showing subscription required")
            user_lang = user_data.get(user_id, {}).get('lang', 'en')
            await show_subscription_required(update, context, user_lang)
            return
    
    # Dil kontrolü
    if user_id not in user_data or 'lang' not in user_data[user_id]:
        debug_log("No language set, showing selection")
        await show_language_selection(update)
    else:
        debug_log(f"Language already set: {user_data[user_id]['lang']}")
        await show_welcome_message(update, user_data[user_id]['lang'])

async def show_language_selection(update: Update):
    """Dil seçimi göster"""
    debug_log("Showing language selection")
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
    debug_log(f"Showing welcome message in {lang_code}")
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
    """Her mesajda otomatik kontrol"""
    if update.message and not update.message.text.startswith('/'):
        user_id = update.effective_user.id
        debug_log(f"Message from user {user_id}: {update.message.text[:50]}...")
        
        config = load_config()
        if config.get('required_channel', False) and config.get('channel_username'):
            debug_log("Auto-checking message sender...")
            await auto_check_and_approve(update, context)

# ========== ADMIN KOMUTLARI ==========
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/join komutu"""
    user_id = str(update.effective_user.id)
    debug_log(f"/join from user {user_id}")
    
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
            f"👑 **Admin ID:** {config.get('admin_id')}\n"
            f"📢 **Channel:** {config.get('channel_username', 'Not set')}\n"
            f"🏷️ **Title:** {config.get('channel_title', 'Not set')}\n"
            f"🔗 **Invite Link:** {config.get('channel_invite_link', 'Not set')}\n"
            f"📌 **Required:** {'✅ YES' if config.get('required_channel') else '❌ NO'}\n\n"
            "**Commands:**\n"
            "/join test - Test channel\n"
            "/join on - Enable required\n"
            "/join off - Disable required\n"
            "/join @channel - Set channel"
        )
        await update.message.reply_text(current_settings)
        return
    
    command = context.args[0].lower()
    debug_log(f"Admin command: {command}")
    
    if command == "on":
        if not config.get('channel_username'):
            await update.message.reply_text("❌ First set a channel with /join @channel")
            return
        config['required_channel'] = True
        save_config(config)
        await update.message.reply_text("✅ Required subscription ENABLED!")
        
    elif command == "off":
        config['required_channel'] = False
        save_config(config)
        await update.message.reply_text("✅ Required subscription DISABLED!")
        
    elif command == "test":
        if not config.get('channel_username'):
            await update.message.reply_text("❌ No channel set!")
            return
        
        channel_username = config['channel_username']
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        try:
            chat = await context.bot.get_chat(chat_id=f"@{channel_username}")
            
            # Test: Admin'in durumunu kontrol et
            try:
                admin_member = await context.bot.get_chat_member(
                    chat_id=chat.id,
                    user_id=update.effective_user.id
                )
                admin_status = f"Your status: {admin_member.status}"
            except Exception as e:
                admin_status = f"Your status: Error - {str(e)}"
            
            # Test: Bot'un durumunu kontrol et
            try:
                bot_member = await context.bot.get_chat_member(
                    chat_id=chat.id,
                    user_id=context.bot.id
                )
                bot_status = f"Bot status: {bot_member.status}"
            except Exception as e:
                bot_status = f"Bot status: Error - {str(e)}"
            
            config['channel_id'] = chat.id
            config['channel_title'] = chat.title
            save_config(config)
            
            await update.message.reply_text(
                f"✅ **Channel Test**\n\n"
                f"📢 Title: {chat.title}\n"
                f"👤 Username: @{chat.username}\n"
                f"🆔 ID: {chat.id}\n"
                f"📝 Type: {chat.type}\n\n"
                f"🔧 {bot_status}\n"
                f"👑 {admin_status}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Test failed: {str(e)}")
        
    elif command.startswith('@'):
        channel_username = command
        
        try:
            chat = await context.bot.get_chat(chat_id=channel_username)
            config['channel_username'] = channel_username
            config['channel_id'] = chat.id
            config['channel_title'] = chat.title
            
            if not config.get('channel_invite_link'):
                channel_name = channel_username[1:]
                config['channel_invite_link'] = f"https://t.me/{channel_name}"
            
            save_config(config)
            
            await update.message.reply_text(
                f"✅ Channel set!\n"
                f"Title: {chat.title}\n"
                f"ID: {chat.id}\n"
                f"Link: {config['channel_invite_link']}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        
    else:
        await update.message.reply_text("❌ Invalid command!")

# ========== BUTON İŞLEMLERİ ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton işlemleri"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    debug_log(f"Button callback from user {user_id}: {query.data}")
    
    user_data = load_user_data()
    config = load_config()
    
    # Önce kanal kontrolü
    if config.get('required_channel', False) and config.get('channel_username'):
        debug_log("Checking channel for button click...")
        approved = await auto_check_and_approve(update, context)
        if not approved:
            debug_log("User not approved for button action")
            user_lang = user_data.get(user_id, {}).get('lang', 'en')
            await show_subscription_required(update, context, user_lang)
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
async def main_async():
    """Async main fonksiyonu"""
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not set!")
        return
    
    # Health server'ı başlat
    health_thread = Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Botu başlat
    print("🤖 Bot starting...")
    print("✅ FIX: Using ChatMemberStatus.OWNER instead of CREATOR")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handler'ları ekle
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('join', join_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_any_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Config yükle
    config = load_config()
    print(f"✅ Bot running! Admin: {config.get('admin_id')}")
    print(f"📢 Channel: {config.get('channel_username', 'Not set')}")
    
    # Polling başlat
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Bot started successfully!")
    
    # Sonsuz döngü
    while True:
        await asyncio.sleep(3600)

def main():
    """Main fonksiyonu"""
    asyncio.run(main_async())

if __name__ == '__main__':
    main()
