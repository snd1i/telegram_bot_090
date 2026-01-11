from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatMemberStatus
from aiohttp import web
import json
import os
import asyncio

# Bot token'ınızı Railway environment variable'dan alın
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Dosya yolları
USER_DATA_FILE = 'user_data.json'
CONFIG_FILE = 'config.json'

# ========== HEALTH CHECK SERVER ==========
async def health_check(request):
    """Health check endpoint for Railway"""
    return web.Response(text="OK")

async def start_health_server():
    """Start health check server on port 8080"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("✅ Health check server started on port 8080")

# ========== DOSYA İŞLEMLERİ ==========
def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_data(data):
    """Kullanıcı verilerini kaydet"""
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_config():
    """Config dosyasını yükle"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            if config_data.get('admin_id') != "5541236874":
                config_data['admin_id'] = "5541236874"
                save_config(config_data)
            return config_data
    except (FileNotFoundError, json.JSONDecodeError):
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
        'admin_only': '❌ تەنیا بەڕێوەبەر دەتوانێت ئەم فرمانە بەکاربهێنێت!',
        'checking': '🔍 پشکنین بۆ ئەندامێتی...'
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
        'admin_only': '❌ Only admin can use this command!',
        'checking': '🔍 Checking membership...'
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
        'admin_only': '❌ فقط المدير يمكنه استخدام هذا الأمر!',
        'checking': '🔍 التحقق من العضوية...'
    }
}

