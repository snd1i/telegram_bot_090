import telebot
from telebot import types
import time

# Bot instance'ı için
bot = None
users = None

def init_bot(bot_instance, users_set):
    global bot, users
    bot = bot_instance
    users = users_set

# Geçici veri saklama
temp_data = {}

def process_duyuru_text(message):
    user_id = message.from_user.id
    
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ İşlem iptal edildi.")
        return
    
    # Metni kaydet
    temp_data[user_id] = {
        'text': message.text,
        'photo': None,
        'step': 'ask_photo'
    }
    
    # Fotoğraf sorusu
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Evet", callback_data='add_photo_yes'),
        types.InlineKeyboardButton("❌ Hayır", callback_data='add_photo_no')
    )
    
    bot.send_message(
        message.chat.id,
        f"📝 **Metin kaydedildi!**\n\n"
        f"🖼️ **Fotoğraf eklemek istiyor musunuz?**",
        reply_markup=markup
    )

def handle_duyuru_callbacks(call):
    user_id = call.from_user.id
    
    if call.data == 'add_photo_yes':
        bot.edit_message_text(
            "📸 **Fotoğraf gönderin:**\n\n"
            "Lütfen duyuru için bir fotoğraf gönderin.",
            call.message.chat.id,
            call.message.message_id
        )
        # Durumu güncelle
        if user_id in temp_data:
            temp_data[user_id]['step'] = 'waiting_photo'
    
    elif call.data == 'add_photo_no':
        if user_id in temp_data:
            data = temp_data[user_id]
            show_preview(call.message, data['text'], None)
            del temp_data[user_id]
    
    elif call.data == 'send_duyuru':
        send_duyuru_to_all(call)
    
    elif call.data == 'cancel_duyuru':
        bot.edit_message_text(
            "❌ Duyuru iptal edildi.",
            call.message.chat.id,
            call.message.message_id
        )
        if user_id in temp_data:
            del temp_data[user_id]

def process_duyuru_photo(message):
    user_id = message.from_user.id
    
    if user_id in temp_data and temp_data[user_id]['step'] == 'waiting_photo':
        if message.content_type == 'photo':
            photo_id = message.photo[-1].file_id
            temp_data[user_id]['photo'] = photo_id
            
            # Önizlemeyi göster
            data = temp_data[user_id]
            show_preview(message, data['text'], photo_id)
            
            # Temizle
            del temp_data[user_id]
        else:
            bot.send_message(message.chat.id, "❌ Lütfen fotoğraf gönderin!")

def show_preview(message, text, photo_id):
    # OTOMATİK BUTON - Her duyuruda olacak
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("prompts 🔥", url="https://t.me/PrompttAI_bot/Prompts"))
    
    # Gönder/İptal butonları
    markup.row(
        types.InlineKeyboardButton("🚀 GÖNDER", callback_data='send_duyuru'),
        types.InlineKeyboardButton("❌ İPTAL", callback_data='cancel_duyuru')
    )
    
    preview_text = f"""
📢 **DUYURU ÖNİZLEME**

{text}

────────────
👥 **Hedef:** {len(users)} kullanıcı
🕐 **Zaman:** {time.strftime('%H:%M')}
"""
    
    if photo_id:
        bot.send_photo(
            message.chat.id,
            photo_id,
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

def send_duyuru_to_all(call):
    message = call.message
    
    if message.content_type == 'photo':
        text = message.caption
        photo_id = message.photo[-1].file_id if message.photo else None
    else:
        # "DUYURU ÖNİZLEME" başlığını kaldır
        text_lines = message.text.split('\n')
        if len(text_lines) > 2:
            text = '\n'.join(text_lines[2:-6])  # Başlık ve alt çizgiyi kaldır
        else:
            text = message.text
        photo_id = None
    
    # OTOMATİK BUTON
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("prompts 🔥", url="https://t.me/PrompttAI_bot/Prompts"))
    
    # Gönderim başlıyor
    bot.edit_message_text(
        f"⏳ **Gönderiliyor...**\n\n0/{len(users)} kullanıcı",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    success = 0
    failed = 0
    total = len(users)
    
    # Her kullanıcıya gönder
    for i, user_id in enumerate(list(users), 1):
        try:
            if photo_id:
                bot.send_photo(
                    user_id,
                    photo_id,
                    caption=text,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            else:
                bot.send_message(
                    user_id,
                    text,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
            success += 1
        except:
            failed += 1
        
        # İlerlemeyi güncelle
        if i % 10 == 0 or i == total:
            bot.edit_message_text(
                f"⏳ **Gönderiliyor...**\n\n{i}/{total} kullanıcı\n"
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
• 👥 Toplam: {total}
• 🎯 Başarı Oranı: %{(success/total*100):.1f}

🕐 **Zaman:** {time.strftime('%H:%M:%S')}
"""
    
    bot.edit_message_text(
        result,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
