from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatMemberStatus
import json
import os
import re

# Bot token'ınızı buraya yapıştırın
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Dosya yolları
USER_DATA_FILE = 'user_data.json'
CONFIG_FILE = 'config.json'

# Mesajlar ve butonlar için dil seçenekleri
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
        'already_subscribed': '✅ سوپاس! ئێستا دەتوانیت بۆتەکە بەکاربهێنیت.'
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
        'already_subscribed': '✅ Thank you! You can now use the bot.'
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
        'already_subscribed': '✅ شكراً! يمكنك الآن استخدام البوت.'
    }
}

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
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Varsayılan config
        return {
            "admin_id": "",
            "channel_username": "",
            "channel_invite_link": "",
            "required_channel": False
        }

def save_config(config):
    """Config dosyasını kaydet"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# ========== KANAL KONTROLÜ ==========
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının kanala üye olup olmadığını kontrol et"""
    config = load_config()
    
    # Eğer kanal zorunlu değilse veya kanal ayarlanmamışsa true dön
    if not config.get('required_channel', False) or not config.get('channel_username'):
        return True
    
    try:
        channel_username = config['channel_username']
        # @ işaretini temizle
        if channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        # Kullanıcının kanal durumunu kontrol et
        chat_member = await context.bot.get_chat_member(
            chat_id=f"@{channel_username}",
            user_id=user_id
        )
        
        # Kullanıcının durumunu kontrol et (üye, yönetici, vs.)
        if chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, 
                                 ChatMemberStatus.OWNER, ChatMemberStatus.CREATOR]:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Kanal kontrol hatası: {e}")
        return False

