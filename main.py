import os
import telebot
from telebot import types
import duyuru
import diller
import subscription
import threading
import time

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "5541236874"

bot = telebot.TeleBot(TOKEN)

# Tüm kullanıcıları sakla
users = set()
# Kullanıcı chat ID'lerini sakla {user_id: chat_id}
user_chats = {}

# Bot'u subscription modülüne ver
subscription.init_bot(bot)

def start_auto_checkers():
    """Otomatik kontrolleri başlat"""
    # Kanaldan ayrılma kontrolü
    subscription.start_unsubscribe_checker()
    print("✅ Otomatik kontroller başlatıldı")

def get_user_chat_id(user_id):
    """Kullanıcının chat ID'sini getir"""
    return user_chats.get(user_id)

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
    chat_id = message.chat.id
    users.add(user_id)
    user_chats[user_id] = chat_id
    
    print(f"🚀 /start: {user_id}")
    
    # ADMIN için direkt devam et
    if str(user_id) == ADMIN_ID:
        subscription.add_active_user(user_id)
        user_lang = diller.get_user_language(user_id)
        if user_lang:
            show_welcome_message(message, user_lang)
        else:
            show_language_selection(message)
        return
    
    # Aktif kullanıcı olarak işaretle
    subscription.add_active_user(user_id)
    
    # GERÇEK ZAMANLI abonelik kontrolü (cache bypass)
    is_subscribed = subscription.check_subscription_real_time(user_id)
    
    if is_subscribed:
        # Abone, normal akış
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
            subscription.show_subscription_required(chat_id, user_id, user_lang)
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
        admin_stats = f"\n\n📊 **Admin İstatistik:**\n• 👥 Toplam kullanıcı: {len(users)}\n• 🔧 Duyuru gönder: /send\n• 📢 Kanal değiştir: /channel"
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
    subscription.add_active_user(user_id)
    
    # HEMEN hoşgeldin mesajını göster
    user_lang = diller.get_user_language(user_id) or 'tr'
    show_welcome_message(message, user_lang)

# /help komutu (kısa tutalım)
@bot.message_handler(commands=['help', 'yardim', 'h'])
def help_command(message):
    """Kısa yardım komutu"""
    user_id = message.from_user.id
    
    # Aktif kullanıcı olarak işaretle
    subscription.add_active_user(user_id)
    
    lang_data = diller.get_language_data(user_id)
    user_name = diller.format_user_name(message.from_user)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            lang_data.get('button_channel', 'Kanal'), 
            url=lang_data['channel_url']
        ),
        types.InlineKeyboardButton(
            lang_data.get('button_prompts', 'Prompts'), 
            url=lang_data['prompts_url']
        )
    )
    
    help_text = f"""<b>{lang_data.get('help_greeting', 'Merhaba').format(name=user_name)}</b>

<b>Komutlar:</b>
• /start - Botu başlat
• /help - Yardım
• /language - Dil değiştir

<b>Promptlar için:</b>"""
    
    # Admin için ek komutları göster
    if str(user_id) == ADMIN_ID:
        help_text += f"""

<b>Admin Komutları:</b>
• /send - Duyuru gönder
• /stats - İstatistikler
• /channel - Kanal değiştir"""
    
    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    user_id = call.from_user.id
    
    # Aktif kullanıcı olarak işaretle
    subscription.add_active_user(user_id)
    
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
            show_welcome_message(call.message, lang_code)
        else:
            # GERÇEK ZAMANLI abonelik kontrolü
            is_subscribed = subscription.check_subscription_real_time(user_id)
            
            if is_subscribed:
                show_welcome_message(call.message, lang_code)
            else:
                subscription.show_subscription_required(call.message.chat.id, user_id, lang_code)

@bot.callback_query_handler(func=lambda call: call.data == 'check_subscription')
def handle_check_subscription(call):
    """Abonelik kontrol butonu"""
    subscription.handle_subscription_check(call)

@bot.message_handler(commands=['language', 'dil'])
def change_language(message):
    user_id = message.from_user.id
    subscription.add_active_user(user_id)
    show_language_selection(message)

