# extensions/basic.py - SADECE /help KOMUTU
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 **Prompt Bot - Yardım**\n\n"
        "📍 **Ana Komutlar:**\n"
        "✅ /start - Botu başlat\n"
        "🆘 /help - Bu yardım mesajı\n"
        "🌍 Dil değiştirmek için 'Change Language' butonunu kullanın\n\n"
        "👑 **Admin Komutları:**\n"
        "⚙️ /settings - Admin paneli\n\n"
        "📢 **Ek Özellikler:**\n"
        "• 3 dil desteği\n"
        "• Zorunlu kanal aboneliği\n"
        "• Genişletilebilir yapı"
    )
    await update.message.reply_text(help_text)

def setup(app):
    """Sadece /help komutunu ekler"""
    app.add_handler(CommandHandler("help", help_command))
    print("✅ Basic extension loaded: /help")
