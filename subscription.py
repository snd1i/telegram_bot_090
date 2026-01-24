import telebot
from telebot import types
import diller
import time
import threading

# Telegram bot instance'ı
bot = None

# Zorunlu kanal
REQUIRED_CHANNEL = {
    'name': 'SNDI Kanal 📢',
    'url': 'https://t.me/sndiyi',
    'username': 'sndiyi'
}

# Abonelik durumu
user_subscriptions = {}  # {user_id: {'subscribed': True/False, 'last_check': timestamp}}
pending_checks = {}  # Bekleyen kontroller
active_users = set()  # Aktif kullanıcılar (botu kullanan)

def init_bot(bot_instance):
    """Bot instance'ını başlat"""
    global bot
    bot = bot_instance

def get_subscription_text(lang_code):
    """Dile göre abonelik mesajı al"""
    if lang_code == 'ku_badini':
        return {
            'title': "🔒 پێدفیە کەنالێ مە جوین بکی دا بشێی بوتی بکار بینی",
            'steps_title': "ختوە",
            'step1': "تلا خول کەنالی بدە",
            'step2': "جوین بکە", 
            'step3': "پشتی جوین دکی بوتی بەکار ینی",
            'success': "✅ دەستخوش جویناتە هاتە وەلگرتن!",
            'welcome': "🤖 خێرهاتی بو نافا بوتی!",
            'not_subscribed': "هێشتا تە کەنال جوین نەکرە",
            'check_button': "من جوین کر 🔁",
            'unsubscribed': "❌ تە کەنال بەجێهێشتە، دیسان جوین بکە!",
            'subscribe_button': "کەنال 📢",
            'subscribed_button': "جوین کر 🎯"
        }
    elif lang_code == 'ku_sorani':
        return {
            'title': "🔒 پێویستە بەشداربیت لە کەناڵەکەمان بۆ بەکارهێنانی بۆت!",
            'steps_title': "هەنگاوەکان",
            'step1': "کرتە لەسەر کەناڵەکە بکە",
            'step2': "بەشداربە",
            'step3': "دوای بەشداربوون بۆت بەکاربهێنە",
            'success': "✅ پیرۆز بێت! بەشداربوویت.",
            'welcome': "🤖 بەخێربێیت بۆ بۆت!",
            'not_subscribed': "هێشتا بەشدارنەبوویت",
            'check_button': "پشکنینی بەشداربوون 🔁",
            'unsubscribed': "❌ کەناڵەکەت بەجێهێشتووە، دیسان بەشداربە!",
            'subscribe_button': "کەناڵ 📢",
            'subscribed_button': "بەشداربوو 🎯"
        }
    elif lang_code == 'tr':
        return {
            'title': "🔒 Botu kullanmak için kanalımıza abone olmalısınız!",
            'steps_title': "Adımlar",
            'step1': "Kanala tıklayın",
            'step2': "Abone olun",
            'step3': "Abone olduktan sonra botu kullanın",
            'success': "✅ Tebrikler! Kanala abone oldunuz.",
            'welcome': "🤖 Bot'a hoş geldiniz!",
            'not_subscribed': "Hala abone değilsiniz",
            'check_button': "Aboneliği Kontrol Et 🔁",
            'unsubscribed': "❌ Kanaldan ayrılmışsınız, tekrar abone olun!",
            'subscribe_button': "Kanal 📢",
            'subscribed_button': "Abone Oldum 🎯"
        }
    elif lang_code == 'en':
        return {
            'title': "🔒 You must subscribe to our channel to use the bot!",
            'steps_title': "Steps",
            'step1': "Click on the channel",
            'step2': "Subscribe",
            'step3': "Use the bot after subscribing",
            'success': "✅ Congratulations! You subscribed to the channel.",
            'welcome': "🤖 Welcome to the bot!",
            'not_subscribed': "Still not subscribed",
            'check_button': "Check Subscription 🔁",
            'unsubscribed': "❌ You left the channel, subscribe again!",
            'subscribe_button': "Channel 📢",
            'subscribed_button': "Subscribed 🎯"
        }
    elif lang_code == 'ar':
        return {
            'title': "🔒 يجب أن تشترك في قناتنا لاستخدام البوت!",
            'steps_title': "الخطوات",
            'step1': "انقر على القناة",
            'step2': "اشترك",
            'step3': "استخدم البوت بعد الاشتراك",
            'success': "✅ مبروك! لقد اشتركت في القناة.",
            'welcome': "🤖 مرحبًا بك في البوت!",
            'not_subscribed': "ما زلت غير مشترك",
            'check_button': "تحقق من الاشتراك 🔁",
            'unsubscribed': "❌ غادرت القناة، اشترك مرة أخرى!",
            'subscribe_button': "القناة 📢",
            'subscribed_button': "اشتركت 🎯"
        }
    else:
        # Varsayılan Türkçe
        return get_subscription_text('tr')