@bot.message_handler(commands=['channel'])
def channel_command(message):
    """Kanal bilgilerini değiştir (SADECE ADMIN)"""
    user_id = message.from_user.id
    
    if str(user_id) != ADMIN_ID:
        lang_data = diller.get_language_data(user_id)
        bot.reply_to(
            message, 
            f"⛔ {lang_data.get('help_command', 'Yardım için')} /help"
        )
        return
    
    # Mevcut kanal bilgilerini göster
    current_channel = subscription.REQUIRED_CHANNEL
    
    # Kanal ayarlama klavyesi
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Mevcut kanalı göster butonu
    markup.add(
        types.InlineKeyboardButton(
            f"📊 Mevcut Kanal: {current_channel['name']}",
            url=current_channel['url']
        )
    )
    
    # Gizli/Grup kanalı için buton
    markup.add(
        types.InlineKeyboardButton(
            "🔒 Gizli/Grup Kanalı Ayarla",
            callback_data='set_private_channel'
        )
    )
    
    # Normal kanal için buton
    markup.add(
        types.InlineKeyboardButton(
            "📢 Normal Kanal Ayarla",
            callback_data='set_public_channel'
        )
    )
    
    bot.send_message(
        message.chat.id,
        f"🔧 **Kanal Yönetimi**\n\n"
        f"**Mevcut Kanal:**\n"
        f"• İsim: {current_channel['name']}\n"
        f"• Kullanıcı adı: @{current_channel['username']}\n"
        f"• URL: {current_channel['url']}\n\n"
        f"Hangi tür kanal ayarlamak istiyorsunuz?",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data in ['set_private_channel', 'set_public_channel'])
