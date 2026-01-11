import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# ============ AYARLAR ============
# Railway'da AYARLANACAK:
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OWNER_ID = int(os.environ.get('TELEGRAM_OWNER_ID', '7140249921'))
CHANNEL_USERNAME = os.environ.get('TELEGRAM_CHANNEL_USERNAME', '@snd_yatirim')

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ============ ABONE KONTROLÜ ============
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Kullanıcı kanalda mı kontrol et"""
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ============ /start KOMUTU ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Abonelik kontrolü
    is_member = await is_user_member(user_id, context)
    
    if is_member:
        # ZATEN ABONE OLANLAR
        await update.message.reply_text(
            f'✅ Hoşgeldin {user.first_name}!\n'
            f'Zaten kanalımıza abonesin. Botu kullanabilirsin.\n\n'
            f'📢 Duyuru yapmak için: /duyuru <mesajınız>'
        )
    else:
        # ABONE OLMAYANLAR
        keyboard = [
            [InlineKeyboardButton("📢 Kanalıma Katıl", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ Abone Oldum", callback_data='check')]
        ]
        from telegram import InlineKeyboardMarkup
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'Merhaba {user.first_name}! 👋\n\n'
            f'Botu kullanmak için kanalıma abone ol:\n'
            f'{CHANNEL_USERNAME}\n\n'
            f'Katıldıktan sonra "✅ Abone Oldum" butonuna tıkla:',
            reply_markup=reply_markup
        )

# ============ BUTON TIKLAMA ============
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == 'check':
        # Abonelik kontrolü
        is_member = await is_user_member(user_id, context)
        
        if is_member:
            await query.edit_message_text(
                "🎉 Teşekkürler! Botu şimdi kullanabilirsin.\n"
                "Komutlar: /start /duyuru"
            )
        else:
            await query.edit_message_text(
                "❌ Henüz kanalda değilsin.\n"
                "Lütfen önce katıl:\n"
                f"{CHANNEL_USERNAME}\n\n"
                "Katıldıktan sonra /start yaz."
            )

# ============ /duyuru KOMUTU ============
async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # SADECE SAHİP
    if str(user_id) != str(OWNER_ID):
        await update.message.reply_text("❌ Bu komutu sadece benim sahibim kullanabilir.")
        return
    
    # Mesaj kontrolü
    if not context.args:
        await update.message.reply_text(
            "📢 Kullanım:\n"
            "/duyuru <mesajınız>\n\n"
            "Örnek: /duyuru Yeni video yüklendi!"
        )
        return
    
    # Mesajı al
    message_text = ' '.join(context.args)
    
    # Buton oluştur
    keyboard = [[InlineKeyboardButton("📺 Kanalıma Katıl", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Duyuru hazır!\n\n"
        f"Mesaj: {message_text}\n\n"
        f"Bu mesajı kanala göndermek için geliştirilecek.",
        reply_markup=reply_markup
    )

# ============ ANA PROGRAM ============
def main():
    """Botu başlat"""
    if not BOT_TOKEN:
        print("❌ HATA: TELEGRAM_BOT_TOKEN bulunamadı!")
        print("Railway'da Environment Variables ekleyin:")
        print("1. TELEGRAM_BOT_TOKEN")
        print("2. TELEGRAM_OWNER_ID")
        print("3. TELEGRAM_CHANNEL_USERNAME")
        return
    
    # Botu oluştur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru))
    app.add_handler(CallbackQueryHandler(button_click))
    
    # Başlat
    print("🤖 Bot başlatılıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
