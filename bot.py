import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot tokeninizi buraya yapıştırın
TOKEN = "BURAYA_BOT_TOKENINIZI_YAPIŞTIRIN"

# /start komutuna cevap
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Merhaba! Ben çalışıyorum! 🎉')

# Gelen mesajlara cevap
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Siz dediniz: {update.message.text}')

# Ana fonksiyon
def main():
    # Bot uygulamasını oluştur
    app = Application.builder().token(TOKEN).build()
    
    # Komutları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Botu başlat
    print("🤖 Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