def check_subscription_real_time(user_id):
    """Gerçek zamanlı abonelik kontrolü (API çağrısı)"""
    try:
        member = bot.get_chat_member(f'@{REQUIRED_CHANNEL["username"]}', user_id)
        is_subscribed = member.status in ['member', 'administrator', 'creator']
        return is_subscribed
    except Exception as e:
        print(f"Gerçek zamanlı abonelik kontrol hatası: {e}")
        return False

def check_subscription(user_id, force_check=False):
    """Kullanıcının kanala abone olup olmadığını kontrol et"""
    current_time = time.time()
    
    # Cache'den kontrol et (5 dakika öncesine kadar geçerli)
    if user_id in user_subscriptions and not force_check:
        user_data = user_subscriptions[user_id]
        # 5 dakikadan eski değilse cache kullan
        if current_time - user_data['last_check'] < 300:  # 5 dakika
            return user_data['subscribed'], REQUIRED_CHANNEL
    
    # Gerçek zamanlı kontrol
    is_subscribed = check_subscription_real_time(user_id)
    
    # Cache'i güncelle
    user_subscriptions[user_id] = {
        'subscribed': is_subscribed,
        'last_check': current_time
    }
    
    return is_subscribed, REQUIRED_CHANNEL

def create_subscription_keyboard(lang_code):
    """Abonelik kontrol klavyesi oluştur - SADECE 2 BUTON"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    text = get_subscription_text(lang_code)
    
    # Kanal butonu
    markup.add(
        types.InlineKeyboardButton(
            text['subscribe_button'],
            url=REQUIRED_CHANNEL['url']
        )
    )
    
    # Abone Oldum butonu
    markup.add(
        types.InlineKeyboardButton(
            text['subscribed_button'],
            callback_data='check_subscription'
        )
    )
    
    return markup

def show_subscription_required(chat_id, user_id, lang_code='tr'):
    """Abonelik gerekli mesajını göster"""
    # Gerçek zamanlı kontrol (cache bypass)
    is_subscribed = check_subscription_real_time(user_id)
    
    if is_subscribed:
        # Zaten abone, cache'i güncelle
        user_subscriptions[user_id] = {
            'subscribed': True,
            'last_check': time.time()
        }
        return True
    
    # Abone değil, mesaj göster
    text = get_subscription_text(lang_code)
    markup = create_subscription_keyboard(lang_code)
    
    # SADELEŞTİRİLMİŞ MESAJ (kanal listesi yok)
    message_text = f"""
{text['title']}

