import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loglama ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin ID'si
ADMIN_ID = 5541236874

# Kullanıcı veritabanı
USER_DATA_FILE = "users.txt"

# =================== VERİTABANI İŞLEMLERİ ===================
def load_users():
    """Kayıtlı kullanıcıları yükle"""
    try:
        if not os.path.exists(USER_DATA_FILE):
            return set()
        with open(USER_DATA_FILE, "r") as f:
            users = set(line.strip() for line in f if line.strip())
            logger.info(f"{len(users)} kullanıcı yüklendi")
            return users
    except Exception as e:
        logger.error(f"Kullanıcı yükleme hatası: {e}")
        return set()

def save_user(user_id):
    """Yeni kullanıcı kaydet"""
    try:
        users = load_users()
        user_str = str(user_id)
        if user_str not in users:
            users.add(user_str)
            with open(USER_DATA_FILE, "w") as f:
                f.write("\n".join(users))
            logger.info(f"Yeni kullanıcı kaydedildi: {user_id}")
    except Exception as e:
        logger.error(f"Kullanıcı kaydetme hatası: {e}")

# =================== KOMUTLAR ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botu başlatan komut"""
    user = update.effective_user
    user_id = user.id
    
    save_user(user_id)
    
    welcome_text = f"""
    👋 Merhaba {user.first_name}!
    
    Ben duyuru botuyum. Adminler önemli duyuruları buradan paylaşabilir.
    
    /start - Botu başlat
    /help - Yardım
    """
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım komutu"""
    help_text = """
    🤖 **BOT KOMUTLARI**
    
    /start - Botu başlat
    /help - Yardım mesajı
    
    ⚠️ Duyurular sadece admin tarafından yapılır.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin yardım komutu"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    help_text = """
    🔧 **ADMIN KOMUTLARI**
    
    /duyuru - Duyuru gönderme menüsü
    /istatistik - Bot istatistikleri
    /kullanicilar - Tüm kullanıcılar
    /iptal - İşlemi iptal et
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İstatistik komutu"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    users = load_users()
    await update.message.reply_text(f"📊 **İstatistikler**\n\n✅ Toplam kullanıcı: {len(users)}")

