import telebot
from telebot import types
import diller
import time

# Telegram bot instance'ı
bot = None

# Zorunlu kanallar
REQUIRED_CHANNELS = [
    {
        'name': 'SNDI Kanal 📢',
        'url': 'https://t.me/sndiyi',
        'username': 'sndiyi'
    },
    {
        'name': 'Prompts 🔥',
        'url': 'https://t.me/PrompttAI_bot/Prompts', 
        'username': 'PrompttAI_bot'
    }
]

# Abonelik durumu
user_subscriptions = {}
pending_checks = {}  # Bekleyen kontroller

def init_bot(bot_instance):
    """Bot instance'ını başlat"""
    global bot
    bot = bot_instance

def get_subscription_text(lang_code):
    """Dile göre abonelik mesajı al"""
    if lang_code == 'ku_badini':
        return {
            'title': "🔒 پێدفیە کەنالێ مە جوین بکی دا بشێی بوتی بکار بینی",
            'channels_title': "کەنالێ یجباری",
            'steps_title': "ختوە",
            'step1': "تلا خول کەنالی بدە",
            'step2': "جوین بکە", 
            'step3': "پشتی جوین دکی تبلا خول دکمادی بدە",
            'success': "✅ دەستخوش جویناتە هاتە وەلگرتن!",
            'welcome': "🤖 خێرهاتی بو نافا بوتی!",
            'not_subscribed': "هێشتا تە کەنال جوین نەکرە",
            'check_button': "من جوین کر 🔁",
            'already_subscribed': "✅ تە هەر جوین کرەویە ب هەموا کەنالا!"
        }
    elif lang_code == 'tr':
        return {
            'title': "🔒 Botu kullanmak için kanallarımıza abone olmalısınız!",
            'channels_title': "Zorunlu Kanallar",
            'steps_title': "Adımlar",
            'step1': "Kanallara tıklayın",
            'step2': "Abone olun",
            'step3': "Abone olduktan sonra butona tıklayın",
            'success': "✅ Tebrikler! Tüm kanallara abone oldunuz.",
            'welcome': "🤖 Bot'a hoş geldiniz!",
            'not_subscribed': "Hala abone değilsiniz",
            'check_button': "Aboneliği Kontrol Et 🔁",
            'already_subscribed': "✅ Zaten tüm kanallara abonesiniz!"
        }
    else:
        return {
            'title': "🔒 You must subscribe to our channels to use the bot!",
            'channels_title': "Required Channels",
            'steps_title': "Steps",
            'step1': "Click on channels",
            'step2': "Subscribe",
            'step3': "After subscribing click the button",
            'success': "✅ Congratulations! You subscribed to all channels.",
            'welcome': "🤖 Welcome to the bot!",
            'not_subscribed': "Still not subscribed",
            'check_button': "Check Subscription 🔁",
            'already_subscribed': "✅ You're already subscribed to all channels!"
        }

def check_subscription(user_id):
    """Kullanıcının tüm kanallara abone olup olmadığını kontrol et"""
    try:
        for channel in REQUIRED_CHANNELS:
            try:
                # Kullanıcının kanalda olup olmadığını kontrol et
                member = bot.get_chat_member(f'@{channel["username"]}', user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    return False, channel
            except Exception as e:
                print(f"Kanal kontrol hatası {channel['username']}: {e}")
                return False, channel
        return True, None
    except Exception as e:
        print(f"Abonelik kontrol hatası: {e}")
        return False, REQUIRED_CHANNELS[0]

def create_subscription_keyboard(lang_code):
    """Abonelik kontrol klavyesi oluştur"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    text = get_subscription_text(lang_code)
    
    for channel in REQUIRED_CHANNELS:
        markup.add(
            types.InlineKeyboardButton(
                f"📢 {channel['name']}",
                url=channel['url']
            )
        )
    
    markup.add(
        types.InlineKeyboardButton(
            text['check_button'],
            callback_data='check_subscription'
        )
    )
    
    return markup

def show_subscription_required(chat_id, user_id, lang_code='tr'):
    """Abonelik gerekli mesajını göster"""
    # Önce kullanıcının zaten abone olup olmadığını kontrol et
    is_subscribed, missing_channel = check_subscription(user_id)
    
    if is_subscribed:
        # Zaten abone, mesaj gösterme, True döndür
        return True
    
    # Abone değil, mesaj göster
    text = get_subscription_text(lang_code)
    markup = create_subscription_keyboard(lang_code)
    
    message_text = f"""
{text['title']}

📌 **{text['channels_title']}:**
1️⃣ {REQUIRED_CHANNELS[0]['name']} - Tüm güncellemeler
2️⃣ {REQUIRED_CHANNELS[1]['name']} - Hazır promptlar

⚠️ **{text['steps_title']}:**
• {text['step1']}
• {text['step2']}
• {text['step3']}
"""
    
    # Mesajı gönder ve ID'sini kaydet
    msg = bot.send_message(
        chat_id,
        message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    # Mesaj ID'sini kaydet (sonra silmek için)
    pending_checks[user_id] = {
        'message_id': msg.message_id,
        'chat_id': chat_id
    }
    return False

def handle_subscription_check(call):
    """Abonelik kontrol callback'ini handle et"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Kullanıcı dilini al
    lang_data = diller.get_language_data(user_id)
    lang_code = lang_data['code'] if lang_data else 'tr'
    text = get_subscription_text(lang_code)
    
    # Aboneliği kontrol et
    is_subscribed, missing_channel = check_subscription(user_id)
    
    if is_subscribed:
        # Abone olmuş
        user_subscriptions[user_id] = True
        
        # Eski abonelik mesajını sil
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        
        # Bekleyen mesajı temizle
        if user_id in pending_checks:
            del pending_checks[user_id]
        
        # Başarı mesajı göster (geçici)
        success_msg = bot.send_message(
            chat_id,
            f"{text['success']}\n{text['welcome']}",
            parse_mode='Markdown'
        )
        
        # 2 saniye bekle ve sil
        time.sleep(2)
        try:
            bot.delete_message(chat_id, success_msg.message_id)
        except:
            pass
        
        # Ana modüle sinyal gönder
        from main import on_subscription_complete
        on_subscription_complete(call.message, user_id)
        
    else:
        # Hala abone değil
        bot.answer_callback_query(
            call.id,
            f"❌ {text['not_subscribed']}: {missing_channel['name']}",
            show_alert=True
        )

def is_user_subscribed(user_id):
    """Kullanıcı abone mi kontrol et"""
    # Önce cache'den kontrol et
    if user_id in user_subscriptions:
        return user_subscriptions[user_id]
    
    # Cache'de yoksa API'den kontrol et
    is_subscribed, _ = check_subscription(user_id)
    if is_subscribed:
        user_subscriptions[user_id] = True
    return is_subscribed

def cleanup_pending_message(user_id):
    """Bekleyen mesajı temizle"""
    if user_id in pending_checks:
        try:
            data = pending_checks[user_id]
            bot.delete_message(data['chat_id'], data['message_id'])
            del pending_checks[user_id]
        except:
            pass

def setup_subscription_handlers():
    """Abonelik handler'larını kur (main.py'de yapılacak)"""
    pass
