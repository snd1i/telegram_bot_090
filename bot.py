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
YONETICI_ID = 123456789  # BU NUMARAYI DEĞİŞTİR!

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
    """/start komutu"""
    user = update.effective_user
    save_user(user.id)
    
    await update.message.reply_text(
        f"🎉 Merhaba {user.first_name}!\n\n"
        f"Duyuru botuna hoş geldin. Önemli duyurular buradan iletilecek.\n\n"
        f"✅ Başarıyla kayıt oldun!",
        parse_mode=ParseMode.MARKDOWN
    )

async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yönetici: /duyuru komutu"""
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Yetkiniz yok!")
        return
    
    await update.message.reply_text(
        "📢 **DUYURU GÖNDER**\n\n"
        "Şu formatta mesaj gönder:\n\n"
        "*Başlık*\nMetin\n*Resim:* https://...\n*Buton:* Yazı - https://...\n\n"
        "Örnek:\n"
        "Yeni Güncelleme!\n"
        "Merhaba, yeni özellikler eklendi.\n"
        "*Resim:* https://i.imgur.com/abc123.jpg\n"
        "*Buton:* Detaylar - https://site.com",
        parse_mode=ParseMode.MARKDOWN
    )

async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/istatistik komutu"""
    if update.effective_user.id != YONETICI_ID:
        await update.message.reply_text("⛔ Yetkiniz yok!")
        return
    
    users = get_all_users()
    await update.message.reply_text(
        f"📊 **İstatistikler**\n\n"
        f"👥 Toplam Kullanıcı: {len(users)}\n"
        f"🆔 Yönetici ID: {YONETICI_ID}\n"
        f"🤖 Bot: @{context.bot.username if context.bot.username else 'bilinmiyor'}",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru mesajını işle"""
    if update.effective_user.id != YONETICI_ID:
        return
    
    text = update.message.text
    
    # Başlık ve metni ayır
    lines = text.split('\n')
    if len(lines) < 2:
        await update.message.reply_text("❌ Geçersiz format! En az 2 satır olmalı.")
        return
    
    baslik = lines[0].strip()
    metin = lines[1].strip()
    
    # Resim ve butonları bul
    resim_url = None
    buton_text = None
    buton_url = None
    
    for line in lines[2:]:
        line = line.strip()
        if line.lower().startswith("*resim:*"):
            resim_url = line.replace("*Resim:*", "").replace("*resim:*", "").strip()
        elif line.lower().startswith("*buton:*"):
            buton_part = line.replace("*Buton:*", "").replace("*buton:*", "").strip()
            if " - " in buton_part:
                buton_text, buton_url = buton_part.split(" - ", 1)
    
    # Buton oluştur
    keyboard = None
    if buton_text and buton_url:
        keyboard = [[InlineKeyboardButton(buton_text.strip(), url=buton_url.strip())]]
    
    # Mesajı hazırla
    mesaj = f"📢 **{baslik}**\n\n{metin}"
    
    # Kullanıcılara gönder
    users = get_all_users()
    basarili = 0
    
    for user_id in users:
        try:
            if resim_url and resim_url.startswith("http"):
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=resim_url,
                    caption=mesaj,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=mesaj,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
                )
            basarili += 1
        except:
            continue
    
    await update.message.reply_text(
        f"✅ Duyuru gönderildi!\n"
        f"✅ {basarili}/{len(users)} kişiye iletildi",
        parse_mode=ParseMode.MARKDOWN
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hızlı duyuru /broadcast"""
    if update.effective_user.id != YONETICI_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: /broadcast mesajınız")
        return
    
    mesaj = " ".join(context.args)
    
    users = get_all_users()
    basarili = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 {mesaj}",
                parse_mode=ParseMode.MARKDOWN
            )
            basarili += 1
        except:
            continue
    
    await update.message.reply_text(f"✅ {basarili} kişiye gönderildi")

def main():
    """Botu başlat"""
    # Token'ı al
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN bulunamadı! Railway'da ayarladın mı?")
        return
    
    logger.info(f"🤖 Bot başlatılıyor... Yönetici ID: {YONETICI_ID}")
    
    # Uygulamayı oluştur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru))
    app.add_handler(CommandHandler("istatistik", istatistik))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # Duyuru mesaj handler
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(YONETICI_ID),
        handle_duyuru
    ))
    
    # Botu başlat
    logger.info("🚀 Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
