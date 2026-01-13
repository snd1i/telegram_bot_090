import os
import telebot
from telebot import types
import duyuru
import diller
import subscription
import threading
import time

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "5541236874"  # TIRNAK İÇİNDE

bot = telebot.TeleBot(TOKEN)

# Tüm kullanıcıları sakla
users = set()

# Bot'u subscription modülüne ver
subscription.init_bot(bot)

def start_auto_checker():
    """Otomatik abonelik kontrolü başlat"""
    def checker():
        while True:
            try:
                subscription.auto_check_subscription()
            except Exception as e:
                print(f"Otomatik kontrol hatası: {e}")
            time.sleep(5)  # Her 5 saniyede bir kontrol et
    
    thread = threading.Thread(target=checker, daemon=True)
    thread.start()
    print("✅ Otomatik abonelik kontrolü başlatıldı")

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
    
    print(f"🚀 /start: {user_id} (Admin: {str(user_id) == ADMIN_ID})")
    
    # ADMIN için direkt devam et
    if str(user_id) == ADMIN_ID:
        user_lang = diller.get_user_language(user_id)
        if user_lang:
            show_welcome_message(message, user_lang)
        else:
            show_language_selection(message)
        return
    
    # NORMAL KULLANICI için abonelik kontrolü
    is_subscribed = subscription.is_user_subscribed(user_id)
    
    if is_subscribed:
        # Zaten abone, normal akış
        user_lang = diller.get_user_language(user_id)
        if user_lang:
            show_welcome_message(message, user_lang)
        else:
            show_language_selection(message)
    else:
        # Abone değil, dil seçimine yönlendir
        user_lang = diller.get_user_language(user_id)
        if user_lang:
            # Dil seçmiş, direkt abonelik mesajı göster
            subscription.show_subscription_required(message.chat.id, user_id, user_lang)
        else:
            # Dil seçimi göster
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

def on_subscription_complete(message, user_id):
    """Abonelik tamamlandığında çağrılır (butonla)"""
    subscription.cleanup_pending_message(user_id)
    user_lang = diller.get_user_language(user_id) or 'tr'
    show_welcome_message(message, user_lang)

def on_subscription_complete_auto(chat_id, user_id, lang_code):
    """Otomatik abonelik tamamlandığında çağrılır"""
    subscription.cleanup_pending_message(user_id)
    
    # Fake message oluştur
    class FakeMessage:
        def __init__(self, chat_id, user_id):
            self.chat = type('obj', (object,), {'id': chat_id})
            self.from_user = type('obj', (object,), {'id': user_id})
    
    fake_msg = FakeMessage(chat_id, user_id)
    show_welcome_message(fake_msg, lang_code)

# /help komutu (önceki gibi kalacak)
@bot.message_handler(commands=['help', 'yardim', 'h'])
def help_command(message):
    """Yardım komutu"""
    user_id = message.from_user.id
    is_admin = (str(user_id) == ADMIN_ID)
    
    lang_data = diller.get_language_data(user_id)
    user_name = diller.format_user_name(message.from_user)
    
    # 3 butonlu klavye
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            lang_data.get('button_channel', 'Kanal'), 
            url=lang_data['channel_url']
        ),
        types.InlineKeyboardButton(
            lang_data.get('button_prompts', 'Prompts'), 
            url=lang_data['prompts_url']
        ),
        types.InlineKeyboardButton(
            lang_data.get('button_support', 'Destek'), 
            url=lang_data['support_url']
        )
    )
    
    help_text = f"""<b>{lang_data.get('help_greeting', 'Merhaba').format(name=user_name)}</b>

<b>{lang_data.get('help_info_title', 'Botumuz hakkında bilgiler')}</b>
• {lang_data.get('help_bot_for', 'Bot promptslar içindir')}
• {lang_data.get('help_prompts_info', 'Hazır promptlar sadece kopyala yapıştır')}

<b>{lang_data.get('help_commands_title', 'Komutlar')}</b>
• {lang_data.get('help_start_cmd', '/start - Botu çalıştırmak için')}
• {lang_data.get('help_help_cmd', '/help - Yardım için')}

<b>✨ {lang_data.get('help_prompts_access', 'Promptlara erişmek için prompts butonuna tıklayın')}</b>
<b>ℹ️ {lang_data.get('help_more_info', 'Daha fazla bilgi için aşağıdaki butonlara tıklayın')}</b>"""
    
    if is_admin:
        help_text += f"""

<b>👑 Admin Komutları:</b>
• /send - Duyuru gönder
• /stats - İstatistikler"""
    
    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    user_id = call.from_user.id
    lang_code = call.data.replace('lang_', '')
    
    if lang_code in diller.DILLER:
        # Dil tercihini kaydet
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
        
        # ADMIN kontrolü
        if str(user_id) == ADMIN_ID:
            # Admin için direkt hoşgeldin
            show_welcome_message(call.message, lang_code)
        else:
            # Normal kullanıcı için abonelik kontrolü
            is_subscribed = subscription.is_user_subscribed(user_id)
            
            if is_subscribed:
                # Zaten abone, direkt hoşgeldin
                show_welcome_message(call.message, lang_code)
            else:
                # Abone değil, abonelik mesajı göster
                subscription.show_subscription_required(call.message.chat.id, user_id, lang_code)

@bot.callback_query_handler(func=lambda call: call.data == 'check_subscription')
def handle_check_subscription(call):
    """Abonelik kontrol butonu"""
    subscription.handle_subscription_check(call)

# Diğer komutlar (önceki gibi)
@bot.message_handler(commands=['language', 'dil'])
def change_language(message):
    show_language_selection(message)

@bot.message_handler(commands=['send'])
def send_command(message):
    user_id = message.from_user.id
    
    if str(user_id) != ADMIN_ID:
        lang_data = diller.get_language_data(user_id)
        bot.reply_to(
            message, 
            f"⛔ {lang_data.get('help_command', 'Yardım için')} /help"
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

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if call.data.startswith('lang_'):
        pass
    elif call.data == 'check_subscription':
        pass
    else:
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
            f"{lang_data.get('help_command', 'Yardım için')}: /help"
        )

if __name__ == "__main__":
    # Duyuru modülünü başlat
    duyuru.init_bot(bot, users)
    
    # Otomatik abonelik kontrolünü başlat
    start_auto_checker()
    
    print("=" * 60)
    print("🤖 PROMPT BOTU BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(users)}")
    print(f"🌍 Diller: {len(diller.DILLER)} dil")
    print("=" * 60)
    print("✅ Zorunlu Abonelik Sistemi AKTİF")
    print("📋 Sadece 1 kanal: @sndiyi")
    print("🔘 2 buton: Kanal + Abone Oldum")
    print("🤖 Otomatik kontrol: Her 5 saniyede bir")
    print("👑 Admin: Abonelik gerekmez")
    print("=" * 60)
    
    bot.infinity_polling()