async def show_subscription_required(update: Update, context: ContextTypes.DEFAULT_TYPE, user_lang='en'):
    """Abonelik gerekli mesajını göster"""
    config = load_config()
    lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
    
    keyboard = [
        [InlineKeyboardButton(lang_data['subscribe_button'], url=config.get('channel_invite_link', ''))],
        [InlineKeyboardButton(lang_data['check_button'], callback_data='check_subscription')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        lang_data['not_subscribed'],
        reply_markup=reply_markup
    )

# ========== ANA KOMUTLAR ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu işleyici"""
    user_id = str(update.effective_user.id)
    user_data = load_user_data()
    
    # Kanal kontrolü
    config = load_config()
    if config.get('required_channel', False):
        is_member = await check_channel_membership(update.effective_user.id, context)
        if not is_member:
            # Kullanıcının dilini bul
            user_lang = user_data.get(user_id, {}).get('lang', 'en')
            await show_subscription_required(update, context, user_lang)
            return
    
    # Kullanıcıyı kontrol et
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
    
    await update.message.reply_text(
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
    
    await update.message.reply_text(
        lang_data['welcome'],
        reply_markup=reply_markup
    )

# ========== ADMIN KOMUTLARI ==========
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/join komutu - Admin paneli"""
    config = load_config()
    user_id = str(update.effective_user.id)
    
    # Admin kontrolü
    if user_id != config.get('admin_id'):
        await update.message.reply_text("❌ Bu komutu sadece admin kullanabilir!")
        return
    
    # Eğer argüman yoksa mevcut ayarları göster
    if not context.args:
        current_settings = (
            "🛠️ **Admin Panel - Zorunlu Kanal Ayarları**\n\n"
            f"📢 **Mevcut Kanal:** {config.get('channel_username', 'Ayarlanmamış')}\n"
            f"🔗 **Davet Linki:** {config.get('channel_invite_link', 'Ayarlanmamış')}\n"
            f"📌 **Zorunlu mu?:** {'✅ Evet' if config.get('required_channel') else '❌ Hayır'}\n\n"
            "**Komutlar:**\n"
            "/join kanal_adi - Kanalı ayarla (ör: @kanaladi)\n"
            "/join link davet_linki - Davet linkini ayarla\n"
            "/join on - Zorunlu aboneliği aç\n"
            "/join off - Zorunlu aboneliği kapat\n"
            "/join status - Mevcut durumu göster"
        )
        await update.message.reply_text(current_settings)
        return
    
    command = context.args[0].lower()
    
    if command == "on":
        config['required_channel'] = True
        save_config(config)
        await update.message.reply_text("✅ Zorunlu kanal aboneliği AKTİF edildi!")
        
    elif command == "off":
        config['required_channel'] = False
        save_config(config)
        await update.message.reply_text("✅ Zorunlu kanal aboneliği PASİF edildi!")
        
    elif command == "status":
        status_text = (
            f"📊 **Durum Raporu**\n\n"
            f"Kanal: {config.get('channel_username', 'Ayarlanmamış')}\n"
            f"Zorunlu Abonelik: {'✅ AKTİF' if config.get('required_channel') else '❌ PASİF'}\n"
            f"Davet Linki: {config.get('channel_invite_link', 'Ayarlanmamış')}"
        )
        await update.message.reply_text(status_text)
        
    elif command == "link" and len(context.args) > 1:
        link = context.args[1]
        if not link.startswith('https://t.me/'):
            await update.message.reply_text("❌ Geçersiz link! Link https://t.me/ ile başlamalı.")
            return
        config['channel_invite_link'] = link
        save_config(config)
        await update.message.reply_text(f"✅ Davet linki güncellendi: {link}")
        
    elif command.startswith('@') or ('t.me/' in command):
        # Kanal kullanıcı adı
        if command.startswith('@'):
            channel_username = command
        else:
            # t.me/kanaladi formatından @kanaladi formatına çevir
            if 't.me/' in command:
                channel_username = '@' + command.split('t.me/')[-1]
            else:
                channel_username = '@' + command
        
        config['channel_username'] = channel_username
        save_config(config)
        await update.message.reply_text(f"✅ Kanal ayarlandı: {channel_username}")
        
    else:
        await update.message.reply_text("❌ Geçersiz komut! /join yazarak yardım alın.")

# ========== BUTON İŞLEMLERİ ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_data = load_user_data()
    config = load_config()
    
    # Abonelik kontrol butonu
    if query.data == 'check_subscription':
        if config.get('required_channel', False):
            is_member = await check_channel_membership(query.from_user.id, context)
            if is_member:
                # Kullanıcının dilini bul
                user_lang = user_data.get(user_id, {}).get('lang', 'en')
                lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
                await query.edit_message_text(text=lang_data['already_subscribed'])
                
                # Dil seçimi veya hoşgeldin mesajı göster
                if user_id not in user_data or 'lang' not in user_data[user_id]:
                    await show_language_selection(update, context)
                else:
                    await show_welcome_message(update, context, user_data[user_id]['lang'])
            else:
                # Hala abone değil
                user_lang = user_data.get(user_id, {}).get('lang', 'en')
                await show_subscription_required(update, context, user_lang)
        return
    
    if query.data.startswith('lang_'):
        # Kanal kontrolü (dil seçimi sırasında)
        if config.get('required_channel', False):
            is_member = await check_channel_membership(query.from_user.id, context)
            if not is_member:
                lang_code = query.data.split('_')[1]
                await show_subscription_required(update, context, lang_code)
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
        # Dil değiştirme
        await show_language_selection(update, context)
        
    elif query.data == 'help':
        # Yardım butonu
        user_lang = user_data.get(user_id, {}).get('lang', 'en')
        lang_data = LANGUAGES.get(user_lang, LANGUAGES['en'])
        await query.message.reply_text(lang_data['help_text'])

# ========== BOT BAŞLATMA ==========
def main():
    """Botu başlat"""
    # Token kontrolü
    if not BOT_TOKEN:
        print("❌ Lütfen BOT_TOKEN değerini ayarlayın!")
        return
    
    # Config dosyasını kontrol et
    config = load_config()
    if not config.get('admin_id'):
        print("⚠️ UYARI: Admin ID ayarlanmamış! /join komutu çalışmayacak.")
        print("Lütfen config.json dosyasına admin_id ekleyin.")
    
    # Bot uygulamasını oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komut işleyicileri
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('join', join_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Botu başlat
    print("🤖 Bot başlatılıyor...")
    print(f"👑 Admin ID: {config.get('admin_id', 'Ayarlanmamış')}")
    print(f"📢 Kanal: {config.get('channel_username', 'Ayarlanmamış')}")
    print(f"🔒 Zorunlu Abonelik: {config.get('required_channel', False)}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
