# extensions/basic.py - Temel komutlar
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot çalışıyor mu?"""
    await update.message.reply_text("🏓 Pong! Bot çalışıyor!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım komutu"""
    help_text = (
        "🆘 **Yardım**\n\n"
        "🏓 /ping - Bot çalışıyor mu?\n"
        "🆘 /help - Bu mesaj\n"
        "ℹ️ /info - Bot bilgileri\n"
        "👋 /hello - Selamlama\n"
        "🕒 /time - Saati göster\n"
        "📅 /date - Tarihi göster"
    )
    await update.message.reply_text(help_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot bilgileri"""
    await update.message.reply_text(
        "🤖 **Prompt Bot**\n\n"
        "📍 Özellikler:\n"
        "• 3 dil desteği\n"
        "• Zorunlu kanal aboneliği\n"
        "• Admin paneli\n"
        "• Genişletilebilir yapı\n\n"
        "👨‍💻 Geliştirici: Siz"
    )

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Selamlama"""
    await update.message.reply_text("👋 Merhaba! Nasılsınız?")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saat"""
    from datetime import datetime
    now = datetime.now().strftime('%H:%M:%S')
    await update.message.reply_text(f"🕒 Saat: {now}")

async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tarih"""
    from datetime import datetime
    today = datetime.now().strftime('%d/%m/%Y')
    await update.message.reply_text(f"📅 Tarih: {today}")

# BU FONKSİYON ZORUNLU - loader.py bunu arar
def setup(app):
    """Tüm komutları bot'a ekler"""
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("hello", hello_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("date", date_command))
    print("✅ Basic commands loaded!")
