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

@bot.message_handler(commands=['start'])
def start(message):
    users.add(message.from_user.id)
    
    bot.reply_to(
        message,
        f"🤖 Bot aktif!\nKullanıcı: {len(users)}",
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
        "📝 **Duyuru metnini yazın:**",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_text)

def process_text(message):
    global current_announcement
    
    # Metni kaydet
    current_announcement = {
        'text': message.text,
        'photo': None,
        'buttons': []
    }
    
    # Buton ekleme seçeneği
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("➕ Buton Ekle", callback_data='add_button'),
        types.InlineKeyboardButton("➡️ Devam Et", callback_data='no_button')
    )
    
    bot.send_message(
        message.chat.id,
        "🔘 Buton eklemek ister misiniz?",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global current_announcement
    
    if call.data == 'add_button':
        bot.edit_message_text(
            "🔗 Buton formatı:\n`Metin - URL`\n\nÖrnek:\n`Google - https://google.com`\n\nButonu yazın:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(call.message, add_button)
    
    elif call.data == 'no_button':
        ask_for_photo(call.message)
    
    elif call.data == 'add_photo':
        bot.edit_message_text(
            "🖼️ Fotoğraf gönderin:",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(call.message, process_photo)
    
    elif call.data == 'no_photo':
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

def add_button(message):
    global current_announcement
    
    if ' - ' in message.text:
        text, url = message.text.split(' - ', 1)
        current_announcement['buttons'].append({
            'text': text.strip(),
            'url': url.strip()
        })
        
        # Başka buton eklemek ister mi?
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("➕ Başka Buton Ekle", callback_data='add_button'),
            types.InlineKeyboardButton("➡️ Devam Et", callback_data='no_button')
        )
        
        bot.send_message(
            message.chat.id,
            f"✅ Buton eklendi: {text.strip()}",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Hatalı format! Tekrar deneyin: `Metin - URL`"
        )
        bot.register_next_step_handler(message, add_button)

def ask_for_photo(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🖼️ Fotoğraf Ekle", callback_data='add_photo'),
        types.InlineKeyboardButton("➡️ Devam Et", callback_data='no_photo')
    )
    
    bot.send_message(
        message.chat.id,
        "Fotoğraf eklemek ister misiniz?",
        reply_markup=markup
    )

def process_photo(message):
    global current_announcement
    
    if message.content_type == 'photo':
        current_announcement['photo'] = message.photo[-1].file_id
        show_preview(message)
    else:
        bot.send_message(message.chat.id, "❌ Lütfen fotoğraf gönderin.")
        bot.register_next_step_handler(message, process_photo)

def show_preview(message):
    global current_announcement
    
    if not current_announcement:
        return
    
    # Mesaj butonları
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Kullanıcı butonları
    for btn in current_announcement['buttons']:
        markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    # İşlem butonları
    markup.row(
        types.InlineKeyboardButton("🚀 GÖNDER", callback_data='send_announcement'),
        types.InlineKeyboardButton("❌ İPTAL", callback_data='cancel_announcement')
    )
    
    preview_text = f"""
📢 **DUYURU**
{current_announcement['text']}
────────────
👥 Kullanıcı: {len(users)}
🕐 {time.strftime('%H:%M')}
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
        return
    
    # Gönderim başlıyor
    bot.edit_message_text(
        f"⏳ Gönderiliyor... 0/{len(users)}",
        call.message.chat.id,
        call.message.message_id
    )
    
    # Butonları hazırla
    markup = types.InlineKeyboardMarkup(row_width=1)
    for btn in current_announcement['buttons']:
        markup.add(types.InlineKeyboardButton(btn['text'], url=btn['url']))
    
    success = 0
    failed = 0
    
    # Her kullanıcıya gönder
    for i, user_id in enumerate(list(users), 1):
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
        except:
            failed += 1
        
        # İlerlemeyi güncelle
        if i % 10 == 0 or i == len(users):
            bot.edit_message_text(
                f"⏳ Gönderiliyor... {i}/{len(users)}",
                call.message.chat.id,
                call.message.message_id
            )
    
    # Sonuç
    result = f"""
✅ **GÖNDERİLDİ!**

✓ Başarılı: {success}
✗ Başarısız: {failed}
👥 Toplam: {len(users)}
🕐 {time.strftime('%H:%M:%S')}
    """
    
    bot.edit_message_text(
        result,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    # Temizle
    current_announcement = None

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    users.add(message.from_user.id)

if __name__ == "__main__":
    print(f"🤖 Bot başlatıldı | Kullanıcı: {len(users)}")
    bot.infinity_polling()
