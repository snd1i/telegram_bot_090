import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ============ AYARLAR ============
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OWNER_ID = "5541236874"  # BURAYA SİZİN ID'NİZİ YAZDIM

# Kanal bilgisi - Bot panelinden ayarlanacak
user_channel = None

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ============ /start KOMUTU ============
async def start(update: Update, context):
    user = update.effective_user
    
    # SADECE SİZ GÖREBİLİRSİNİZ
    if str(user.id) == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("📢 Kanalı Ayarla", callback_data='set_channel')],
            [InlineKeyboardButton("📤 Duyuru Gönder", callback_data='send_announce')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'👑 Merhaba Sahip {user.first_name}!\n\n'
            f'Bot Kontrol Paneli\n'
            f'ID: {user.id}\n\n'
            f'Ne yapmak istersiniz?',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f'Merhaba {user.first_name}!\n'
            f'Bu bot sadece yönetici içindir.'
        )

# ============ BUTON İŞLEMLERİ ============
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    # Sadece siz tıklayabilirsiniz
    if str(query.from_user.id) != OWNER_ID:
        await query.edit_message_text("❌ Yetkiniz yok!")
        return
    
    if query.data == 'set_channel':
        await query.edit_message_text(
            "📢 **Kanal Ayarlama**\n\n"
            "Lütfen kanal @username gönderin:\n"
            "Örnek: @snd_yatirim\n\n"
            "Veya kanal ID:\n"
            "Örnek: -1002129401570\n\n"
            "Gönderdikten sonra bot kanalı kontrol edecek."
        )
        # Kanal bekliyoruz
        context.user_data['waiting_for_channel'] = True
        
    elif query.data == 'send_announce':
        global user_channel
        
        if not user_channel:
            await query.edit_message_text(
                "❌ Önce kanal ayarlayın!\n"
                "📢 Kanalı Ayarla butonuna tıklayın."
            )
            return
        
        await query.edit_message_text(
            "📤 **Duyuru Gönder**\n\n"
            "Şimdi gönderin:\n"
            "• Yazı mesajı\n"
            "• Resim + yazı\n"
            "• Video + yazı\n\n"
            "Gönderdiğiniz her şey kanala gidecek."
        )
        context.user_data['waiting_for_announce'] = True

# ============ KANAL KAYDETME ============
async def handle_channel(update: Update, context):
    if str(update.effective_user.id) != OWNER_ID:
        return
    
    if context.user_data.get('waiting_for_channel'):
        channel = update.message.text.strip()
        global user_channel
        
        try:
            # Test mesajı gönder
            test = await update.message.reply_text(f"🔍 Kanal kontrol ediliyor: {channel}")
            
            # Basit kontrol - @ işareti veya -100
            if channel.startswith('@') or channel.startswith('-100'):
                user_channel = channel
                
                await update.message.reply_text(
                    f"✅ Kanal ayarlandı!\n\n"
                    f"Kanal: {channel}\n\n"
                    f"Artık duyuru gönderebilirsiniz.\n"
                    f"/start yazıp '📤 Duyuru Gönder' butonuna tıklayın."
                )
            else:
                await update.message.reply_text(
                    "❌ Geçersiz format!\n"
                    "@username veya -1001234567890 şeklinde olmalı."
                )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")
        
        finally:
            context.user_data['waiting_for_channel'] = False

# ============ DUYURU GÖNDERME ============
async def handle_announcement(update: Update, context):
    if str(update.effective_user.id) != OWNER_ID:
        return
    
    if context.user_data.get('waiting_for_announce'):
        global user_channel
        
        if not user_channel:
            await update.message.reply_text("❌ Kanal ayarlanmamış! /start")
            return
        
        try:
            # Buton oluştur
            keyboard = [[
                InlineKeyboardButton("📢 Katıl", url="https://t.me/snd_yatirim"),
                InlineKeyboardButton("✅ Oldum", callback_data='joined')
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = update.message
            
            # RESİM
            if message.photo:
                photo = message.photo[-1]
                caption = message.caption or "📢 Yeni Duyuru!"
                
                await update.message.reply_text(
                    f"✅ Resimli duyuru hazır!\n"
                    f"Kanal: {user_channel}\n"
                    f"Mesaj: {caption}\n\n"
                    f"⚠️ NOT: Kanal gönderimi test modunda."
                )
            
            # VIDEO
            elif message.video:
                caption = message.caption or "📢 Yeni Duyuru!"
                
                await update.message.reply_text(
                    f"✅ Videolu duyuru hazır!\n"
                    f"Kanal: {user_channel}\n"
                    f"Mesaj: {caption}\n\n"
                    f"⚠️ NOT: Kanal gönderimi test modunda."
                )
            
            # METİN
            elif message.text:
                await update.message.reply_text(
                    f"✅ Duyuru hazır!\n"
                    f"Kanal: {user_channel}\n"
                    f"Mesaj: {message.text}\n\n"
                    f"⚠️ NOT: Kanal gönderimi test modunda."
                )
            
            context.user_data['waiting_for_announce'] = False
            
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {str(e)}")

# ============ ANA PROGRAM ============
def main():
    print("=" * 50)
    print("🤖 TELEGRAM BOT BAŞLATILIYOR")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("=" * 50)
    
    # Token kontrol
    if not BOT_TOKEN:
        print("❌ HATA: TELEGRAM_BOT_TOKEN yok!")
        print("Railway → Variables → TELEGRAM_BOT_TOKEN ekleyin")
        return
    
    # Bot oluştur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Mesajlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_channel))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.TEXT, handle_announcement))
    
    # Başlat
    print("✅ Bot başlatıldı. /start yazın...")
    app.run_polling()

if __name__ == '__main__':
    main()
