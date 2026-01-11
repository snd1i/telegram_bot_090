# commands.py - Tüm yeni komutlar burada

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# ========== BASİT KOMUT ÖRNEKLERİ ==========

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Basit selamlama komutu"""
    await update.message.reply_text("👋 Merhaba! Nasılsınız?")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saat komutu"""
    from datetime import datetime
    now = datetime.now()
    await update.message.reply_text(f"🕒 Saat: {now.strftime('%H:%M:%S')}")

async def date_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tarih komutu"""
    from datetime import datetime
    today = datetime.now()
    await update.message.reply_text(f"📅 Tarih: {today.strftime('%d/%m/%Y')}")

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo komutu - yazılanı tekrar eder"""
    if not context.args:
        await update.message.reply_text("❌ Kullanım: /echo <mesaj>")
        return
    
    text = " ".join(context.args)
    await update.message.reply_text(f"📢 {text}")

async def help2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ek yardım komutu"""
    help_text = (
        "🆘 **Ek Komutlar**\n\n"
        "👋 /hello - Selamlama\n"
        "🕒 /time - Saati göster\n"
        "📅 /date - Tarihi göster\n"
        "📢 /echo - Mesajı tekrarla\n"
        "ℹ️ /help2 - Bu yardım mesajı"
    )
    await update.message.reply_text(help_text)

# ========== KOMUTLARI BOT'A EKLEYEN FONKSİYON ==========
def setup_commands(application):
    """Tüm komutları bot'a ekler"""
    
    # Komut listesi - ÇOK KOLAY EKLEME!
    command_list = [
        ('hello', hello_command),
        ('time', time_command),
        ('date', date_command),
        ('echo', echo_command),
        ('help2', help2_command),
    ]
    
    # Her komutu bot'a ekle
    for command_name, command_function in command_list:
        application.add_handler(CommandHandler(command_name, command_function))
    
    print(f"✅ {len(command_list)} yeni komut eklendi:")
    for cmd, _ in command_list:
        print(f"   • /{cmd}")