# ========== KANAL KONTROLÜ ==========
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının kanala üye olup olmadığını kontrol et"""
    config = load_config()
    
    if not config.get('required_channel', False) or not config.get('channel_username'):
        return True
    
    if is_admin(user_id):
        return True
    
    try:
        channel_username = config['channel_username']
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        chat_id = config.get('channel_id')
        if chat_id:
            try:
                chat_member = await context.bot.get_chat_member(
                    chat_id=chat_id,
                    user_id=user_id
                )
            except:
                chat_member = await context.bot.get_chat_member(
                    chat_id=f"@{channel_username}",
                    user_id=user_id
                )
        else:
            chat_member = await context.bot.get_chat_member(
                chat_id=f"@{channel_username}",
                user_id=user_id
            )
        
        if chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, 
                                 ChatMemberStatus.OWNER, ChatMemberStatus.CREATOR]:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Channel check error: {e}")
        return False

async def show_subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE, user_lang='en'):
    """Abonelik gerekli mesajını göster"""
    config = load_config()
    lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
    
    if not config.get('channel_invite_link'):
        if update.message:
            await update.message.reply_text("❌ Channel invite link is not set! Admin must set it first.")
        return
    
    keyboard = [
        [InlineKeyboardButton(lang_data['subscribe_button'], url=config.get('channel_invite_link'))],
        [InlineKeyboardButton(lang_data['check_button'], callback_data='check_subscription')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            lang_data['not_subscribed'],
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            lang_data['not_subscribed'],
            reply_markup=reply_markup
        )

# ========== ANA KOMUTLAR ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu işleyici"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    config = load_config()
    if config.get('required_channel', False) and config.get('channel_username'):
        is_member = await check_channel_membership(update.effective_user.id, context)
        
        if not is_member:
            user_lang = user_data.get(user_id, {}).get('lang', 'en')
            await show_subscription_required(update, context, user_lang)
            return
    
    if user_id not in user_data or 'lang' not in user_data[user_id]:
        await show_language_selection(update, context)
    else:
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
            "👋 Please choose a language / تكایە زمانێک هەڵبژێرە / الرجاء اختيار لغة:",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "👋 Please choose a language / تكایە زمانێک هەڵبژێرە / الرجاء اختيار لغة:",
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
    """/join komutu - Admin paneli"""
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
            "🛠️ **Admin Panel - Required Channel Settings**\n\n"
            f"👑 **Admin ID:** {config.get('admin_id')}\n"
            f"📢 **Current Channel:** {config.get('channel_username', 'Not set')}\n"
            f"🆔 **Channel ID:** {config.get('channel_id', 'Not set')}\n"
            f"🔗 **Invite Link:** {config.get('channel_invite_link', 'Not set')}\n"
            f"📌 **Required?:** {'✅ YES' if config.get('required_channel') else '❌ NO'}\n\n"
            "**Commands:**\n"
            "/join @channelname - Set channel\n"
            "/join link https://t.me/... - Set invite link\n"
            "/join on - Enable required subscription\n"
            "/join off - Disable required subscription\n"
            "/join status - Show current status\n"
            "/join test - Test channel membership"
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
            f"Channel ID: {config.get('channel_id', 'Not set')}\n"
            f"Required: {'✅ ENABLED' if config.get('required_channel') else '❌ DISABLED'}\n"
            f"Invite Link: {config.get('channel_invite_link', 'Not set')}"
        )
        await update.message.reply_text(status_text)
        
    elif command == "test":
        if not config.get('channel_username'):
            await update.message.reply_text("❌ No channel set!")
            return
        try:
            channel_username = config['channel_username']
            if channel_username.startswith('@'):
                channel_username = channel_username[1:]
            chat = await context.bot.get_chat(chat_id=f"@{channel_username}")
            config['channel_id'] = chat.id
            save_config(config)
            await update.message.reply_text(f"✅ Channel accessible!\nTitle: {chat.title}\nID: {chat.id}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        
    elif command == "link" and len(context.args) > 1:
        link = context.args[1]
        if not link.startswith('https://t.me/'):
            await update.message.reply_text("❌ Invalid link! Must start with https://t.me/")
            return
        config['channel_invite_link'] = link
        save_config(config)
        await update.message.reply_text(f"✅ Invite link updated: {link}")
        
    elif command.startswith('@'):
        try:
            chat = await context.bot.get_chat(chat_id=command)
            config['channel_username'] = command
            config['channel_id'] = chat.id
            if not config.get('channel_invite_link'):
                channel_name = command[1:]
                config['channel_invite_link'] = f"https://t.me/{channel_name}"
            save_config(config)
            await update.message.reply_text(
                f"✅ Channel set!\nName: {chat.title}\nID: {chat.id}\nLink: {config['channel_invite_link']}"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        
    else:
        await update.message.reply_text("❌ Invalid command! Type /join for help.")

# ========== BUTON İŞLEMLERİ ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    config = load_config()
    
    if query.data == 'check_subscription':
        user_lang = user_data.get(user_id, {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        
        await query.edit_message_text(text=lang_data['checking'])
        
        if config.get('required_channel', False):
            is_member = await check_channel_membership(query.from_user.id, context)
            
            if is_member:
                await query.edit_message_text(text=lang_data['already_subscribed'])
                if user_id not in user_data or 'lang' not in user_data[user_id]:
                    await show_language_selection(update, context)
                else:
                    await show_welcome_message(update, context, user_data[user_id]['lang'])
            else:
                await show_subscription_required(update, context, user_lang)
        return
    
    if config.get('required_channel', False) and config.get('channel_username'):
        is_member = await check_channel_membership(query.from_user.id, context)
        if not is_member:
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
        await show_welcome_message(update, context, lang_code)
        
    elif query.data == 'change_lang':
        await show_language_selection(update, context)
        
    elif query.data == 'help':
        user_lang = user_data.get(user_id, {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        await query.message.reply_text(lang_data['help_text'])

# ========== BOT BAŞLATMA ==========
async def main():
    """Botu başlat"""
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN environment variable not set!")
        print("Go to Railway → Variables → Add BOT_TOKEN")
        return
    
    # Health check server'ı başlat
    await start_health_server()
    print("✅ Health server started")
    
    # Config yükle
    config = load_config()
    
    # Bot uygulamasını oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komut işleyicileri
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('join', join_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Botu başlat
    print("🤖 Bot starting...")
    print(f"👑 Admin ID: {config.get('admin_id')}")
    print(f"📢 Channel: {config.get('channel_username', 'Not set')}")
    
    # Polling'i başlat
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Bot started successfully!")
    
    # Sonsuz döngüde kal
    while True:
        await asyncio.sleep(3600)  # Her saat uyan

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