⚠️ **{text['steps_title']}:**
• {text['step1']}
• {text['step2']}
• {text['step3']}
"""
    
    # Mesajı gönder
    msg = bot.send_message(
        chat_id,
        message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    # Bekleyen kontrollere ekle
    pending_checks[user_id] = {
        'message_id': msg.message_id,
        'chat_id': chat_id,
        'lang_code': lang_code,
        'shown_at': time.time()
    }
    
    # Aktif kullanıcılara ekle (kanaldan ayrılma kontrolü için)
    active_users.add(user_id)
    
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
    
    # GERÇEK ZAMANLI kontrol
    is_subscribed = check_subscription_real_time(user_id)
    
    if is_subscribed:
        # Abone olmuş
        user_subscriptions[user_id] = {
            'subscribed': True,
            'last_check': time.time()
        }
        
        # Eski abonelik mesajını sil
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        
        # Bekleyen mesajı temizle
        cleanup_pending_message(user_id)
        
        # Aktif kullanıcılara ekle
        active_users.add(user_id)
        
        # BUTONLU abonelik başarı mesajını göster
        markup = types.InlineKeyboardMarkup()
        prompts_button = types.InlineKeyboardButton(
            lang_data.get('prompts_button', '🎉 prompts 🎉'),
            url='https://t.me/PrompttAI_bot/Prompts'
        )
        markup.add(prompts_button)
        
        # Özel abonelik başarı mesajını gönder (KALICI - SİLİNMEYECEK)
        bot.send_message(
            chat_id,
            f"✅ {text['success']}\n\n"
            f"{lang_data.get('subscription_success_message', 'subscribed to channel 🎉')}",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        # HEMEN hoşgeldin mesajını göster
        from main import show_welcome_message
        show_welcome_message(call.message, lang_code)
        
    else:
        # Hala abone değil
        bot.answer_callback_query(
            call.id,
            f"❌ {text['not_subscribed']}",
            show_alert=True
        )

def is_user_subscribed(user_id, force_check=False):
    """Kullanıcı abone mi kontrol et"""
    # GERÇEK ZAMANLI kontrol (force_check True ise)
    if force_check:
        is_subscribed = check_subscription_real_time(user_id)
        user_subscriptions[user_id] = {
            'subscribed': is_subscribed,
            'last_check': time.time()
        }
        return is_subscribed
    
    # Normal cache kontrolü
    is_subscribed, _ = check_subscription(user_id, force_check)
    return is_subscribed

def cleanup_pending_message(user_id):
    """Bekleyen mesajı temizle"""
    if user_id in pending_checks:
        try:
            data = pending_checks[user_id]
            bot.delete_message(data['chat_id'], data['message_id'])
        except:
            pass
        del pending_checks[user_id]

def check_unsubscribed_users():
    """Kanaldan ayrılan kullanıcıları kontrol et"""
    users_to_check = list(active_users.copy())
    
    for user_id in users_to_check:
        try:
            # Sadece son 10 dakika içinde aktif olanları kontrol et
            if user_id in user_subscriptions:
                user_data = user_subscriptions[user_id]
                # 10 dakikadan eski kayıtları kontrol et
                if time.time() - user_data['last_check'] > 600:
                    continue
            
            # Gerçek zamanlı kontrol
            is_subscribed = check_subscription_real_time(user_id)
            
            if not is_subscribed:
                # Kanaldan ayrılmış
                print(f"⚠️ Kullanıcı kanaldan ayrıldı: {user_id}")
                
                # Cache'i güncelle
                user_subscriptions[user_id] = {
                    'subscribed': False,
                    'last_check': time.time()
                }
                
                # Eski mesajları temizle
                cleanup_pending_message(user_id)
                
                # Yeni abonelik mesajı gönder (eğer hala aktifse)
                from main import get_user_chat_id
                chat_id = get_user_chat_id(user_id)
                if chat_id:
                    lang_data = diller.get_language_data(user_id)
                    lang_code = lang_data['code'] if lang_data else 'tr'
                    
                    text = get_subscription_text(lang_code)
                    markup = create_subscription_keyboard(lang_code)
                    
                    message_text = f"""
{text['unsubscribed']}

{text['title']}

⚠️ **{text['steps_title']}:**
• {text['step1']}
• {text['step2']}
• {text['step3']}
"""
                    
                    bot.send_message(
                        chat_id,
                        message_text,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                    
        except Exception as e:
            print(f"Kanaldan ayrılma kontrol hatası {user_id}: {e}")

def start_unsubscribe_checker():
    """Kanaldan ayrılma kontrolünü başlat"""
    def checker():
        while True:
            try:
                check_unsubscribed_users()
            except Exception as e:
                print(f"Kanaldan ayrılma kontrol hatası: {e}")
            time.sleep(60)  # Her 1 dakikada bir kontrol et
    
    thread = threading.Thread(target=checker, daemon=True)
    thread.start()
    print("✅ Kanaldan ayrılma kontrolü başlatıldı")

def add_active_user(user_id):
    """Aktif kullanıcı ekle"""
    active_users.add(user_id)
