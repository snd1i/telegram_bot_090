# extensions/basic.py - DİL DESTEKLİ /help KOMUTU
import json
import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# ========== DOSYA İŞLEMLERİ ==========
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except:
        return {}

def get_user_lang(user_id):
    """Kullanıcının dilini al"""
    user_data = load_user_data()
    return user_data.get(str(user_id), {}).get('lang', 'en')

# ========== DİL MESAJLARI ==========
HELP_TEXTS = {
    'ku': (
        "🤖 **Prompt Bot - یارمەتی**\n\n"
        "📍 **کۆمەندە سەرەکیەکان:**\n"
        "✅ /start - دەستپێکردنی بۆت\n"
        "🆘 /help - ئەم پەیامی یارمەتیە\n"
        "⚙️ /settings - پانێلی ئەدمین (تەنها ئەدمین)\n\n"
        "📢 **تایبەتمەندیەکانی تر:**\n"
        "• پشتیوانی لە 3 زمان\n"
        "• سیستەمی ڕاگەیاندنی ئەدمین\n"
        "• بەڕێوەبردنی بەکارهێنەر"
    ),
    'en': (
        "🤖 **Prompt Bot - Help**\n\n"
        "📍 **Main Commands:**\n"
        "✅ /start - Start the bot\n"
        "🆘 /help - This help message\n"
        "⚙️ /settings - Admin panel (admin only)\n\n"
        "📢 **Additional Features:**\n"
        "• Support for 3 languages\n"
        "• Admin broadcast system\n"
        "• User management"
    ),
    'ar': (
        "🤖 **Prompt Bot - المساعدة**\n\n"
        "📍 **الأوامر الرئيسية:**\n"
        "✅ /start - بدء البوت\n"
        "🆘 /help - رسالة المساعدة هذه\n"
        "⚙️ /settings - لوحة المشرف (المشرف فقط)\n\n"
        "📢 **ميزات إضافية:**\n"
        "• دعم 3 لغات\n"
        "• نظام بث المشرف\n"
        "• إدارة المستخدم"
    )
}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dil destekli help komutu"""
    user_id = update.effective_user.id
    user_lang = get_user_lang(user_id)
    
    await update.message.reply_text(
        HELP_TEXTS.get(user_lang, HELP_TEXTS['en']),
        parse_mode='Markdown'
    )

def setup(app):
    """Sadece /help komutunu ekler"""
    app.add_handler(CommandHandler("help", help_command))
    print("✅ Basic extension loaded: /help (multi-language)")
