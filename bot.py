import os
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ============ AYARLAR ============
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OWNER_ID = "5541236874"  # SİZİN ID'NİZ

# Kullanıcıları kaydetmek için JSON dosyası
USERS_FILE = "users.json"

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ============ KULLANICI KAYDETME ============
def save_user(user_id, username, first_name):
    """Kullanıcıyı JSON dosyasına kaydet"""
    try:
        # Dosya varsa oku, yoksa oluştur
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        else:
            users = {}
        
        # Kullanıcıyı ekle/güncelle
        users[str(user_id)] = {
            "username": username,
            "first_name": first_name,
            "joined_at": logging.Formatter().formatTime(logging.makeLogRecord({}))
        }
        
        # Kaydet
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logging.error(f"Kullanıcı kaydetme hatası: {e}")

def get_all_users():
    """Tüm kullanıcıları getir"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}

# ============ /start KOMUTU ============
async def start(update: Update, context):
    user = update.effective_user
    
    # Kullanıcıyı kaydet
    save_user(user.id, user.username, user.first_name)
    
    # SADECE SİZ GÖREBİLİRSİNİZ (Owner paneli)
    if str(user.id) == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("📢 Duyuru Gönder", callback_data='send_broadcast')],
            [InlineKeyboardButton("👥 Kullanıcılar", callback_data='show_users')],
            [InlineKeyboardButton("ℹ️ Yardım", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'👑 Merhaba Sahip {user.first_name}!\n\n'
            f'📊 Bot İstatistikleri:\n'
            f'• Toplam Kullanıcı: {len(get_all_users())}\n\n'
            f'Ne yapmak istersiniz?',
            reply_markup=reply_markup
        )
    else:
        # NORMAL KULLANICILAR
        keyboard = [
            [InlineKeyboardButton("📢 Kanalım", url="https://t.me/snd_yatirim")],
            [InlineKeyboardButton("🌟 Sahibim", url="https://t.me/snd1i")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'👋 Merhaba {user.first_name}!\n\n'
            f'Ben SND Yatırım Asistanıyım.\n\n'
            f'✅ Özellikler:\n'
            f'• Duyuruları takip et\n'
            f'• Yatırım sinyalleri\n'
            f'• Güncel bilgiler\n\n'
            f'Sahibimden duyuruları buradan alacaksın!',
            reply_markup=reply_markup
        )

# ============ BUTON İŞLEMLERİ ============
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    # Sadece siz tıklayabilirsiniz
    if user_id != OWNER_ID:
        await query.edit_message_text("❌ Bu panel sadece yönetici içindir!")
        return
    
    if query.data == 'send_broadcast':
        await query.edit_message_text(
            "📢 **Tüm Kullanıcılara Duyuru Gönder**\n\n"
            "Şimdi gönderin:\n"
            "• Yazı mesajı\n"
            "• Resim + altyazı\n"
            "• Video + altyazı\n\n"
            "Gönderdiğiniz her şey TÜM kullanıcılara gidecek.\n\n"
            "ℹ️ İptal için /start yazın."
        )
        context.user_data['waiting_broadcast'] = True
        
    elif query.data == 'show_users':
        users = get_all_users()
        if not users:
            await query.edit_message_text("📭 Henüz hiç kullanıcı yok.")
            return
        
        user_list = "\n".join([f"• {data['first_name']} (@{data['username'] or 'yok'})" 
                              for data in list(users.values())[:20]])
        
        await query.edit_message_text(
            f"👥 **Son 20 Kullanıcı**\n\n"
            f"{user_list}\n\n"
            f"📊 Toplam: {len(users)} kullanıcı"
        )
        
    elif query.data == 'help':
        await query.edit_message_text(
            "🤖 **Yönetici Kılavuzu**\n\n"
            "📢 **Duyuru Gönder:**\n"
            "1. '📢 Duyuru Gönder' butonuna tıkla\n"
            "2. Mesajını gönder (yazı/resim/video)\n"
            "3. Bot tüm kullanıcılara gönderecek\n\n"
            "👥 **Kullanıcılar:**\n"
            "• Tüm bot kullanıcılarını gör\n"
            "• Toplam sayıyı kontrol et\n\n"
            "💡 **Not:** Her /start yazan kullanıcı otomatik kaydedilir."
        )

# ============ DUYURU GÖNDERME (TÜM KULLANICILARA) ============
async def handle_broadcast(update: Update, context):
    if str(update.effective_user.id) != OWNER_ID:
        return
    
    if not context.user_data.get('waiting_broadcast'):
        return
    
    message = update.message
    users = get_all_users()
    
    if not users:
        await message.reply_text("❌ Henüz hiç kullanıcı yok!")
        context.user_data['waiting_broadcast'] = False
        return
    
    # İstatistik
    success_count = 0
    fail_count = 0
    
    # İlk mesaj - "Gönderiliyor..."
    status_msg = await message.reply_text(
        f"⏳ Duyuru gönderiliyor...\n"
        f"Toplam {len(users)} kullanıcı\n"
        f"Başarılı: 0\n"
        f"Başarısız: 0"
    )
    
    try:
        # RESİM ile duyuru
        if message.photo:
            photo = message.photo[-1]
            caption = message.caption or "📢 Yeni Duyuru!"
            
            for user_id in users.keys():
                try:
                    await context.bot.send_photo(
                        chat_id=int(user_id),
                        photo=photo.file_id,
                        caption=caption
                    )
                    success_count += 1
                except:
                    fail_count += 1
                
                # Her 5 gönderimde bir güncelle
                if success_count % 5 == 0:
                    await status_msg.edit_text(
                        f"⏳ Duyuru gönderiliyor...\n"
                        f"Toplam {len(users)} kullanıcı\n"
                        f"Başarılı: {success_count}\n"
                        f"Başarısız: {fail_count}"
                    )
        
        # VIDEO ile duyuru
        elif message.video:
            video = message.video
            caption = message.caption or "📢 Yeni Duyuru!"
            
            for user_id in users.keys():
                try:
                    await context.bot.send_video(
                        chat_id=int(user_id),
                        video=video.file_id,
                        caption=caption
                    )
                    success_count += 1
                except:
                    fail_count += 1
                
                if success_count % 5 == 0:
                    await status_msg.edit_text(
                        f"⏳ Duyuru gönderiliyor...\n"
                        f"Toplam {len(users)} kullanıcı\n"
                        f"Başarılı: {success_count}\n"
                        f"Başarısız: {fail_count}"
                    )
        
        # METİN ile duyuru
        elif message.text:
            text = message.text
            
            for user_id in users.keys():
                try:
                    await context.bot.send_message(
                        chat_id=int(user_id),
                        text=text
                    )
                    success_count += 1
                except:
                    fail_count += 1
                
                if success_count % 5 == 0:
                    await status_msg.edit_text(
                        f"⏳ Duyuru gönderiliyor...\n"
                        f"Toplam {len(users)} kullanıcı\n"
                        f"Başarılı: {success_count}\n"
                        f"Başarısız: {fail_count}"
                    )
        
        # Sonuç mesajı
        await status_msg.edit_text(
            f"✅ **Duyuru Tamamlandı!**\n\n"
            f"📊 İstatistikler:\n"
            f"• Toplam Kullanıcı: {len(users)}\n"
            f"• Başarılı: {success_count}\n"
            f"• Başarısız: {fail_count}\n"
            f"• Başarı Oranı: %{int((success_count/len(users))*100)}"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Hata oluştu: {str(e)}")
    
    finally:
        context.user_data['waiting_broadcast'] = False

# ============ /istatistik KOMUTU (SADECE SİZ) ============
async def stats(update: Update, context):
    if str(update.effective_user.id) != OWNER_ID:
        return
    
    users = get_all_users()
    
    await update.message.reply_text(
        f"📊 **Bot İstatistikleri**\n\n"
        f"👥 Toplam Kullanıcı: {len(users)}\n\n"
        f"📈 Son 5 Kullanıcı:\n" +
        "\n".join([f"• {data['first_name']}" 
                  for data in list(users.values())[-5:]])
    )

# ============ ANA PROGRAM ============
def main():
    print("=" * 50)
    print("🤖 BOT BAŞLATILIYOR - TÜM KULLANICILARA DUYURU")
    print(f"👑 Sahip ID: {OWNER_ID}")
    print("=" * 50)
    
    # Token kontrol
    if not BOT_TOKEN:
        print("❌ HATA: TELEGRAM_BOT_TOKEN yok!")
        return
    
    # Bot oluştur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("istatistik", stats))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Mesajlar (duyuru için)
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.TEXT & ~filters.COMMAND,
        handle_broadcast
    ))
    
    # Başlat
    print("✅ Bot hazır! /start yazın...")
    app.run_polling()

if __name__ == '__main__':
    main()
