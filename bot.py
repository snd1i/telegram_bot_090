import os
import telebot
from telebot import types
import time

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "BURAYA_SIZIN_TELEGRAM_ID_NIZI_YAZIN"

bot = telebot.TeleBot(TOKEN)

# Veriler
users = set()
current_announcement = None
user_states = {}  # Kullanıcı durumlarını takip et

@bot.message_handler(commands=['start'])
def start(message):
    users.add(message.from_user.id)
    
    bot.reply_to(
        message,
        f"🤖 Bot aktif! Kullanıcı: {len(users)}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['duyuru'])
def duyuru_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "⛔ Yetkiniz yok.")
        return
    
    # Duyuru metni iste
    msg = bot.send_message(
        message.chat.id,
        "📝 **Duyuru metnini yazın:**\n\nYazdıktan sonra enter'a basın.",
        parse_mode='Markdown'
    )
    user_states[message.from_user.id] = 'waiting_for_text'
    bot.register_next_step_handler(msg, process_text)

def process_text(message):
    global current_announcement
    
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ İşlem iptal edildi.")
        user_states.pop(message.from_user.id, None)
        return
    
    # Metni kaydet
    current_announcement = {
        'text': message.text,
        'photo': None,
        'buttons': []
    }
    
    user_states[message.from_user.id] = 'asking_for_buttons'
    
    # Buton ekleme seçeneği - SADECE İKİ BUTON
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ EVET", callback_data='add_button'),
        types.InlineKeyboardButton("❌ HAYIR", callback_data='no_button')
    )
    
    bot.send_message(
        message.chat.id,
        "🔘 **Buton eklemek istiyor musunuz?**\n\nEvet'i seçerseniz, buton metni ve URL'sini isteyeceğim.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global current_announcement
    
    if call.data == 'add_button':
        user_states[call.from_user.id] = 'waiting_for_button'
        
        bot.edit_message_text(
            "🔗 **Buton bilgilerini girin:**\n\n"
            "**FORMAT:** `Metin - URL`\n\n"
            "**ÖRNEK:**\n"
            "`İndir - https://play.google.com`\n"
            "`Web Site - https://example.com`\n\n"
            "Lütfen butonunuzu bu formatta yazın:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    
    elif call.data == 'no_button':
        user_states[call.from_user.id] = 'asking_for_photo'
        
        # Fotoğraf sorusu - SADECE İKİ BUTON
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ EVET", callback_data='add_photo'),
            types.InlineKeyboardButton("❌ HAYIR", callback_data='no_photo')
        )
        
        bot.edit_message_text(
            "🖼️ **Fotoğraf eklemek istiyor musunuz?**",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif call.data == 'add_photo':
        user_states[call.from_user.id] = 'waiting_for_photo'
        
        bot.edit_message_text(
            "📸 **Fotoğraf gönderin:**\n\n"
            "Lütfen duyuru için bir fotoğraf gönderin.\n"
            "Fotoğraf göndermek istemiyorsanız 'Hayır'ı seçmelisiniz.",
            call.message.chat.id,
            call.message.message_id
        )
    
    elif call.data == 'no_photo':
        user_states.pop(call.from_user.id, None)
        show_preview(call.message)
    
    elif call.data == 'send_announcement':
        send_to_all(call)
    
    elif call.data == 'cancel_announcement':
        bot.edit_message_text(
            "❌ Duyuru iptal edildi.",
            call.message.chat.id,
            call.message.message_id
        )
        current_announcement = None
        user_states.pop(call.from_user.id, None)

# Buton bilgisi al
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_for_button')
def receive_button_info(message):
    global current_announcement
    
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ İşlem iptal edildi.")
        user_states.pop(message.from_user.id, None)
        return
    
    # Format kontrolü
    if ' - ' not in message.text:
        bot.send_message(
            message.chat.id,
            "❌ **HATALI FORMAT!**\n\n"
            "Doğru format: `Metin - URL`\n\n"
            "**Örnekler:**\n"
            "• `Google - https://google.com`\n"
            "• `İndir - https://play.google.com`\n"
            "• `Web Site - https://example.com`\n\n"
            "Lütfen tekrar deneyin:",
            parse_mode='Markdown'
        )
        return  # Tekrar bekleyecek
    
    # Butonu kaydet
    button_text, button_url = message.text.split(' - ', 1)
    current_announcement['buttons'].append({
        'text': button_text.strip(),
        'url': button_url.strip()
    })
    
    user_states[message.from_user.id] = 'asking_for_more_buttons'
    
    # Başka buton eklemek ister mi? - SADECE İKİ BUTON
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ EVET", callback_data='add_button'),
        types.InlineKeyboardButton("❌ HAYIR", callback_data='no_button')
    )
    
    bot.send_message(
        message.chat.id,
        f"✅ **Buton eklendi:** {button_text.strip()}\n\n"
        "Başka buton eklemek istiyor musunuz?",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Fotoğraf al
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_for_photo')
def receive_photo(message):
    global current_announcement
    
    if message.content_type == 'photo':
        current_announcement['photo'] = message.photo[-1].file_id
        user_states.pop(message.from_user.id, None)
        show_preview(message)
    else:
        bot.send_message(
            message.chat.id,
            "❌ Lütfen sadece **fotoğraf** gönderin!\n\n"
            "Fotoğraf göndermek istemiyorsanız 'Hayır'ı seçmelisiniz."
        )

def show_preview(message):
    global current_announcement
    
    if not current_announcement:
        bot.send_message(message.chat.id, "❌ Duyuru bulunamadı.")
        return
    
    # Mesaj butonları
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Kullanıcının eklediği butonlar
    if current_announcement['buttons']:
        for btn in current_announcement['buttons']:
            markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    # İşlem butonları - NET VE BÜYÜK
    markup.row(
        types.InlineKeyboardButton("🚀 GÖNDER", callback_data='send_announcement'),
        types.InlineKeyboardButton("❌ İPTAL", callback_data='cancel_announcement')
    )
    
    preview_text = f"""
📢 **DUYURU ÖNİZLEME**

{current_announcement['text']}

────────────
👥 **Hedef:** {len(users)} kullanıcı
🕐 **Zaman:** {time.strftime('%H:%M')}
"""
    
    if current_announcement['photo']:
        bot.send_photo(
            message.chat.id,
            current_announcement['photo'],
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

def send_to_all(call):
    global current_announcement
    
    if not current_announcement:
        bot.answer_callback_query(call.id, "❌ Duyuru bulunamadı!")
        return
    
    # Gönderim başlıyor
    bot.edit_message_text(
        f"⏳ **Gönderiliyor...**\n\n0/{len(users)} kullanıcı",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # Butonları hazırla
    markup = types.InlineKeyboardMarkup(row_width=1)
    for btn in current_announcement['buttons']:
        markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    success = 0
    failed = 0
    
    # Her kullanıcıya gönder
    user_list = list(users)
    total_users = len(user_list)
    
    for i, user_id in enumerate(user_list, 1):
        try:
            if current_announcement['photo']:
                bot.send_photo(
                    user_id,
                    current_announcement['photo'],
                    caption=current_announcement['text'],
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    user_id,
                    current_announcement['text'],
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            success += 1
        except Exception as e:
            failed += 1
        
        # İlerlemeyi güncelle (her 5 kullanıcıda bir)
        if i % 5 == 0 or i == total_users:
            bot.edit_message_text(
                f"⏳ **Gönderiliyor...**\n\n{i}/{total_users} kullanıcı\n"
                f"✓ {success} başarılı\n✗ {failed} başarısız",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
    
    # Sonuç
    result = f"""
✅ **DUYURU GÖNDERİLDİ!**

📊 **İstatistikler:**
• ✓ Başarılı: {success}
• ✗ Başarısız: {failed}
• 👥 Toplam: {total_users}
• 🎯 Başarı Oranı: %{(success/total_users*100):.1f}

🕐 **Zaman:** {time.strftime('%H:%M:%S')}
"""
    
    bot.edit_message_text(
        result,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # Temizle
    current_announcement = None
    user_states.pop(call.from_user.id, None)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    users.add(message.from_user.id)
    
    # Eğer bir state'de değilse ve admin değilse
    if (message.from_user.id not in user_states and 
        str(message.from_user.id) != ADMIN_ID):
        bot.reply_to(
            message,
            "🤖 Bu bot sadece duyuru almak içindir.\n"
            "Duyurular yönetici tarafından gönderilecektir."
        )

if __name__ == "__main__":
    print("=" * 40)
    print("🤖 DUYURU BOTU ÇALIŞIYOR")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kayıtlı Kullanıcı: {len(users)}")
    print("=" * 40)
    
    bot.infinity_polling()
