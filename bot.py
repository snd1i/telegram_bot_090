import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# YÖNETİCİ ID - KENDİ ID'Nİ YAZ!
YONETICI_ID = 123456789  # ⚠️ BU NUMARAYI DEĞİŞTİR!

# Kullanıcı verileri
USER_DATA_FILE = "users.txt"

def save_user(user_id):
    """Yeni kullanıcıyı kaydet"""
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = f.read().splitlines()
    except:
        users = []
    
    if str(user_id) not in users:
        with open(USER_DATA_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        return True
    return False

def get_all_users():
    """Tüm kullanıcıları getir"""
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return [int(line.strip()) for line in f if line.strip()]
    except:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    user = update.effective_user
    is_new = save_user(user.id)
    
    if is_new:
        await update.message.reply_text(
            f"🎉 Merhaba {user.first_name}!\n\n"
            f"✅ Duyuru botuna başarıyla kaydoldun.\n"
            f"📢 Önemli duyuruları buradan alacaksın.\n\n"
            f"👥 Toplam kullanıcı: {len(get_all_users())}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            f"👋 Tekrar hoş geldin {user.first_name}!\n"
            f"Zaten kayıtlısın. Duyuruları bekleyin.",
            parse_mode=ParseMode.MARKDOWN
        )

async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yönetici: /duyuru komutu"""
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Bu komutu sadece yöneticiler kullanabilir.")
        return
    
    help_text = """
    📢 **DUYURU GÖNDERMEK İÇİN**

    Şu şekilde mesaj gönder:

    ```
    BAŞLIK: Duyuru Başlığı
    METİN: Duyuru metni buraya yazılacak.
    RESİM: https://example.com/resim.jpg (isteğe bağlı)
    BUTON: Buton Yazısı - https://ornek.com (isteğe bağlı)
    ```

    **Örnek:**
    ```
    BAŞLIK: 🎉 Yeni Özellik!
    METİN: Bildirim sistemi güncellendi.
    RESİM: https://images.unsplash.com/photo-1551650975
    BUTON: İncele - https://sitemiz.com
    ```
    """
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/istatistik komutu"""
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Bu komutu sadece yöneticiler kullanabilir.")
        return
    
    users = get_all_users()
    
    stats_text = f"""
    📊 **BOT İSTATİSTİKLERİ**

    👥 Toplam Kullanıcı: {len(users)}
    🆔 Yönetici ID: `{YONETICI_ID}`
    🤖 Bot: @{context.bot.username}

    *Son 5 kullanıcı ID:*
    """
    
    for user_id in users[-5:]:
        stats_text += f"\n• `{user_id}`"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hızlı duyuru /broadcast"""
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Bu komutu sadece yöneticiler kullanabilir.")
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: `/broadcast Mesajınız`", parse_mode=ParseMode.MARKDOWN)
        return
    
    message = " ".join(context.args)
    users = get_all_users()
    success = 0
    failed = 0
    
    await update.message.reply_text(f"📤 {len(users)} kişiye gönderiliyor...")
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 **Duyuru:**\n\n{message}",
                parse_mode=ParseMode.MARKDOWN
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Kullanıcı {user_id}: {e}")
    
    await update.message.reply_text(
        f"✅ **Duyuru tamamlandı!**\n\n"
        f"✅ Başarılı: {success}\n"
        f"❌ Başarısız: {failed}\n"
        f"📊 Toplam: {len(users)}",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_duyuru_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru mesajını işle"""
    if update.effective_user.id != YONETICI_ID:
        return
    
    text = update.message.text
    
    # Format kontrolü
    if not text.startswith("BAŞLIK:"):
        return
    
    # Mesajı parse et
    lines = text.split('\n')
    data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    
    # Buton oluştur
    keyboard = None
    if 'BUTON' in data and ' - ' in data['BUTON']:
        btn_text, btn_url = data['BUTON'].split(' - ', 1)
        keyboard = [[InlineKeyboardButton(
            btn_text.strip(),
            url=btn_url.strip()
        )]]
    
    # Mesajı hazırla
    message_text = f"📢 **{data.get('BAŞLIK', 'Duyuru')}**\n\n{data.get('METİN', '')}"
    
    # Kullanıcılara gönder
    users = get_all_users()
    success = 0
    failed = 0
    
    await update.message.reply_text(f"📤 {len(users)} kişiye gönderiliyor...")
    
    for user_id in users:
        try:
            if 'RESİM' in data and data['RESİM'].startswith('http'):
                # Resimli gönder
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=data['RESİM'],
                    caption=message_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
                )
            else:
                # Sadece metin
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
                )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Kullanıcı {user_id}: {e}")
    
    # Rapor
    await update.message.reply_text(
        f"✅ **Duyuru tamamlandı!**\n\n"
        f"✅ Başarılı: {success} kişi\n"
        f"❌ Başarısız: {failed} kişi\n"
        f"📊 Toplam: {len(users)} kullanıcı",
        parse_mode=ParseMode.MARKDOWN
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test duyurusu /test"""
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Bu komutu sadece yöneticiler kullanabilir.")
        return
    
    # Kendine test mesajı gönder
    test_message = """
    BAŞLIK: ✅ Test Duyurusu
    METİN: Bot başarıyla çalışıyor! Bu bir test mesajıdır.
    RESİM: https://images.unsplash.com/photo-1611224923853-80b023f02d71
    BUTON: GitHub - https://github.com
    """
    
    # Mesajı simüle et
    update.message.text = test_message
    await handle_duyuru_message(update, context)

def main():
    """Botu başlat"""
    # Token'ı al
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı! Railway Variables'da ayarla.")
        return
    
    logger.info(f"🤖 Bot başlatılıyor...")
    logger.info(f"🆔 Yönetici ID: {YONETICI_ID}")
    
    try:
        # Uygulamayı oluştur - YENİ METOT
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Komutlar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("duyuru", duyuru))
        app.add_handler(CommandHandler("istatistik", istatistik))
        app.add_handler(CommandHandler("broadcast", broadcast))
        app.add_handler(CommandHandler("test", test))
        
        # Duyuru mesaj handler - sadece yönetici
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(YONETICI_ID),
            handle_duyuru_message
        ))
        
        # Botu başlat
        logger.info("🚀 Bot çalışıyor...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Bot başlatılamadı: {e}")

if __name__ == "__main__":
    main()
