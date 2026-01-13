import telebot
from telebot import types
import time

bot = None
users = None

def init_bot(bot_instance, users_set):
    global bot, users
    bot = bot_instance
    users = users_set

# Duyuru verisini sakla
duyuru_data = {}

def process_duyuru_text(message):
    user_id = message.from_user.id
    
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ İptal edildi.")
        return
    
    # Metni kaydet
    duyuru_data[user_id] = {
        'text': message.text,
        'photo': None
    }
    
    # Fotoğraf sorusu
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Evet", callback_data='photo_yes'),
        types.InlineKeyboardButton("❌ Hayır", callback_data='photo_no')
    )
    
    bot.send_message(
        message.chat.id,
        "🖼️ Fotoğraf eklemek istiyor musunuz?",
        reply_markup=markup
    )

def handle_duyuru_callbacks(call):
    user_id = call.from_user.id
    
    if call.data == 'photo_yes':
        bot.send_message(
            call.message.chat.id,
            "📸 Fotoğraf gönderin:"
        )
        # Durumu kaydet
        duyuru_data[user_id]['waiting_photo'] = True
    
    elif call.data == 'photo_no':
        if user_id in duyuru_data:
            data = duyuru_data[user_id]
            show_preview(call.message, data['text'], None)
    
    elif call.data == 'send_duyuru':
        # GÖNDER butonu - ÇALIŞAN VERSİYON
        send_to_all_simple(call)
    
    elif call.data == 'cancel_duyuru':
        bot.send_message(
            call.message.chat.id,
            "❌ Duyuru iptal edildi."
        )
        if user_id in duyuru_data:
            del duyuru_data[user_id]

def process_duyuru_photo(message):
    user_id = message.from_user.id
    
    if user_id in duyuru_data and 'waiting_photo' in duyuru_data[user_id]:
        if message.content_type == 'photo':
            photo_id = message.photo[-1].file_id
            duyuru_data[user_id]['photo'] = photo_id
            
            # Önizlemeyi göster
            data = duyuru_data[user_id]
            show_preview(message, data['text'], photo_id)
        else:
            bot.send_message(message.chat.id, "❌ Lütfen fotoğraf gönderin!")

def show_preview(message, text, photo_id):
    # OTOMATİK BUTON
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("prompts 🔥", url="https://t.me/PrompttAI_bot/Prompts"))
    
    # Gönder/İptal butonları
    markup.row(
        types.InlineKeyboardButton("🚀 GÖNDER", callback_data='send_duyuru'),
        types.InlineKeyboardButton("❌ İPTAL", callback_data='cancel_duyuru')
    )
    
    preview_text = f"📢 DUYURU\n\n{text}\n\n👥 {len(users)} kullanıcı"
    
    if photo_id:
        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=preview_text,
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            preview_text,
            reply_markup=markup
        )

def send_to_all_simple(call):
    """BASİT ve ÇALIŞAN gönderim fonksiyonu"""
    
    user_id = call.from_user.id
    
    # Mesajı al
    message = call.message
    
    # Önce bir "gönderiliyor" mesajı gönder (EDIT YAPMADAN)
    status_msg = bot.send_message(
        call.message.chat.id,
        f"⏳ Gönderiliyor... 0/{len(users)}"
    )
    
    # OTOMATİK BUTON
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("prompts 🔥", url="https://t.me/PrompttAI_bot/Prompts"))
    
    # Mesaj içeriğini al
    if message.content_type == 'photo':
        # Fotoğraf mesajı
        text = message.caption
        photo_id = message.photo[-1].file_id
        has_photo = True
    else:
        # Metin mesajı
        text = message.text.replace("📢 DUYURU\n\n", "").split("\n\n👥")[0]
        photo_id = None
        has_photo = False
    
    success = 0
    failed = 0
    total = len(users)
    
    # Her kullanıcıya gönder
    user_list = list(users)
    
    for i, uid in enumerate(user_list, 1):
        try:
            if has_photo and photo_id:
                bot.send_photo(
                    uid,
                    photo_id,
                    caption=text,
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    uid,
                    text,
                    reply_markup=markup
                )
            success += 1
        except:
            failed += 1
        
        # İlerlemeyi GÜNCELLE (sadece mesajı değiştir)
        if i % 5 == 0 or i == total:
            bot.edit_message_text(
                f"⏳ Gönderiliyor... {i}/{total}\n✓ {success} başarılı\n✗ {failed} başarısız",
                status_msg.chat.id,
                status_msg.message_id
            )
    
    # Sonuç mesajı (YENİ MESAJ OLARAK)
    bot.send_message(
        call.message.chat.id,
        f"✅ Duyuru gönderildi!\n\n"
        f"✓ Başarılı: {success}\n"
        f"✗ Başarısız: {failed}\n"
        f"👥 Toplam: {total}"
    )
    
    # Önceki mesajı sil (opsiyonel)
    try:
        bot.delete_message(status_msg.chat.id, status_msg.message_id)
    except:
        pass
