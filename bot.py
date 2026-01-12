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

# Kullanıcı verileri
USER_DATA_FILE = "users.txt"

def save_user(user_id):
    """Yeni kullanıcıyı kaydet"""
    try:
        with open(USER_DATA_FILE, "r") as f:
            users = f.read().splitlines()
    except:
        users = []
    
    if str(user_id) not in users:
        with open(USER_DATA_FILE, "a") as f:
            f.write(f"{user_id}\n")
        return True
    return False

def get_all_users():
    """Tüm kullanıcıları getir"""
    try:
        with open(USER_DATA_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip()]
    except:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcı başlattığında"""
    user = update.effective_user
    is_new = save_user(user.id)
    
    welcome_msg = f"""
    🎉 **Hoş Geldin {user.first_name}!**
    
    🤖 **Duyuru Botu** - Yöneticilerden önemli duyurular alacaksın.
    
    📊 *{len(get_all_users())} kişi bu botu kullanıyor*
    
    {"✨ *Yeni kullanıcı kaydedildi!*" if is_new else ""}
    
    ✅ Başarıyla kaydedildin. Duyuruları bekleyin!
    """
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode=ParseMode.MARKDOWN
    )

async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yönetici: Duyuru gönderme komutu"""
    # YÖNETİCİ ID - DEĞİŞTİRMEN GEREKECEK!
    YONETICI_ID = 123456789  # BU NUMARAYI KENDİ ID'NLE DEĞİŞTİR
    
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Bu komutu sadece yöneticiler kullanabilir.")
        return
    
    help_text = """
    📢 **DUYURU FORMATI**
    
    Aşağıdaki gibi mesaj gönder:
    
    ```
    BAŞLIK: Önemli Duyuru!
    METİN: Değerli kullanıcılarımız, yeni güncelleme...
    RESİM: https://örnek.com/resim.jpg
    BUTON: Detaylar - https://site.com
    ```
    
    *Notlar:*
    • RESİM ve BUTON isteğe bağlı
    • Her satır başı büyük harfle başlamalı
    • Resim URL'si doğrudan erişilebilir olmalı
    """
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def handle_duyuru_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru mesajını işle"""
    YONETICI_ID = 123456789  # BU NUMARAYI KENDİ ID'NLE DEĞİŞTİR
    
    if update.effective_user.id != YONETICI_ID:
        return
    
    text = update.message.text
    
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
    if 'BUTON' in data and '-' in data['BUTON']:
        btn_text, btn_url = data['BUTON'].split('-', 1)
        keyboard = [[InlineKeyboardButton(
            btn_text.strip(),
            url=btn_url.strip()
        )]]
    
    # Tüm kullanıcılara gönder
    users = get_all_users()
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            message_text = f"📢 **{data.get('BAŞLIK', 'Duyuru')}**\n\n{data.get('METİN', '')}"
            
            if 'RESİM' in data and data['RESİM'].startswith('http'):
                # Resimli mesaj
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
            logging.error(f"Kullanıcı {user_id}: {e}")
    
    # Rapor gönder
    await update.message.reply_text(
        f"✅ **Duyuru Tamamlandı!**\n\n"
        f"✅ Başarılı: {success} kişi\n"
        f"❌ Başarısız: {failed} kişi\n"
        f"📊 Toplam: {len(users)} kullanıcı"
    )

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İstatistikleri göster"""
    YONETICI_ID = 123456789  # BU NUMARAYI KENDİ ID'NLE DEĞİŞTİR
    
    if update.effective_user.id != YONETICI_ID:
        return
    
    users = get_all_users()
    
    stats = f"""
    📊 **BOT İSTATİSTİKLERİ**
    
    👥 Toplam Kullanıcı: {len(users)}
    🆔 Yönetici ID: {YONETICI_ID}
    🤖 Bot: @{context.bot.username}
    
    *Son 5 Kullanıcı ID:*
    """
    
    for user_id in users[-5:]:
        stats += f"\n• `{user_id}`"
    
    await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)

async def test_duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test duyurusu gönder"""
    YONETICI_ID = 123456789  # BU NUMARAYI KENDİ ID'NLE DEĞİŞTİR
    
    if update.effective_user.id != YONETICI_ID:
        return
    
    # Kendine test mesajı gönder
    test_message = """
    BAŞLIK: ✅ Test Duyurusu
    METİN: Bu bir test duyurusudur. Bot çalışıyor!
    RESİM: https://images.unsplash.com/photo-1611224923853-80b023f02d71
    BUTON: GitHub - https://github.com
    """
    
    await handle_duyuru_message(update, context)

def main():
    """Botu başlat"""
    # BOT TOKEN - Railway'da ayarlayacaksın
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN bulunamadı!")
        return
    
    # Uygulamayı oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("duyuru", duyuru))
    application.add_handler(CommandHandler("istatistik", istatistik))
    application.add_handler(CommandHandler("test", test_duyuru))
    
    # Duyuru mesaj handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_duyuru_message
    ))
    
    # Botu başlat
    logging.info("Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