# =================== DUYURU SİSTEMİ ===================
async def announce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru komutu"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Metin Duyurusu", callback_data='text_announce')],
        [InlineKeyboardButton("🖼️ Resimli Duyuru", callback_data='photo_announce')],
        [InlineKeyboardButton("📊 İstatistik", callback_data='stats')],
        [InlineKeyboardButton("❌ İptal", callback_data='cancel')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 **DUYURU SİSTEMİ**\n\n"
        "Ne tür bir duyuru göndermek istiyorsunuz?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ Yetkiniz yok!")
        return
    
    data = query.data
    
    if data == 'text_announce':
        await query.edit_message_text(
            "📝 **Metin Duyurusu**\n\n"
            "Lütfen göndermek istediğiniz metni yazın:"
        )
        context.user_data['mode'] = 'waiting_text'
        
    elif data == 'photo_announce':
        await query.edit_message_text(
            "🖼️ **Resimli Duyuru**\n\n"
            "Lütfen göndermek istediğiniz resmi gönderin:"
        )
        context.user_data['mode'] = 'waiting_photo'
        
    elif data == 'stats':
        users = load_users()
        await query.edit_message_text(f"📊 **İstatistikler**\n\nToplam kullanıcı: {len(users)}")
        
    elif data == 'cancel':
        if 'mode' in context.user_data:
            del context.user_data['mode']
        await query.edit_message_text("✅ İşlem iptal edildi.")
    
    elif data == 'confirm_send':
        # Duyuruyu gönder
        users = load_users()
        total = len(users)
        success = 0
        failed = 0
        
        await query.edit_message_text(f"🔄 Duyuru gönderiliyor...\n\nToplam: {total} kullanıcı")
        
        announcement = context.user_data.get('announcement', {})
        
        for user_id_str in users:
            try:
                if announcement.get('type') == 'photo':
                    await context.bot.send_photo(
                        chat_id=int(user_id_str),
                        photo=announcement.get('photo_id'),
                        caption=announcement.get('text', ''),
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_message(
                        chat_id=int(user_id_str),
                        text=announcement.get('text', ''),
                        parse_mode='Markdown'
                    )
                success += 1
            except Exception as e:
                logger.error(f"Kullanıcı {user_id_str} gönderilemedi: {e}")
                failed += 1
            await asyncio.sleep(0.1)  # Rate limit için bekle
        
        # Temizle
        if 'mode' in context.user_data:
            del context.user_data['mode']
        if 'announcement' in context.user_data:
            del context.user_data['announcement']
        
        await query.edit_message_text(
            f"✅ **Duyuru Tamamlandı!**\n\n"
            f"✅ Başarılı: {success}\n"
            f"❌ Başarısız: {failed}\n"
            f"📊 Toplam: {total}"
        )
    
    elif data == 'cancel_send':
        # Temizle
        if 'mode' in context.user_data:
            del context.user_data['mode']
        if 'announcement' in context.user_data:
            del context.user_data['announcement']
        
        await query.edit_message_text("✅ Duyuru iptal edildi.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mesajları işle"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    mode = context.user_data.get('mode')
    
    if mode == 'waiting_text':
        text = update.message.text
        
        if text.startswith('/'):
            return
        
        # Onay butonları
        keyboard = [
            [InlineKeyboardButton("✅ Gönder", callback_data='confirm_send')],
            [InlineKeyboardButton("❌ İptal", callback_data='cancel_send')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['announcement'] = {
            'type': 'text',
            'text': text
        }
        
        users = load_users()
        
        await update.message.reply_text(
            f"📝 **Duyuru Önizleme**\n\n"
            f"{text}\n\n"
            f"📊 Bu duyuru {len(users)} kullanıcıya gönderilecek.\n"
            f"Göndermek istiyor musunuz?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        del context.user_data['mode']
    
    elif mode == 'waiting_photo':
        if update.message.photo:
            photo = update.message.photo[-1]
            context.user_data['temp_photo'] = photo.file_id
            context.user_data['mode'] = 'waiting_caption'
            
            await update.message.reply_text(
                "✅ Fotoğraf alındı.\n"
                "Şimdi açıklama metnini yazın (isteğe bağlı):"
            )
        else:
            await update.message.reply_text("Lütfen bir fotoğraf gönderin!")
    
    elif mode == 'waiting_caption':
        caption = update.message.text if update.message.text else ""
        photo_id = context.user_data.get('temp_photo')
        
        # Onay butonları
        keyboard = [
            [InlineKeyboardButton("✅ Gönder", callback_data='confirm_send')],
            [InlineKeyboardButton("❌ İptal", callback_data='cancel_send')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.user_data['announcement'] = {
            'type': 'photo',
            'photo_id': photo_id,
            'text': caption
        }
        
        users = load_users()
        
        preview_text = f"🖼️ **Fotoğraf Duyurusu**\n\n"
        if caption:
            preview_text += f"Açıklama: {caption}\n\n"
        preview_text += f"📊 Bu duyuru {len(users)} kullanıcıya gönderilecek.\n"
        preview_text += f"Göndermek istiyor musunuz?"
        
        await update.message.reply_text(
            preview_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Temizle
        if 'temp_photo' in context.user_data:
            del context.user_data['temp_photo']
        del context.user_data['mode']

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İptal komutu"""
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        # Tüm verileri temizle
        keys_to_remove = ['mode', 'announcement', 'temp_photo']
        for key in keys_to_remove:
            if key in context.user_data:
                del context.user_data[key]
        
        await update.message.reply_text("✅ Tüm işlemler iptal edildi.")

# =================== ANA FONKSİYON ===================
def main():
    """Botu başlat"""
    # Bot token'ını environment variable'dan al
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı!")
        logger.error("Lütfen Railway'de BOT_TOKEN environment variable ekleyin")
        return
    
    logger.info("🤖 Bot başlatılıyor...")
    
    try:
        # Application oluştur
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Komut handler'ları ekle
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin", admin_help))
        application.add_handler(CommandHandler("duyuru", announce_command))
        application.add_handler(CommandHandler("istatistik", stats_command))
        application.add_handler(CommandHandler("kullanicilar", stats_command))
        application.add_handler(CommandHandler("iptal", cancel_command))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Mesaj handler'ları
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_message))
        
        # Botu başlat
        logger.info("✅ Bot başlatıldı. Polling başlıyor...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Bot başlatma hatası: {e}")
        raise

if __name__ == '__main__':
    main()
