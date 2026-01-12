# extensions/basic.py - DİL DESTEKLİ /help KOMUTU
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import json

# ========== DOSYA İŞLEMLERİ ==========
def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
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
        "🌍 بۆ گۆڕینی زمان، دوگمەی 'Change Language' بەکاربهێنە\n\n"
        "📢 **تایبەتمەندیەکانی تر:**\n"
        "• پشتیوانی لە 3 زمان\n"
        "• ئەندامێتییەکی ناچاری کەناڵ\n"
        "• پێکھاتەی فراوانکراو"
    ),
    'en': (
        "🤖 **Prompt Bot - Help**\n\n"
        "📍 **Main Commands:**\n"
        "✅ /start - Start the bot\n"
        "🆘 /help - This help message\n"
        "🌍 To change language, use the 'Change Language' button\n\n"
        "📢 **Additional Features:**\n"
        "• Support for 3 languages\n"
        "• Mandatory channel subscription\n"
        "• Extensible structure"
    ),
    'ar': (
        "🤖 **Prompt Bot - المساعدة**\n\n"
        "📍 **الأوامر الرئيسية:**\n"
        "✅ /start - بدء البوت\n"
        "🆘 /help - رسالة المساعدة هذه\n"
        "🌍 لتغيير اللغة، استخدم زر 'تغيير اللغة'\n\n"
        "📢 **ميزات إضافية:**\n"
        "• دعم 3 لغات\n"
        "• اشتراك قناة إلزامي\n"
        "• هيكل قابل للتوسيع"
    )
}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dil destekli help komutu"""
    user_id = update.effective_user.id
    user_lang = get_user_lang(user_id)
    
    await update.message.reply_text(HELP_TEXTS.get(user_lang, HELP_TEXTS['en']))

def setup(app):
    """Sadece /help komutunu ekler"""
    app.add_handler(CommandHandler("help", help_command))
    print("✅ Basic extension loaded: /help (multi-language)")
