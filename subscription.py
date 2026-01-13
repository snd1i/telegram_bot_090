import telebot
from telebot import types
import diller

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
            'success': "دەستخوش جویناتە هاتە وەلگرتن",
            'welcome': "خێرهاتی بو نافا بوتی",
            'not_subscribed': "هێشتا تە کەنال جوین نەکرە",
            'check_button': "من جوین کر"
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
            'not_subscribed': "❌ Hala abone değilsiniz",
            'check_button': "🔁 Aboneliği Kontrol Et"
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
            'not_subscribed': "❌ Still not subscribed",
            'check_button': "🔁 Check Subscription"
        }

def check_subscription(bot, user_id):
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

def show_subscription_required(bot, chat_id, user_id, lang_code='tr'):
    """Abonelik gerekli mesajını göster"""
    # Önce kullanıcının zaten abone olup olmadığını kontrol et
    is_subscribed, missing_channel = check_subscription(bot, user_id)
    
    if is_subscribed:
        # Zaten abone, abonelik mesajı gösterme
        return True
    
    # Abone değil, mesaj göster
    text = get_subscription_text(lang_code)
    markup = create_subscription_keyboard(lang_code)
    
    message_text = f"""
{text['title']}

📌 **{text['channels_title']}:**
1️⃣ SNDI Kanal - Tüm güncellemeler
2️⃣ Prompts Kanalı - Hazır promptlar

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
    pending_checks[user_id] = msg.message_id
    return False

def setup_subscription_handlers(bot):
    """Abonelik handler'larını kur"""
    
    @bot.callback_query_handler(func=lambda call: call.data == 'check_subscription')
    def handle_subscription_check(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Kullanıcı dilini al
        lang_data = diller.get_language_data(user_id)
        lang_code = lang_data['code'] if lang_data else 'tr'
        text = get_subscription_text(lang_code)
        
        # Aboneliği kontrol et
        is_subscribed, missing_channel = check_subscription(bot, user_id)
        
        if is_subscribed:
            # Abone olmuş
            user_subscriptions[user_id] = True
            
            # Eski mesajı sil
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            
            # Bekleyen mesajı temizle
            if user_id in pending_checks:
                del pending_checks[user_id]
            
            # Başarı mesajı göster
            bot.send_message(
                chat_id,
                f"{text['success']}\n\n{text['welcome']}",
                parse_mode='Markdown'
            )
            
            # Ana modüle abonelik tamamlandı sinyali gönder
            from main import on_subscription_complete
            on_subscription_complete(call.message, user_id)
            
        else:
            # Hala abone değil
            bot.answer_callback_query(
                call.id,
                f"{text['not_subscribed']}: {missing_channel['name']}",
                show_alert=True
            )
