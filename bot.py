import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Loglama ayarı
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin ID'si (kendi ID'nizi buraya yazın)
ADMIN_ID = 5541236874

# Kullanıcı veritabanı (basit bir dosya sistemi)
USER_DATA_FILE = "users.txt"

# =================== VERİTABANI İŞLEMLERİ ===================
def load_users():
    """Kayıtlı kullanıcıları yükle"""
    if not os.path.exists(USER_DATA_FILE):
        return set()
    with open(USER_DATA_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_user(user_id):
    """Yeni kullanıcı kaydet"""
    users = load_users()
    if str(user_id) not in users:
        users.add(str(user_id))
        with open(USER_DATA_FILE, "w") as f:
            f.write("\n".join(users))

# =================== KOMUTLAR ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botu başlatan komut"""
    user_id = update.effective_user.id
    save_user(user_id)
    
    await update.message.reply_text(
        "👋 Merhaba! Ben duyuru botuyum.\n"
        "Adminler duyuru gönderebilir."
    )

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
    /kullanici_sayisi - Toplam kullanıcı sayısı
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcı istatistikleri"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    users = load_users()
    await update.message.reply_text(f"📊 Toplam kullanıcı: {len(users)}")

# =================== DUYURU SİSTEMİ ===================
async def announce_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru menüsü"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Metin Duyurusu", callback_data='announce_text')],
        [InlineKeyboardButton("🖼️ Resimli Duyuru", callback_data='announce_photo')],
        [InlineKeyboardButton("📊 İstatistik", callback_data='show_stats')],
        [InlineKeyboardButton("❌ İptal", callback_data='cancel')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📢 **DUYURU SİSTEMİ**\n\n"
        "Göndermek istediğiniz duyuru tipini seçin:",
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
    
    if data == 'announce_text':
        context.user_data['announce_type'] = 'text'
        await query.edit_message_text(
            "📝 **Metin Duyurusu**\n\n"
            "Lütfen göndermek istediğiniz mesajı yazın:\n"
            "(İptal etmek için /iptal yazın)",
            parse_mode='Markdown'
        )
    
    elif data == 'announce_photo':
        context.user_data['announce_type'] = 'photo'
        await query.edit_message_text(
            "🖼️ **Resimli Duyuru**\n\n"
            "Lütfen göndermek istediğiniz resmi gönderin:\n"
            "(İptal etmek için /iptal yazın)",
            parse_mode='Markdown'
        )
    
    elif data == 'show_stats':
        users = load_users()
        await query.edit_message_text(f"📊 **İstatistikler**\n\nToplam kullanıcı: {len(users)}")
    
    elif data == 'cancel':
        await query.edit_message_text("✅ İşlem iptal edildi.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gelen mesajları işle"""
    user_id = update.effective_user.id
    
    # Admin duyuru modunda mı kontrol et
    if user_id == ADMIN_ID and 'announce_type' in context.user_data:
        announce_type = context.user_data['announce_type']
        
        if announce_type == 'text':
            text = update.message.text
            if text == '/iptal':
                del context.user_data['announce_type']
                await update.message.reply_text("✅ Duyuru iptal edildi.")
                return
            
            # Onay butonları
            keyboard = [
                [InlineKeyboardButton("✅ Gönder", callback_data=f'send_text:{text[:50]}')],
                [InlineKeyboardButton("❌ İptal", callback_data='cancel_send')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📝 **Duyuru Önizleme**\n\n{text}\n\n"
                f"Bu duyuru {len(load_users())} kullanıcıya gönderilecek.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif announce_type == 'photo':
            if update.message.photo:
                # Fotoğrafı kaydet
                photo = update.message.photo[-1]
                context.user_data['announce_photo'] = photo.file_id
                await update.message.reply_text(
                    "✅ Fotoğraf alındı. Şimdi açıklama metnini yazın:\n"
                    "(İptal etmek için /iptal yazın)"
                )
                context.user_data['announce_step'] = 'waiting_caption'
            else:
                await update.message.reply_text("Lütfen bir fotoğraf gönderin!")
    
    # Fotoğraf açıklaması bekleniyor
    elif (user_id == ADMIN_ID and 
          'announce_step' in context.user_data and 
          context.user_data['announce_step'] == 'waiting_caption'):
        
        caption = update.message.text
        if caption == '/iptal':
            del context.user_data['announce_step']
            if 'announce_photo' in context.user_data:
                del context.user_data['announce_photo']
            await update.message.reply_text("✅ Duyuru iptal edildi.")
            return
        
        # Onay butonları
        keyboard = [
            [InlineKeyboardButton("✅ Gönder", callback_data=f'send_photo:{caption[:50]}')],
            [InlineKeyboardButton("❌ İptal", callback_data='cancel_send')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🖼️ **Fotoğraflı Duyuru Önizleme**\n\n"
            f"Açıklama: {caption}\n\n"
            f"Bu duyuru {len(load_users())} kullanıcıya gönderilecek.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        context.user_data['announce_caption'] = caption

async def send_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru gönderme onayı"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ Yetkiniz yok!")
        return
    
    data = query.data
    
    if data == 'cancel_send':
        # Temizle
        keys_to_delete = ['announce_type', 'announce_step', 'announce_photo', 'announce_caption']
        for key in keys_to_delete:
            if key in context.user_data:
                del context.user_data[key]
        
        await query.edit_message_text("✅ Duyuru iptal edildi.")
    
    elif data.startswith('send_text:'):
        text = data.split(':', 1)[1]
        original_text = query.message.text.split('\n\n')[1]  # Önizlemeden orijinal metni al
        
        await query.edit_message_text("🔄 Duyuru gönderiliyor...")
        
        # Tüm kullanıcılara gönder
        success, fail = await send_to_all_users(context, text=original_text)
        
        await query.edit_message_text(
            f"✅ Duyuru gönderildi!\n\n"
            f"✅ Başarılı: {success}\n"
            f"❌ Başarısız: {fail}"
        )
        
        if 'announce_type' in context.user_data:
            del context.user_data['announce_type']
    
    elif data.startswith('send_photo:'):
        caption = data.split(':', 1)[1]
        original_caption = query.message.text.split('Açıklama: ')[1].split('\n\n')[0]
        photo_id = context.user_data.get('announce_photo')
        
        await query.edit_message_text("🔄 Duyuru gönderiliyor...")
        
        # Tüm kullanıcılara gönder
        success, fail = await send_to_all_users(context, photo=photo_id, caption=original_caption)
        
        await query.edit_message_text(
            f"✅ Duyuru gönderildi!\n\n"
            f"✅ Başarılı: {success}\n"
            f"❌ Başarısız: {fail}"
        )
        
        # Temizle
        keys_to_delete = ['announce_type', 'announce_step', 'announce_photo', 'announce_caption']
        for key in keys_to_delete:
            if key in context.user_data:
                del context.user_data[key]

async def send_to_all_users(context: ContextTypes.DEFAULT_TYPE, text=None, photo=None, caption=None):
    """Tüm kullanıcılara mesaj gönder"""
    users = load_users()
    success = 0
    fail = 0
    
    for user_id_str in users:
        try:
            if photo:
                await context.bot.send_photo(
                    chat_id=int(user_id_str),
                    photo=photo,
                    caption=caption,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=int(user_id_str),
                    text=text,
                    parse_mode='Markdown'
                )
            success += 1
        except Exception as e:
            logger.error(f"Kullanıcı {user_id_str} gönderilemedi: {e}")
            fail += 1
    
    return success, fail

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İptal komutu"""
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        # Temizle
        keys_to_delete = ['announce_type', 'announce_step', 'announce_photo', 'announce_caption']
        for key in keys_to_delete:
            if key in context.user_data:
                del context.user_data[key]
        
        await update.message.reply_text("✅ Tüm işlemler iptal edildi.")

# =================== ANA FONKSİYON ===================
def main():
    """Botu başlat"""
    # Bot token'ını environment variable'dan al
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN bulunamadı!")
        return
    
    # Application oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_help))
    application.add_handler(CommandHandler("duyuru", announce_menu))
    application.add_handler(CommandHandler("istatistik", user_stats))
    application.add_handler(CommandHandler("kullanici_sayisi", user_stats))
    application.add_handler(CommandHandler("iptal", cancel))
    
    # Buton handler
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^(announce_text|announce_photo|show_stats|cancel)$'))
    application.add_handler(CallbackQueryHandler(send_confirmation_handler, pattern='^(send_text|send_photo|cancel_send)'))
    
    # Mesaj handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    
    # Botu başlat
    print("🤖 Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
