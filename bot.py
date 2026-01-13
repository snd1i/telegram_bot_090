import os
import telebot
from telebot import types
import time

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "BURAYA_SIZIN_TELEGRAM_ID_NIZI_YAZIN"  # Örnek: "123456789"

bot = telebot.TeleBot(TOKEN)

# Kullanıcı veritabanı
user_db = {'users': set()}

# Aktif duyuru verisi
active_announcement = None

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_db['users'].add(user_id)
    
    bot.reply_to(
        message,
        "🤖 **Duyuru Botu Aktif!**\n\n"
        "Bu bot ile duyurular alacaksınız.\n"
        f"📊 Aktif kullanıcı: {len(user_db['users'])}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['duyuru'])
def duyuru_menu(message):
    user_id = str(message.from_user.id)
    
    if user_id != ADMIN_ID:
        bot.reply_to(message, "⛔ Yetkiniz yok.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📢 Duyuru Gönder')
    btn2 = types.KeyboardButton('📊 İstatistik')
    btn3 = types.KeyboardButton('❌ İptal')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id,
        "🏢 **Duyuru Paneli**\n\n"
        "Ne yapmak istiyorsunuz?",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text == '📢 Duyuru Gönder' and str(message.from_user.id) == ADMIN_ID)
def start_announcement(message):
    msg = bot.send_message(
        message.chat.id,
        "✏️ **Duyuru metnini yazın:**\n\n"
        "Örnek:\n"
        "*YENİ DUYURU*\n"
        "Bugün bakım yapılacaktır.",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_announcement_text)

def process_announcement_text(message):
    global active_announcement
    
    if message.text == '/cancel':
        bot.send_message(message.chat.id, "❌ İptal edildi.")
        return
    
    # Buton ekleme seçeneği
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✅ Evet", callback_data='add_buttons_yes')
    btn2 = types.InlineKeyboardButton("❌ Hayır", callback_data='add_buttons_no')
    markup.add(btn1, btn2)
    
    active_announcement = {
        'text': message.text,
        'photo_id': None,
        'buttons': []
    }
    
    bot.send_message(
        message.chat.id,
        "🔘 **Buton eklemek istiyor musunuz?**\n\n"
        "Butonlar kullanıcıları bir linke yönlendirebilir.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_buttons'))
def handle_buttons_choice(call):
    if call.data == 'add_buttons_yes':
        bot.edit_message_text(
            "➕ **Buton ekleyin**\n\n"
            "Format: `Buton Metni - URL`\n\n"
            "Örnek:\n"
            "`Web Sitemiz - https://example.com`\n"
            "`İndir - https://play.google.com`\n\n"
            "Bitirmek için /done yazın",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(call.message, process_buttons)
    else:
        ask_for_photo(call.message)

def process_buttons(message):
    global active_announcement
    
    if message.text == '/done':
        ask_for_photo(message)
        return
    
    try:
        if ' - ' in message.text:
            button_text, button_url = message.text.split(' - ', 1)
            active_announcement['buttons'].append({
                'text': button_text.strip(),
                'url': button_url.strip()
            })
            
            bot.send_message(
                message.chat.id,
                f"✅ Buton eklendi: {button_text.strip()}\n"
                f"Devam etmek için başka buton ekleyin veya /done yazın."
            )
            bot.register_next_step_handler(message, process_buttons)
        else:
            bot.send_message(
                message.chat.id,
                "❌ Hatalı format! Doğru format: `Metin - URL`\nÖrnek: `Google - https://google.com`"
            )
            bot.register_next_step_handler(message, process_buttons)
    except:
        bot.send_message(message.chat.id, "❌ Bir hata oluştu, tekrar deneyin.")
        bot.register_next_step_handler(message, process_buttons)

def ask_for_photo(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("✅ Evet", callback_data='add_photo_yes')
    btn2 = types.InlineKeyboardButton("❌ Hayır", callback_data='add_photo_no')
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "🖼️ **Fotoğraf eklemek istiyor musunuz?**",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_photo'))
def handle_photo_choice(call):
    if call.data == 'add_photo_yes':
        bot.edit_message_text(
            "📸 **Fotoğraf gönderin:**\n\n"
            "Lütfen duyuru için bir fotoğraf gönderin.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(call.message, process_photo)
    else:
        show_preview(call.message)

def process_photo(message):
    global active_announcement
    
    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        active_announcement['photo_id'] = photo_id
        show_preview(message)
    else:
        bot.send_message(message.chat.id, "❌ Lütfen fotoğraf gönderin.")
        bot.register_next_step_handler(message, process_photo)

def show_preview(message):
    global active_announcement
    
    if not active_announcement:
        bot.send_message(message.chat.id, "❌ Duyuru bulunamadı.")
        return
    
    # Butonları oluştur
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Kullanıcı butonlarını ekle
    for btn in active_announcement['buttons']:
        markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    # Gönder ve İptal butonları
    markup.row(
        types.InlineKeyboardButton("🚀 GÖNDER", callback_data='send_now'),
        types.InlineKeyboardButton("❌ İPTAL", callback_data='cancel_send')
    )
    
    preview_text = f"""
    📢 **DUYURU ÖNİZLEME**
    
    {active_announcement['text']}
    
    ──────────────
    📊 Gönderilecek: {len(user_db['users'])} kullanıcı
    ⏰ Zaman: {time.strftime('%H:%M')}
    """
    
    if active_announcement['photo_id']:
        bot.send_photo(
            message.chat.id,
            active_announcement['photo_id'],
            caption=preview_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            message.chat.id,
            preview_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

@bot.callback_query_handler(func=lambda call: call.data in ['send_now', 'cancel_send'])
def handle_send_decision(call):
    if call.data == 'cancel_send':
        global active_announcement
        active_announcement = None
        
        bot.edit_message_text(
            "❌ Duyuru iptal edildi.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    # Gönderme işlemi
    bot.edit_message_text(
        f"⏳ **Gönderiliyor...**\n0/{len(user_db['users'])}",
        call.message.chat.id,
        call.message.message_id
    )
    
    success = 0
    failed = 0
    
    # Butonları oluştur
    markup = types.InlineKeyboardMarkup(row_width=1)
    for btn in active_announcement['buttons']:
        markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    # Her kullanıcıya gönder
    for i, user_id in enumerate(list(user_db['users']), 1):
        try:
            if active_announcement['photo_id']:
                bot.send_photo(
                    user_id,
                    active_announcement['photo_id'],
                    caption=active_announcement['text'],
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    user_id,
                    active_announcement['text'],
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            success += 1
        except:
            failed += 1
        
        # Her 5 gönderimde bir güncelle
        if i % 5 == 0 or i == len(user_db['users']):
            bot.edit_message_text(
                f"⏳ **Gönderiliyor...**\n{i}/{len(user_db['users'])}",
                call.message.chat.id,
                call.message.message_id
            )
    
    # Sonuç mesajı
    result_text = f"""
    ✅ **DUYURU GÖNDERİLDİ!**
    
    📊 Sonuçlar:
    • ✓ Başarılı: {success}
    • ✗ Başarısız: {failed}
    • 📈 Toplam: {len(user_db['users'])}
    
    🎯 Başarı Oranı: %{(success/len(user_db['users'])*100):.1f}
    ⏰ Saat: {time.strftime('%H:%M:%S')}
    """
    
    bot.edit_message_text(
        result_text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # Temizle
    active_announcement = None

@bot.message_handler(func=lambda message: message.text == '📊 İstatistik' and str(message.from_user.id) == ADMIN_ID)
def show_stats(message):
    stats_text = f"""
    📈 **İSTATİSTİKLER**
    
    👥 Toplam Kullanıcı: {len(user_db['users'])}
    ⏰ Sistem Saati: {time.strftime('%H:%M:%S')}
    📅 Tarih: {time.strftime('%d.%m.%Y')}
    """
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '❌ İptal' and str(message.from_user.id) == ADMIN_ID)
def cancel_all(message):
    global active_announcement
    active_announcement = None
    
    bot.send_message(
        message.chat.id,
        "✅ Tüm işlemler iptal edildi.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    user_db['users'].add(message.from_user.id)
    
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(
            message,
            "🤖 Bu bot sadece duyuru almak içindir.\n"
            "Duyurular yönetici tarafından gönderilecektir."
        )

if __name__ == "__main__":
    print("=" * 40)
    print("🤖 DUYURU BOTU BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(user_db['users'])}")
    print("=" * 40)
    
    bot.infinity_polling()
