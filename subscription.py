import telebot
from telebot import types
import diller
import time

# Telegram bot instance'ı
bot = None

# Zorunlu kanallar (SADECE 1 KANAL)
REQUIRED_CHANNELS = [
    {
        'name': 'SNDI Kanal 📢',
        'url': 'https://t.me/sndiyi',
        'username': 'sndiyi'
    }
]

# Abonelik durumu
user_subscriptions = {}
pending_checks = {}  # Bekleyen kontroller
last_check_time = {}  # Son kontrol zamanları

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
            'step3': "پشتی جوین دکی بوتی بەکار ینی",
            'success': "✅ دەستخوش جویناتە هاتە وەلگرتن!",
            'welcome': "🤖 خێرهاتی بو نافا بوتی!",
            'not_subscribed': "هێشتا تە کەنال جوین نەکرە",
            'check_button': "من جوین کر 🔁",
            'already_subscribed': "✅ تە هەر جوین کرەویە",
            'subscribe_button': "کەنال 📢",
            'subscribed_button': "جوین کر 🎯"
        }
    elif lang_code == 'ku_sorani':
        return {
            'title': "🔒 پێویستە بەشداربیت لە کەناڵەکانمان بۆ بەکارهێنانی بۆت!",
            'channels_title': "کەناڵە پێویستەکان",
            'steps_title': "هەنگاوەکان",
            'step1': "کرتە لەسەر کەناڵەکان بکە",
            'step2': "بەشداربە",
            'step3': "دوای بەشداربوون بۆت بەکاربهێنە",
            'success': "✅ پیرۆز بێت! بەشداربوویت لە هەموو کەناڵەکان.",
            'welcome': "🤖 بەخێربێیت بۆ بۆت!",
            'not_subscribed': "هێشتا بەشدارنەبوویت",
            'check_button': "پشکنینی بەشداربوون 🔁",
            'already_subscribed': "✅ هەر بەشداربوویت",
            'subscribe_button': "کەناڵ 📢",
            'subscribed_button': "بەشداربوو 🎯"
        }
    elif lang_code == 'tr':
        return {
            'title': "🔒 Botu kullanmak için kanalımıza abone olmalısınız!",
            'channels_title': "Zorunlu Kanal",
            'steps_title': "Adımlar",
            'step1': "Kanala tıklayın",
            'step2': "Abone olun",
            'step3': "Abone olduktan sonra botu kullanın",
            'success': "✅ Tebrikler! Kanala abone oldunuz.",
            'welcome': "🤖 Bot'a hoş geldiniz!",
            'not_subscribed': "Hala abone değilsiniz",
            'check_button': "Aboneliği Kontrol Et 🔁",
            'already_subscribed': "✅ Zaten abonesiniz",
            'subscribe_button': "Kanal 📢",
            'subscribed_button': "Abone Oldum 🎯"
        }
    elif lang_code == 'en':
        return {
            'title': "🔒 You must subscribe to our channel to use the bot!",
            'channels_title': "Required Channel",
            'steps_title': "Steps",
            'step1': "Click on the channel",
            'step2': "Subscribe",
            'step3': "Use the bot after subscribing",
            'success': "✅ Congratulations! You subscribed to the channel.",
            'welcome': "🤖 Welcome to the bot!",
            'not_subscribed': "Still not subscribed",
            'check_button': "Check Subscription 🔁",
            'already_subscribed': "✅ Already subscribed",
            'subscribe_button': "Channel 📢",
            'subscribed_button': "Subscribed 🎯"
        }
    elif lang_code == 'ar':
        return {
            'title': "🔒 يجب أن تشترك في قناتنا لاستخدام البوت!",
            'channels_title': "القناة المطلوبة",
            'steps_title': "الخطوات",
            'step1': "انقر على القناة",
            'step2': "اشترك",
            'step3': "استخدم البوت بعد الاشتراك",
            'success': "✅ مبروك! لقد اشتركت في القناة.",
            'welcome': "🤖 مرحبًا بك في البوت!",
            'not_subscribed': "ما زلت غير مشترك",
            'check_button': "تحقق من الاشتراك 🔁",
            'already_subscribed': "✅ مشترك بالفعل",
            'subscribe_button': "القناة 📢",
            'subscribed_button': "اشتركت 🎯"
        }
    else:
        # Varsayılan Türkçe
        return get_subscription_text('tr')

def check_subscription(user_id):
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
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

def create_subscription_keyboard(lang_code, user_id=None):
    """Abonelik kontrol klavyesi oluştur - SADECE 2 BUTON"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    text = get_subscription_text(lang_code)
    
    # Kanal butonu (her zaman göster)
    markup.add(
        types.InlineKeyboardButton(
            text['subscribe_button'],
            url=REQUIRED_CHANNELS[0]['url']
        )
    )
    
    # Otomatik kontrol aktif - "Abone Oldum" butonu
    markup.add(
        types.InlineKeyboardButton(
            text['subscribed_button'],
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
        user_subscriptions[user_id] = True
        return True
    
    # Abone değil, mesaj göster
    text = get_subscription_text(lang_code)
    markup = create_subscription_keyboard(lang_code, user_id)
    
    message_text = f"""
{text['title']}

📌 **{text['channels_title']}:**
{REQUIRED_CHANNELS[0]['name']}

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
        'chat_id': chat_id,
        'lang_code': lang_code
    }
    
    # Otomatik kontrol için zamanı kaydet
    last_check_time[user_id] = time.time()
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
        cleanup_pending_message(user_id)
        
        # Başarı mesajı göster (geçici)
        success_msg = bot.send_message(
            chat_id,
            f"{text['success']}",
            parse_mode='Markdown'
        )
        
        # 1.5 saniye bekle ve sil
        time.sleep(1.5)
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
            f"❌ {text['not_subscribed']}",
            show_alert=True
        )

def is_user_subscribed(user_id):
    """Kullanıcı abone mi kontrol et"""
    # Önce cache'den kontrol et
    if user_id in user_subscriptions:
        if user_subscriptions[user_id]:
            return True
    
    # Cache'de yoksa veya False ise API'den kontrol et
    is_subscribed, _ = check_subscription(user_id)
    user_subscriptions[user_id] = is_subscribed
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
        if user_id in last_check_time:
            del last_check_time[user_id]

def auto_check_subscription():
    """Otomatik abonelik kontrolü (periyodik olarak çağrılacak)"""
    current_time = time.time()
    users_to_remove = []
    
    for user_id, check_data in list(pending_checks.items()):
        # Son kontrolden 10 saniye geçmiş mi?
        if user_id in last_check_time and current_time - last_check_time[user_id] >= 10:
            # Kontrol et
            is_subscribed, _ = check_subscription(user_id)
            
            if is_subscribed:
                # Otomatik olarak abone olmuş
                user_subscriptions[user_id] = True
                
                # Mesajı sil
                try:
                    bot.delete_message(check_data['chat_id'], check_data['message_id'])
                except:
                    pass
                
                # Başarı mesajı göster
                text = get_subscription_text(check_data['lang_code'])
                bot.send_message(
                    check_data['chat_id'],
                    f"✅ {text['success']}",
                    parse_mode='Markdown'
                )
                
                # Ana modüle sinyal gönder
                from main import on_subscription_complete_auto
                on_subscription_complete_auto(check_data['chat_id'], user_id, check_data['lang_code'])
                
                users_to_remove.append(user_id)
            
            # Son kontrol zamanını güncelle
            last_check_time[user_id] = current_time
    
    # Temizle
    for user_id in users_to_remove:
        cleanup_pending_message(user_id)
