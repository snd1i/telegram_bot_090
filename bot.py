import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.error import TelegramError

# ============ AYARLAR ============
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OWNER_ID = int(os.environ.get('TELEGRAM_OWNER_ID', '5541236874'))

# Kanal bilgilerini saklamak için
user_channels = {}  # {user_id: channel_username}

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ /start KOMUTU ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Owner kontrolü
    if user_id == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("📢 Kanal Ayarla", callback_data='set_channel')],
            [InlineKeyboardButton("📤 Duyuru Yap", callback_data='make_announcement')],
            [InlineKeyboardButton("ℹ️ Yardım", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'👑 Merhaba Sahip {user.first_name}!\n\n'
            f'Bot kontrol panelinize hoşgeldiniz.\n'
            f'Lütfen bir seçenek seçin:',
            reply_markup=reply_markup
        )
    else:
        # Normal kullanıcılar için
        await update.message.reply_text(
            f'Merhaba {user.first_name}!\n'
            f'Bu bot sadece yönetici tarafından kullanılabilir.'
        )

# ============ BUTON İŞLEMLERİ ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Sadece owner butonlara tıklayabilir
    if user_id != OWNER_ID:
        await query.edit_message_text("❌ Bu işlemi yapma yetkiniz yok.")
        return
    
    if query.data == 'set_channel':
        # Kanal ayarlama
        await query.edit_message_text(
            "📢 **Kanal Ayarlama**\n\n"
            "Lütfen kanalınızın @username'ini gönderin.\n"
            "Örnek: @snd_yatirim\n\n"
            "Veya kanal ID'sini gönderin:\n"
            "Örnek: -1001234567890\n\n"
            "İptal için /start yazın."
        )
        # Kanal username bekliyoruz
        context.user_data['awaiting_channel'] = True
        
    elif query.data == 'make_announcement':
        # Kanal kontrolü
        if OWNER_ID not in user_channels:
            keyboard = [[InlineKeyboardButton("📢 Kanal Ayarla", callback_data='set_channel')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Önce bir kanal ayarlamanız gerekiyor!",
                reply_markup=reply_markup
            )
            return
        
        await query.edit_message_text(
            "📤 **Duyuru Gönder**\n\n"
            "Şimdi duyurunuzu gönderin:\n"
            "• Sadece metin\n"
            "• Resim + altyazı\n"
            "• Video + altyazı\n\n"
            "Gönderdiğiniz her şey kanala iletilecektir.\n"
            "İptal için /start yazın."
        )
        context.user_data['awaiting_announcement'] = True
        
    elif query.data == 'help':
        await query.edit_message_text(
            "🤖 **Bot Kullanım Kılavuzu**\n\n"
            "1. /start - Botu başlat\n"
            "2. 📢 Kanal Ayarla - Duyuru yapılacak kanalı seç\n"
            "3. 📤 Duyuru Yap - Kanalınıza duyuru gönder\n\n"
            "💡 Önemli:\n"
            "• Botun kanalda admin olması gerekir\n"
            "• Kanal @username veya ID ile eklenebilir\n"
            "• Resim/video ile birlikte altyazı ekleyebilirsiniz"
        )

# ============ KANAL KAYDETME ============
async def save_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        return
    
    if context.user_data.get('awaiting_channel'):
        channel_input = update.message.text.strip()
        
        # @ işareti kontrolü
        if not channel_input.startswith('@') and not channel_input.startswith('-100'):
            await update.message.reply_text(
                "❌ Geçersiz kanal formatı!\n"
                "@username veya -1001234567890 formatında olmalı."
            )
            return
        
        try:
            # Kanalı kontrol et
            chat = await context.bot.get_chat(channel_input)
            user_channels[OWNER_ID] = channel_input
            
            # Kontrol mesajı gönder
            test_msg = await context.bot.send_message(
                chat_id=channel_input,
                text="✅ Bot bağlantı testi başarılı!\nBu kanala duyuru gönderebilirim."
            )
            await test_msg.delete()  # Test mesajını sil
            
            await update.message.reply_text(
                f"✅ Kanal başarıyla ayarlandı!\n\n"
                f"Kanal: {chat.title}\n"
                f"Kullanıcı adı: {chat.username or 'Yok'}\n"
                f"ID: {chat.id}\n\n"
                f"Artık duyuru gönderebilirsiniz. /start yazın."
            )
            
        except TelegramError as e:
            await update.message.reply_text(
                f"❌ Kanal eklenemedi!\n\n"
                f"Hata: {str(e)}\n\n"
                f"Lütfen kontrol edin:\n"
                f"1. Bot kanalda admin mi?\n"
                f"2. Kanal adı doğru mu?\n"
                f"3. Kanal private değil mi?"
            )
        finally:
            context.user_data['awaiting_channel'] = False
    
    elif context.user_data.get('awaiting_announcement'):
        # Duyuru gönderme
        await send_announcement(update, context)

# ============ DUYURU GÖNDERME ============
async def send_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        return
    
    channel = user_channels.get(OWNER_ID)
    if not channel:
        await update.message.reply_text("❌ Önce kanal ayarlayın! /start")
        return
    
    message = update.message
    
    try:
        # Butonlu mesaj
        keyboard = [[
            InlineKeyboardButton("📢 Kanalıma Katıl", url=f"https://t.me/snd_yatirim"),
            InlineKeyboardButton("✅ Katıldım", callback_data='joined')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # RESİM varsa
        if message.photo:
            photo = message.photo[-1]
            caption = message.caption or "📢 Yeni Duyuru!"
            
            sent_msg = await context.bot.send_photo(
                chat_id=channel,
                photo=photo.file_id,
                caption=caption + "\n\n@SND_YATIRIM",
                reply_markup=reply_markup
            )
            
            await update.message.reply_text(
                f"✅ Resimli duyuru gönderildi!\n"
                f"Kanal: {channel}\n"
                f"Mesaj ID: {sent_msg.message_id}"
            )
        
        # VIDEO varsa
        elif message.video:
            video = message.video
            caption = message.caption or "📢 Yeni Duyuru!"
            
            sent_msg = await context.bot.send_video(
                chat_id=channel,
                video=video.file_id,
                caption=caption + "\n\n@SND_YATIRIM",
                reply_markup=reply_markup
            )
            
            await update.message.reply_text(
                f"✅ Videolu duyuru gönderildi!\n"
                f"Kanal: {channel}\n"
                f"Mesaj ID: {sent_msg.message_id}"
            )
        
        # SADECE METİN varsa
        elif message.text:
            text = message.text
            
            sent_msg = await context.bot.send_message(
                chat_id=channel,
                text=text + "\n\n@SND_YATIRIM",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            await update.message.reply_text(
                f"✅ Duyuru gönderildi!\n"
                f"Kanal: {channel}\n"
                f"Mesaj ID: {sent_msg.message_id}"
            )
        
        context.user_data['awaiting_announcement'] = False
        
    except TelegramError as e:
        await update.message.reply_text(f"❌ Gönderilemedi! Hata: {str(e)}")

# ============ ANA FONKSİYON ============
def main():
    """Botu başlat"""
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN bulunamadı!")
        return
    
    # Uygulamayı oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları ekle
    application.add_handler(CommandHandler("start", start))
    
    # Butonları ekle
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Mesaj işleyicileri
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        save_channel
    ))
    
    # Medya mesajları (resim/video)
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO,
        send_announcement
    ))
    
    # Başlat
    logger.info("🤖 Bot başlatılıyor... Sahip: %s", OWNER_ID)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
