import os
import telebot
from telebot import types
import time

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "5541236874"  # Örnek: "123456789"

bot = telebot.TeleBot(TOKEN)

# Kullanıcı veritabanı (basit versiyon)
user_db = {
    'users': set(),
    'stats': {'total_messages': 0, 'last_announcement': None}
}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_db['users'].add(user_id)
    user_db['stats']['total_messages'] += 1
    
    welcome_text = """
    🎉 **Hoş Geldiniz!**
    
    Bu bot, duyuruları almak için kullanılır.
    
    📊 **Bot İstatistikleri:**
    • Toplam Kullanıcı: {}
    • Son Duyuru: {}
    
    ⚠️ **Not:** Sadece yönetici duyuru gönderebilir.
    """.format(
        len(user_db['users']),
        user_db['stats']['last_announcement'] or "Henüz yok"
    )
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['duyuru'])
def duyuru_menu(message):
    user_id = str(message.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.reply_to(message, "⛔ Yetkiniz yok. Sadece yönetici duyuru gönderebilir.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📢 Duyuru Gönder')
    btn2 = types.KeyboardButton('📊 İstatistikler')
    btn3 = types.KeyboardButton('❌ İptal')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id,
        "🏢 **Duyuru Paneli**\n\n"
        "Aşağıdaki seçeneklerden birini seçin:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == '📢 Duyuru Gönder' and str(message.from_user.id) == ADMIN_ID)
def start_announcement(message):
    msg = bot.send_message(
        message.chat.id,
        "✏️ **Duyuru metnini yazın:**\n\n"
        "• Başlık ve içerik\n"
        "• Emojiler kullanabilirsiniz\n"
        "• Markdown formatı desteklenir\n\n"
        "Örnek:\n"
        "*Yeni Güncelleme!*\n"
        "Bugün sistem bakımı yapılacaktır.",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, get_announcement_text)

def get_announcement_text(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, "❌ İşlem iptal edildi.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    user_data = {'text': message.text}
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✅ Evet", callback_data='announce_with_photo_yes')
    btn2 = types.InlineKeyboardButton("❌ Hayır", callback_data='announce_with_photo_no')
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "🖼️ **Fotoğraf eklemek istiyor musunuz?**\n\n"
        "Duyuruya bir görsel eklemek isterseniz 'Evet' seçeneğini seçin.",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, lambda m: setattr(m, 'user_data', user_data))

@bot.callback_query_handler(func=lambda call: call.data.startswith('announce_with_photo'))
def handle_photo_choice(call):
    if call.data == 'announce_with_photo_yes':
        bot.edit_message_text(
            "📸 **Fotoğraf gönderin:**\n\n"
            "Lütfen duyuru için bir fotoğraf gönderin.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(call.message, get_announcement_photo)
    else:
        send_preview(call.message, None)

def get_announcement_photo(message):
    if message.content_type == 'photo':
        # En yüksek çözünürlüklü fotoğrafı al
        photo_id = message.photo[-1].file_id
        send_preview(message, photo_id)
    else:
        bot.send_message(message.chat.id, "❌ Lütfen sadece fotoğraf gönderin.")
        bot.register_next_step_handler(message, get_announcement_photo)

def send_preview(message, photo_id=None):
    user_id = message.from_user.id
    
    # Butonlar oluştur
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📤 Gönder", callback_data='send_announcement')
    btn2 = types.InlineKeyboardButton("✏️ Düzenle", callback_data='edit_announcement')
    btn3 = types.InlineKeyboardButton("❌ İptal", callback_data='cancel_announcement')
    
    # Link butonu örneği
    btn4 = types.InlineKeyboardButton("🌐 Web Sitemiz", url="https://example.com")
    markup.add(btn1, btn2, btn3)
    markup.add(btn4)
    
    preview_text = f"""
    📢 **DUYURU ÖNİZLEME**
    
    {message.text}
    
    ───────────────
    📊 Gönderilecek: {len(user_db['users'])} kullanıcı
    ⏰ Zaman: {time.strftime('%d.%m.%Y %H:%M')}
    """
    
    if photo_id:
        bot.send_photo(
            user_id,
            photo_id,
            caption=preview_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            user_id,
            preview_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Veriyi sakla
    user_db['temp_announcement'] = {
        'text': message.text,
        'photo_id': photo_id,
        'buttons': [{'text': '🌐 Web Sitemiz', 'url': 'https://example.com'}]
    }

@bot.callback_query_handler(func=lambda call: call.data == 'send_announcement')
def send_announcement_to_all(call):
    announcement = user_db.get('temp_announcement')
    if not announcement:
        bot.answer_callback_query(call.id, "❌ Duyuru bulunamadı!")
        return
    
    bot.edit_message_text(
        "⏳ **Duyuru gönderiliyor...**\n\n"
        f"Hedef: {len(user_db['users'])} kullanıcı",
        call.message.chat.id,
        call.message.message_id
    )
    
    success = 0
    failed = 0
    total = len(user_db['users'])
    
    # İlerleme mesajı
    progress_msg = bot.send_message(
        call.message.chat.id,
        f"📤 Gönderim başladı...\n0/{total}"
    )
    
    # Butonları oluştur
    markup = types.InlineKeyboardMarkup()
    for btn in announcement['buttons']:
        markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    # Her kullanıcıya gönder
    for i, user_id in enumerate(user_db['users']):
        try:
            if announcement['photo_id']:
                bot.send_photo(
                    user_id,
                    announcement['photo_id'],
                    caption=announcement['text'],
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    user_id,
                    announcement['text'],
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            success += 1
        except Exception as e:
            failed += 1
        
        # Her 10 gönderimde bir güncelle
        if i % 10 == 0:
            bot.edit_message_text(
                f"📤 Gönderiliyor...\n{success+failed}/{total}",
                call.message.chat.id,
                progress_msg.message_id
            )
    
    # İstatistikleri güncelle
    user_db['stats']['last_announcement'] = time.strftime('%d.%m.%Y %H:%M')
    
    # Sonuç raporu
    report = f"""
    ✅ **DUYURU TAMAMLANDI!**
    
    📊 İstatistikler:
    • ✓ Başarılı: {success}
    • ✗ Başarısız: {failed}
    • 📈 Toplam: {total}
    • ⏰ Zaman: {time.strftime('%d.%m.%Y %H:%M')}
    
    🎯 Başarı Oranı: %{((success/total)*100):.1f}
    """
    
    bot.delete_message(call.message.chat.id, progress_msg.message_id)
    bot.send_message(call.message.chat.id, report, parse_mode='Markdown')
    
    # Geçici veriyi temizle
    if 'temp_announcement' in user_db:
        del user_db['temp_announcement']

@bot.message_handler(func=lambda message: message.text == '📊 İstatistikler' and str(message.from_user.id) == ADMIN_ID)
def show_stats(message):
    stats_text = f"""
    📈 **BOT İSTATİSTİKLERİ**
    
    👥 Kullanıcı Sayısı: {len(user_db['users'])}
    💬 Toplam Mesaj: {user_db['stats']['total_messages']}
    📢 Son Duyuru: {user_db['stats']['last_announcement'] or 'Henüz yok'}
    
    ⏰ Sistem Saati: {time.strftime('%d.%m.%Y %H:%M:%S')}
    """
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '❌ İptal' and str(message.from_user.id) == ADMIN_ID)
def cancel_operation(message):
    bot.send_message(
        message.chat.id,
        "✅ İşlem iptal edildi. Ana menüye dönüldü.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# Diğer mesajları kaydet
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_db['users'].add(message.from_user.id)
    user_db['stats']['total_messages'] += 1
    
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(
            message,
            "🤖 Bu bot sadece duyuru almak içindir. "
            "Yönetici size duyuruları gönderecektir."
        )

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 PROFESYONEL DUYURU BOTU")
    print(f"👥 Kayıtlı Kullanıcı: {len(user_db['users'])}")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print("=" * 50)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("♻️ Bot yeniden başlatılıyor...")
        time.sleep(5)