def handle_channel_type(call):
    """Kanal tipi seçimi"""
    user_id = call.from_user.id
    
    if str(user_id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Yetkiniz yok!", show_alert=True)
        return
    
    if call.data == 'set_private_channel':
        # Gizli/Grup kanalı için
        msg_text = (
            "🔒 **Gizli/Grup Kanalı Ayarlama**\n\n"
            "Gizli kanal veya grup için **Chat ID** gereklidir.\n\n"
            "Chat ID'yi şu şekilde alabilirsiniz:\n"
            "1. @userinfobot'dan grubun ID'sini alın\n"
            "2. Veya botu kanala/gruba ekleyin ve /start yazın\n\n"
            "Lütfen formatı kullanarak gönderin:\n"
            "`Kanal Adı | chat_id | invite_link`\n\n"
            "**Örnek:**\n"
            "`Gizli Kanal | -1001234567890 | https://t.me/+AbCdEfGhIjKlMnOp`\n\n"
            "⚠️ **Not:** Chat ID negatif bir sayıdır (örn: -1001234567890)"
        )
        
    else:  # set_public_channel
        # Normal kanal için
        msg_text = (
            "📢 **Normal Kanal Ayarlama**\n\n"
            "Normal kanal için **@kullanıcı_adı** gereklidir.\n\n"
            "Lütfen formatı kullanarak gönderin:\n"
            "`Kanal Adı | @kullanici_adi | https://t.me/kullanici_adi`\n\n"
            "**Örnek:**\n"
            "`Yeni Kanal | yenikanal | https://t.me/yenikanal`\n\n"
            "⚠️ **Not:** @ işaretini kullanıcı adından önce yazmayın"
        )
    
    # Mesajı düzenle
    try:
        bot.edit_message_text(
            msg_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    except:
        pass
    
    # Yeni mesaj için sonraki adımı kaydet
    msg = bot.send_message(
        call.message.chat.id,
        "📝 Lütfen yeni kanal bilgilerini yukarıdaki formatta gönderin:",
        parse_mode='Markdown'
    )
    
    # Kanal tipini sakla ve sonraki adımı kaydet
    bot.register_next_step_handler(msg, process_channel_settings, call.data)

def process_channel_settings(message, channel_type):
    """Kanal ayarlarını işle"""
    try:
        user_id = message.from_user.id
        
        if str(user_id) != ADMIN_ID:
            return
        
        # Mesajı parçala
        parts = message.text.split('|')
        if len(parts) != 3:
            bot.reply_to(
                message,
                "❌ Hatalı format! Lütfen doğru formatta gönderin.\n\n"
                "Format: `Kanal Adı | ID/KullanıcıAdı | Link`",
                parse_mode='Markdown'
            )
            return
        
        # Parçaları temizle
        channel_name = parts[0].strip()
        channel_identifier = parts[1].strip()
        channel_url = parts[2].strip()
        
        # Gizli kanal için chat ID kontrolü
        if channel_type == 'set_private_channel':
            # Chat ID negatif bir sayı olmalı
            if not channel_identifier.startswith('-100'):
                bot.reply_to(
                    message,
                    "❌ Geçersiz Chat ID! Gizli kanal/grup için -100 ile başlayan bir ID girmelisiniz.\n\n"
                    "Örnek: `-1001234567890`",
                    parse_mode='Markdown'
                )
                return
            channel_username = channel_identifier  # Chat ID'yi username olarak kullan
        
        else:  # Normal kanal
            # @ işaretini kaldır
            channel_username = channel_identifier.replace('@', '')
        
        # subscription.py dosyasındaki kanalı güncelle
        subscription.REQUIRED_CHANNEL['name'] = channel_name
        subscription.REQUIRED_CHANNEL['username'] = channel_username
        subscription.REQUIRED_CHANNEL['url'] = channel_url
        
        # Tüm kullanıcı abonelik cache'ini temizle
        subscription.user_subscriptions.clear()
        subscription.pending_checks.clear()
        
        bot.reply_to(
            message,
            f"✅ **Kanal başarıyla güncellendi!**\n\n"
            f"**Yeni Kanal:** {channel_name}\n"
            f"**{'Chat ID' if channel_type == 'set_private_channel' else 'Kullanıcı Adı'}: **"
            f"{channel_username}\n"
            f"**URL:** {channel_url}\n\n"
            f"📢 Tüm kullanıcılar yeni kanala abone olmalıdır.\n"
            f"🔄 Abonelik kontrolleri sıfırlandı.",
            parse_mode='Markdown'
        )
        
        print(f"🔧 Kanal güncellendi: {channel_name} ({channel_username}) - Tip: {'Gizli' if channel_type == 'set_private_channel' else 'Normal'}")
        
    except Exception as e:
        bot.reply_to(
            message,
            f"❌ Bir hata oluştu: {str(e)}"
        )

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
            f"• 🔑 Admin ID: {ADMIN_ID}\n"
            f"• 📢 Aktif Kanal: {subscription.REQUIRED_CHANNEL['name']}\n"
            f"• 🔗 Kanal URL: {subscription.REQUIRED_CHANNEL['url']}",
            parse_mode='Markdown'
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    if call.data.startswith('lang_'):
        pass
    elif call.data == 'check_subscription':
        pass
    elif call.data in ['set_private_channel', 'set_public_channel']:
        handle_channel_type(call)
    else:
        duyuru.handle_duyuru_callbacks(call)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    subscription.add_active_user(user_id)
    duyuru.process_duyuru_photo(message)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    users.add(user_id)
    subscription.add_active_user(user_id)
    
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
    
    # Otomatik kontrolleri başlat
    start_auto_checkers()
    
    print("=" * 60)
    print("🤖 PROMPT BOTU BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(users)}")
    print(f"📢 Aktif Kanal: {subscription.REQUIRED_CHANNEL['name']}")
    print(f"🔗 Kanal URL: {subscription.REQUIRED_CHANNEL['url']}")
    print("=" * 60)
    print("✅ GERÇEK ZAMANLI Abonelik Kontrolü")
    print("✅ Kanaldan ayrılma tespiti (her 1 dakikada)")
    print("✅ Otomatik hoşgeldin mesajı")
    print("✅ Sadeleştirilmiş abonelik mesajı")
    print("✅ Kanal yönetimi (/channel komutu)")
    print("=" * 60)
    
    bot.infinity_polling()
