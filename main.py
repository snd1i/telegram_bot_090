import os
import telebot
from telebot import types
import duyuru
import diller

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "5541236874"

bot = telebot.TeleBot(TOKEN)

# Tüm kullanıcıları sakla
users = set()

def create_language_keyboard():
    """Dil seçim klavyesi oluştur"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    for lang_code, lang_data in diller.DILLER.items():
        btn = types.InlineKeyboardButton(
            lang_data['name'], 
            callback_data=f'lang_{lang_code}'
        )
        buttons.append(btn)
    
    # 2'li sıralar halinde ekle
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i + 1])
        else:
            markup.row(buttons[i])
    
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    users.add(user_id)
    
    # Eğer kullanıcı daha önce dil seçtiyse doğrudan hoş geldin göster
    user_lang = diller.get_user_language(user_id)
    
    if user_lang:
        # Dil zaten seçilmiş, hoş geldin göster
        show_welcome_message(message, user_lang)
    else:
        # Dil seçimi göster
        show_language_selection(message)

def show_language_selection(message):
    """Dil seçim ekranını göster"""
    markup = create_language_keyboard()
    
    bot.send_message(
        message.chat.id,
        "🌍 **Please select your language / لطفاً زبان خود را انتخاب کنید**\n"
        "────────────\n"
        "**Dil seçin / اختر اللغة / زمانەکێ هەلبژێرە**",
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_welcome_message(message, lang_code=None):
    """Hoş geldin mesajını göster"""
    user_id = message.from_user.id
    
    if not lang_code:
        lang_code = diller.get_user_language(user_id) or 'tr'
    
    lang_data = diller.DILLER.get(lang_code, diller.DILLER['tr'])
    
    # Admin ise istatistik ekle
    if str(user_id) == ADMIN_ID:
        welcome_text = f"""
{lang_data['welcome']} 👋

{lang_data['description']}

📊 **Admin Statistics:**
• 👥 Total users: {len(users)}
• 🔧 Send prompts: /send
• 🌐 Language: {lang_data['name']}
"""
    else:
        welcome_text = f"""
{lang_data['welcome']} 👋

{lang_data['description']}

🌐 {lang_data['language']}: {lang_data['name']}
"""
    
    # Ana menü butonları
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if str(user_id) == ADMIN_ID:
        markup.row(types.KeyboardButton(f"📤 {lang_data['start']}"))
    
    markup.row(
        types.KeyboardButton(f"🌐 {lang_data['language']}"),
        types.KeyboardButton(f"❓ {lang_data['help']}")
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    """Dil seçimini işle"""
    user_id = call.from_user.id
    lang_code = call.data.replace('lang_', '')
    
    if lang_code in diller.DILLER:
        # Dil tercihini kaydet
        diller.set_user_language(user_id, lang_code)
        
        # Callback mesajını güncelle
        lang_data = diller.DILLER[lang_code]
        bot.edit_message_text(
            f"✅ {lang_data['language']}: {lang_data['name']}",
            call.message.chat.id,
            call.message.message_id
        )
        
        # Hoş geldin mesajını göster
        show_welcome_message(call.message, lang_code)

@bot.message_handler(commands=['language', 'dil'])
def change_language(message):
    """Dil değiştirme komutu"""
    show_language_selection(message)

@bot.message_handler(commands=['send'])
def send_command(message):
    user_id = message.from_user.id
    
    # Kullanıcı dilini al
    lang_code = diller.get_user_language(user_id) or 'tr'
    lang_data = diller.DILLER.get(lang_code, diller.DILLER['tr'])
    
    if str(user_id) != ADMIN_ID:
        bot.reply_to(
            message, 
            f"⛔ {lang_data['choose']} {lang_data['help']} /help"
        )
        return
    
    msg = bot.send_message(
        message.chat.id,
        f"📝 **{lang_data['start']}**\n\n"
        f"{lang_data['description']}",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, duyuru.process_duyuru_text)

# Diğer callback'ler
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    # Dil seçimi değilse duyuru callback'lerine yönlendir
    if not call.data.startswith('lang_'):
        duyuru.handle_duyuru_callbacks(call)

# Fotoğraf handler
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    duyuru.process_duyuru_photo(message)

# Buton mesajlarını işle
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    users.add(user_id)
    
    lang_code = diller.get_user_language(user_id) or 'tr'
    lang_data = diller.DILLER.get(lang_code, diller.DILLER['tr'])
    
    # Dil değiştirme butonu
    if "🌐" in message.text:
        show_language_selection(message)
    
    # Yardım butonu
    elif "❓" in message.text:
        bot.reply_to(
            message,
            f"ℹ️ **{lang_data['help']}**\n\n"
            f"• {lang_data['start']}: /start\n"
            f"• {lang_data['language']}: /language\n"
            f"• {lang_data['description']}",
            parse_mode='Markdown'
        )
    
    # Başlat butonu (sadece admin)
    elif "📤" in message.text and str(user_id) == ADMIN_ID:
        send_command(message)
    
    else:
        bot.reply_to(
            message,
            f"🤖 {lang_data['description']}\n\n"
            f"{lang_data['help']}: /help"
        )

if __name__ == "__main__":
    # Duyuru modülünü başlat
    duyuru.init_bot(bot, users)
    
    print("=" * 50)
    print("🤖 PROMPT BOTU BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(users)}")
    print(f"🌍 Diller: {len(diller.DILLER)} dil")
    print("=" * 50)
    
    bot.infinity_polling()
