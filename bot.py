import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token'i environment variable'dan al
TOKEN = os.getenv("TOKEN")

# /start komutuna cevap
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f'Merhaba {user.first_name}! 👋\n'
        f'Ben basit bir Telegram botuyum.\n'
        f'Sana yazdıklarını tekrar ederim!\n\n'
        f'Komutlar:\n'
        f'/start - Botu başlat\n'
        f'/help - Yardım mesajı\n'
        f'/echo [mesaj] - Mesajını yankılar'
    )
    logger.info(f"/start komutunu kullanan: {user.first_name} (ID: {user.id})")

# /help komutuna cevap
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Yardım Menüsü:\n\n'
        '• Sadece bana bir şey yaz, sana aynısını söylerim!\n'
        '• Komutlar:\n'
        '  /start - Botu başlat\n'
        '  /help - Bu mesajı göster\n'
        '  /echo [mesaj] - Mesajını yankıla\n\n'
        'Örnek: /echo Merhaba Dünya!'
    )

# /echo komutuna cevap
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kullanıcının yazdığı mesajı al
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f'📢 Echo: {text}')
    else:
        await update.message.reply_text('Lütfen bir mesaj yazın. Örnek: /echo Merhaba')

# Normal mesajlara cevap
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.effective_user
    
    # Gelen mesajı logla
    logger.info(f"Mesaj: {user.first_name} (ID: {user.id}): {user_message}")
    
    # Basit cevaplar
    if user_message.lower() in ['merhaba', 'selam', 'hi', 'hello']:
        await update.message.reply_text(f'Merhaba {user.first_name}! 👋')
    elif user_message.lower() in ['nasılsın', 'naber', 'iyi misin']:
        await update.message.reply_text('Teşekkürler, iyiyim! Sen nasılsın? 😊')
    elif 'teşekkür' in user_message.lower() or 'sağ ol' in user_message.lower():
        await update.message.reply_text('Rica ederim! Ne demek 🌟')
    else:
        # Diğer mesajları echo yap
        await update.message.reply_text(f'Siz: "{user_message}"\n\nBot: "{user_message}" 😄')

# Hata handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# Ana fonksiyon
def main():
    # Token kontrolü
    if not TOKEN:
        logger.error("❌ HATA: TOKEN bulunamadı!")
        print("=" * 50)
        print("❌ HATA: TOKEN bulunamadı!")
        print("Lütfen Railway'da TOKEN variable ekleyin:")
        print("1. Railway projenize girin")
        print("2. 'Variables' sekmesine tıklayın")
        print("3. 'New Variable' butonuna basın")
        print("4. Name: TOKEN")
        print("5. Value: BotFather'dan aldığınız tokeni yapıştırın")
        print("6. 'Add' butonuna basın")
        print("7. 'Deployments' sekmesinde 'Redeploy' yapın")
        print("=" * 50)
        return
    
    logger.info("🤖 Bot başlatılıyor...")
    print("🤖 Bot başlatılıyor...")
    print(f"Token ilk 10 karakteri: {TOKEN[:10]}...")
    
    try:
        # Bot uygulamasını oluştur
        app = Application.builder().token(TOKEN).build()
        
        # Komut handler'larını ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("echo", echo))
        
        # Mesaj handler'ını ekle
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Hata handler'ını ekle
        app.add_error_handler(error_handler)
        
        # Botu başlat
        logger.info("✅ Bot başarıyla başlatıldı!")
        print("✅ Bot başarıyla başlatıldı!")
        print("📱 Telegram'da botunuzu açıp /start yazın")
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Bot başlatılırken hata: {e}")
        print(f"❌ Bot başlatılırken hata: {e}")
        print("\nOlası sorunlar:")
        print("1. Token yanlış olabilir")
        print("2. Internet bağlantınızı kontrol edin")
        print("3. Railway'da TOKEN variable doğru eklenmiş mi?")

if __name__ == "__main__":
    main()
