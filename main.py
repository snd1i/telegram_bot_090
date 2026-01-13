import os
import telebot
from telebot import types
import duyuru
import diller
import help_module  # YENİ IMPORT

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "5541236874"

bot = telebot.TeleBot(TOKEN)

# Tüm kullanıcıları sakla (help_module'dan erişilebilir olacak)
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
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i + 1])
        else:
            markup.row(buttons[i])
    
    return markup

def create_welcome_buttons(lang_data):
    """Hoşgeldin mesajı butonlarını oluştur"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
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

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    users.add(user_id)
    
    user_lang = diller.get_user_language(user_id)
    
    if user_lang:
        show_welcome_message(message, user_lang)
    else:
        show_language_selection(message)

def show_language_selection(message):
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
    user_id = message.from_user.id
    
    if not lang_code:
        lang_code = diller.get_user_language(user_id) or 'tr'
    
    lang_data = diller.DILLER.get(lang_code, diller.DILLER['tr'])
    
    user_name = diller.format_user_name(message.from_user)
    
    markup = create_welcome_buttons(lang_data)
    
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
    
    if str(user_id) == ADMIN_ID:
        admin_stats = f"\n\n📊 **Admin İstatistik:**\n• 👥 Toplam kullanıcı: {len(users)}\n• 🔧 Duyuru gönder: /send"
        welcome_text += admin_stats
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    user_id = call.from_user.id
    lang_code = call.data.replace('lang_', '')
    
    if lang_code in diller.DILLER:
        diller.set_user_language(user_id, lang_code)
        
        lang_data = diller.DILLER[lang_code]
        try:
            bot.edit_message_text(
                f"✅ {lang_data['name']}",
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass
        
        show_welcome_message(call.message, lang_code)

@bot.message_handler(commands=['language', 'dil'])
def change_language(message):
    show_language_selection(message)

# ESKİ /help KOMUTUNU SİLİYORUZ veya YORUM SATIRI YAPIYORUZ
# @bot.message_handler(commands=['help'])
# def help_command(message):
#     pass

@bot.message_handler(commands=['send'])
def send_command(message):
    user_id = message.from_user.id
    
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
    if str(message.from_user.id) == ADMIN_ID:
        bot.reply_to(
            message,
            f"📊 **Admin İstatistikleri**\n\n"
            f"• 👥 Toplam Kullanıcı: {len(users)}\n"
            f"• 🤖 Bot Durumu: Aktif\n"
            f"• 🔑 Admin ID: {ADMIN_ID}",
            parse_mode='Markdown'
        )
    else:
        lang_data = diller.get_language_data(message.from_user.id)
        bot.reply_to(
            message,
            f"⛔ {lang_data['help_command']} /help"
        )

# /id komutu - test için
@bot.message_handler(commands=['id'])
def id_command(message):
    user_id = message.from_user.id
    is_admin = (str(user_id) == ADMIN_ID)
    user_lang = diller.get_user_language(user_id) or 'Belirtilmemiş'
    
    bot.reply_to(
        message,
        f"👤 **Test Bilgileri:**\n"
        f"• ID: `{user_id}`\n"
        f"• Admin mi: {'✅ Evet' if is_admin else '❌ Hayır'}\n"
        f"• Dil: {user_lang}\n"
        f"• Admin ID ayarı: `{ADMIN_ID}`",
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if not call.data.startswith('lang_'):
        duyuru.handle_duyuru_callbacks(call)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    duyuru.process_duyuru_photo(message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    users.add(user_id)
    
    if not message.text.startswith('/'):
        lang_data = diller.get_language_data(user_id)
        bot.reply_to(
            message,
            f"🤖 {lang_data['welcome_line2']}\n\n"
            f"{lang_data['help_command']}: /help"
        )

if __name__ == "__main__":
    # Duyuru modülünü başlat
    duyuru.init_bot(bot, users)
    
    # YARDIM MODÜLÜNÜ KUR
    help_module.setup_help_commands(bot)
    
    print("=" * 50)
    print("🤖 BOT BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(users)}")
    print("=" * 50)
    print("✅ YENİ /help komutu kuruldu")
    print("✅ Diğer dosyalar değişmedi")
    print("=" * 50)
    
    bot.infinity_polling()
