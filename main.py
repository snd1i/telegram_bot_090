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

def create_welcome_buttons(lang_data):
    """Hoşgeldin mesajı butonlarını oluştur"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # İki buton
    markup.add(
        types.InlineKeyboardButton(
            lang_data['button_channel'], 
            url=lang_data['channel_url']
        ),
        types.InlineKeyboardButton(
            lang_data['button_prompts'], 
            url=lang_data['prompts_url']
        )
    )
    
    return markup

def create_help_buttons(lang_data):
    """Yardım mesajı butonlarını oluştur"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Destek butonu
    markup.add(
        types.InlineKeyboardButton(
            lang_data['button_support'], 
            url=lang_data['support_url']
        )
    )
    
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    users.add(user_id)
    
    # DEBUG: Hangi kullanıcı start yaptı
    print(f"🔍 /start komutu: {user_id} (Admin mi: {str(user_id) == ADMIN_ID})")
    
    # Eğer kullanıcı daha önce dil seçtiyse doğrudan hoş geldin göster
    user_lang = diller.get_user_language(user_id)
    
    if user_lang:
        print(f"✅ Kullanıcının dili var: {user_lang}")
        # Dil zaten seçilmiş, hoş geldin göster (HERKES İÇİN - ADMIN DAHİL)
        show_welcome_message(message, user_lang)
    else:
        print(f"⚠️ Kullanıcının dili yok, dil seçimi gösteriliyor")
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
    """Hoş geldin mesajını göster (HERKES İÇİN - ADMIN DAHİL)"""
    user_id = message.from_user.id
    
    # DEBUG
    print(f"👋 Hoşgeldin mesajı gösteriliyor: {user_id}, dil: {lang_code}")
    
    if not lang_code:
        lang_code = diller.get_user_language(user_id) or 'tr'
        print(f"📝 Dil belirlendi: {lang_code}")
    
    lang_data = diller.DILLER.get(lang_code, diller.DILLER['tr'])
    
    # Kullanıcı adını hazırla
    user_name = diller.format_user_name(message.from_user)
    print(f"👤 Kullanıcı adı: {user_name}")
    
    # Butonları oluştur
    markup = create_welcome_buttons(lang_data)
    
    # Hoşgeldin mesajını oluştur
    welcome_text = f"""
{lang_data['welcome_title'].format(name=user_name)}

{lang_data['welcome_line1']}
{lang_data['welcome_line2']}

{lang_data['welcome_line3']}
• {lang_data['welcome_line4']}
• {lang_data['welcome_line5']}
• {lang_data['welcome_line6']}

{lang_data['welcome_line7']}
{lang_data['welcome_line8']}
"""
    
    # Admin ise istatistik ekle (HER ZAMAN)
    if str(user_id) == ADMIN_ID:
        admin_stats = f"\n\n📊 **Admin İstatistik:**\n• 👥 Toplam kullanıcı: {len(users)}\n• 🔧 Duyuru gönder: /send"
        welcome_text += admin_stats
        print(f"👑 Admin istatistik eklendi")
    
    print(f"📨 Mesaj gönderiliyor...")
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    print(f"✅ Hoşgeldin mesajı gönderildi")

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    """Dil seçimini işle"""
    user_id = call.from_user.id
    lang_code = call.data.replace('lang_', '')
    
    print(f"🎯 Dil seçimi: {user_id} -> {lang_code}")
    
    if lang_code in diller.DILLER:
        # Dil tercihini kaydet
        diller.set_user_language(user_id, lang_code)
        print(f"💾 Dil kaydedildi: {lang_code}")
        
        # Callback mesajını güncelle
        lang_data = diller.DILLER[lang_code]
        try:
            bot.edit_message_text(
                f"✅ {lang_data['name']}",
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass
        
        # Hoş geldin mesajını göster (HERKES İÇİN)
        show_welcome_message(call.message, lang_code)

@bot.message_handler(commands=['language', 'dil'])
def change_language(message):
    """Dil değiştirme komutu"""
    print(f"🌐 Dil değiştirme: {message.from_user.id}")
    show_language_selection(message)

@bot.message_handler(commands=['help', 'yardim'])
def help_command(message):
    """Yardım komutu"""
    user_id = message.from_user.id
    print(f"❓ /help komutu: {user_id}")
    
    lang_data = diller.get_language_data(user_id)
    print(f"📚 Kullanıcı dili: {lang_data['code']}")
    
    # Butonları oluştur
    markup = create_help_buttons(lang_data)
    print(f"🔘 Butonlar oluşturuldu")
    
    # Yardım mesajı
    help_text = f"""
ℹ️ **{lang_data['help_command']}** /help

**📌 {diller.format_user_name(message.from_user)} Komutlar:**
• /start - Botu başlat
• /language - Dil değiştir
• /help - Yardım mesajı

**👑 Admin Komutları:**
• /send - Duyuru gönder
• /stats - İstatistikler

**🔗 Bağlantılar:**
• Kanal: {lang_data['channel_url']}
• Prompts: {lang_data['prompts_url']}

**❓ Sorularınız için aşağıdaki butona tıklayın:**
"""
    
    print(f"📤 Yardım mesajı gönderiliyor...")
    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    print(f"✅ Yardım mesajı gönderildi")

@bot.message_handler(commands=['send'])
def send_command(message):
    user_id = message.from_user.id
    print(f"📨 /send komutu: {user_id}")
    
    if str(user_id) != ADMIN_ID:
        lang_data = diller.get_language_data(user_id)
        bot.reply_to(
            message, 
            f"⛔ {lang_data['help_command']} /help"
        )
        return
    
    msg = bot.send_message(
        message.chat.id,
        "📝 **Duyuru metnini yazın:**\n\n"
        "Yazdıktan sonra gönder butonuna basın.",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, duyuru.process_duyuru_text)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    # SADECE ADMIN istatistik görebilir
    if str(message.from_user.id) == ADMIN_ID:
        bot.reply_to(
            message,
            f"📊 **Admin İstatistikleri**\n\n"
            f"• 👥 Toplam Kullanıcı: {len(users)}\n"
            f"• 🤖 Bot Durumu: Aktif\n"
            f"• 🔑 Admin ID: {ADMIN_ID}",
            parse_mode='Markdown'
        )

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

# Diğer mesajlar
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    users.add(user_id)
    
    lang_data = diller.get_language_data(user_id)
    
    # Eğer mesaj "/" ile başlamıyorsa
    if not message.text.startswith('/'):
        bot.reply_to(
            message,
            f"🤖 {lang_data['welcome_line2']}\n\n"
            f"{lang_data['help_command']}: /help"
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
    print("⚠️ DEBUG MODE: Tüm loglar görünecek")
    print("=" * 50)
    
    bot.infinity_polling()
