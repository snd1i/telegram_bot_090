# extensions/admin.py - GÜNCELLENMİŞ VERSİYON
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import json
import os
from io import BytesIO

# ========== DOSYA İŞLEMLERİ ==========
def load_config():
    """Config dosyasını yükle"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"admin_id": "5541236874"}

def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def get_user_lang(user_id):
    """Kullanıcının dilini al"""
    user_data = load_user_data()
    return user_data.get(str(user_id), {}).get('lang', 'en')

def is_admin(user_id):
    """Admin kontrolü"""
    config = load_config()
    return str(user_id) == config.get('admin_id', "5541236874")

def save_broadcast_data(data):
    """Duyuru verilerini kaydet"""
    with open('broadcast_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_broadcast_data():
    """Duyuru verilerini yükle"""
    try:
        with open('broadcast_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"broadcasts": []}

# ========== DİL MESAJLARI ==========
ADMIN_TEXTS = {
    'ku': {
        'admin_only': "❌ تەنیا بەڕێوەبەر دەتوانێت ئەم فرمانە بەکاربهێنێت!",
        'panel_title': "👑 **پانێلی بەڕێوەبەری**\n\nخوارەوە دوگمەیەک هەڵبژێرە:",
        'broadcast_title': "📢 **ناردنی بڵاوکراوە**\n\nناردنی بڵاوکراوە\n\nتکایە پەیامێک بنێرە یان وێنە یان ڤیدیۆ:\n• دەتوانیت دەق بنووسیت\n• دەتوانیت وێنە یان ڤیدیۆ باربکەیت\n• دەتوانیت دوگمە زیاد بکەیت\n\nدوای ئەوەی هەموو شتێکت زیاد کرد، دوگمەی 'ناردن' بکلیک بکە.",
        'edit_help': "🔄 **دەستکاری پەیامی یارمەتی**\n\nئەم تایبەتمەندیە لە پەرەپێداندایە.\nبەم زووانە بەردەست دەبێت.",
        'app_settings': "📱 **ڕێکخستنەکانی ئەپ**\n\nتایبەتمەندیەکانی ئەپ بەم زووانە زیاد دەکرێن.",
        'stats_title': "📊 **ئامارەکانی بۆت**",
        'bot_settings': "⚙️ **ڕێکخستنەکانی بۆت**",
        'total_users': "👥 کۆی بەکارهێنەران:",
        'lang_dist': "🌍 **دابەشکاری زمان:**",
        'channel': "📢 کەناڵ:",
        'invite_link': "🔗 پەیوەندی بانگهێشتکردن:",
        'required_sub': "📌 ئەندامێتی ناچاری:",
        'on': "✅ چالاکە",
        'off': "❌ ناچالاکە",
        'back': "🔙 گەڕانەوە",
        'send_broadcast': "📤 ناردنی بڵاوکراوە",
        'add_button': "➕ زیادکردنی دوگمە",
        'cancel': "✖️ پاشگەزبوونەوە",
        'broadcast_sent': "✅ بڵاوکراوە نێردرا بۆ {} کەس!",
        'enter_button_text': "📝 دەقی دوگمە بنووسە:",
        'enter_button_url': "🔗 لینکی دوگمە بنووسە:",
        'button_added': "✅ دوگمە زیاد کرا!",
        'no_content': "⚠️ هیچ ناوەڕۆکێک نییە بۆ ناردن!",
        'broadcast_preview': "👁️ **پێشبینینی بڵاوکراوە**\n\n{}"
    },
    'en': {
        'admin_only': "❌ Only admin can use this command!",
        'panel_title': "👑 **Admin Panel**\n\nSelect a button below:",
        'broadcast_title': "📢 **Send Broadcast**\n\nBroadcast Sending\n\nPlease send a message, photo or video:\n• You can write text\n• You can upload photo or video\n• You can add buttons\n\nAfter adding everything, click the 'Send' button.",
        'edit_help': "🔄 **Edit Help Message**\n\nThis feature is under development.\nWill be available soon.",
        'app_settings': "📱 **App Settings**\n\nApp features will be added soon.",
        'stats_title': "📊 **Bot Statistics**",
        'bot_settings': "⚙️ **Bot Settings**",
        'total_users': "👥 Total Users:",
        'lang_dist': "🌍 **Language Distribution:**",
        'channel': "📢 Channel:",
        'invite_link': "🔗 Invite Link:",
        'required_sub': "📌 Required Subscription:",
        'on': "✅ ON",
        'off': "❌ OFF",
        'back': "🔙 Back",
        'send_broadcast': "📤 Send Broadcast",
        'add_button': "➕ Add Button",
        'cancel': "✖️ Cancel",
        'broadcast_sent': "✅ Broadcast sent to {} people!",
        'enter_button_text': "📝 Enter button text:",
        'enter_button_url': "🔗 Enter button URL:",
        'button_added': "✅ Button added!",
        'no_content': "⚠️ No content to send!",
        'broadcast_preview': "👁️ **Broadcast Preview**\n\n{}"
    },
    'ar': {
        'admin_only': "❌ فقط المدير يمكنه استخدام هذا الأمر!",
        'panel_title': "👑 **لوحة المدير**\n\nاختر زرًا أدناه:",
        'broadcast_title': "📢 **إرسال بث**\n\nإرسال البث\n\nالرجاء إرسال رسالة أو صورة أو فيديو:\n• يمكنك كتابة نص\n• يمكنك تحميل صورة أو فيديو\n• يمكنك إضافة أزرار\n\nبعد إضافة كل شيء، انقر على زر 'إرسال'.",
        'edit_help': "🔄 **تحرير رسالة المساعدة**\n\nهذه الميزة قيد التطوير.\nستكون متاحة قريبًا.",
        'app_settings': "📱 **إعدادات التطبيق**\n\nستتم إضافة ميزات التطبيق قريبًا.",
        'stats_title': "📊 **إحصائيات البوت**",
        'bot_settings': "⚙️ **إعدادات البوت**",
        'total_users': "👥 إجمالي المستخدمين:",
        'lang_dist': "🌍 **توزيع اللغة:**",
        'channel': "📢 القناة:",
        'invite_link': "🔗 رابط الدعوة:",
        'required_sub': "📌 الاشتراك المطلوب:",
        'on': "✅ مفعل",
        'off': "❌ معطل",
        'back': "🔙 رجوع",
        'send_broadcast': "📤 إرسال البث",
        'add_button': "➕ إضافة زر",
        'cancel': "✖️ إلغاء",
        'broadcast_sent': "✅ تم إرسال البث إلى {} شخص!",
        'enter_button_text': "📝 أدخل نص الزر:",
        'enter_button_url': "🔗 أدخل رابط الزر:",
        'button_added': "✅ تمت إضافة الزر!",
        'no_content': "⚠️ لا يوجد محتوى للإرسال!",
        'broadcast_preview': "👁️ **معاينة البث**\n\n{}"
    }
}

BUTTON_TEXTS = {
    'ku': {
        'broadcast': "📝 ناردنی بڵاوکراوە",
        'edit_help': "🔄 دەستکاری پەیامی یارمەتی",
        'app_settings': "📱 ڕێکخستنەکانی ئەپ",
        'stats': "📊 ئامارەکان",
        'bot_settings': "⚙️ ڕێکخستنەکانی بۆت",
    },
    'en': {
        'broadcast': "📝 Send Broadcast",
        'edit_help': "🔄 Edit Help Message",
        'app_settings': "📱 App Settings",
        'stats': "📊 Statistics",
        'bot_settings': "⚙️ Bot Settings",
    },
    'ar': {
        'broadcast': "📝 إرسال بث",
        'edit_help': "🔄 تحرير رسالة المساعدة",
        'app_settings': "📱 إعدادات التطبيق",
        'stats': "📊 الإحصائيات",
        'bot_settings': "⚙️ إعدادات البوت",
    }
}

LANG_NAMES = {
    'ku': {'ku': 'کوردی', 'en': 'ئینگلیزی', 'ar': 'عەرەبی'},
    'en': {'ku': 'Kurdish', 'en': 'English', 'ar': 'Arabic'},
    'ar': {'ku': 'الكردية', 'en': 'الإنجليزية', 'ar': 'العربية'}
}

# Duyuru verilerini saklamak için global değişken
user_broadcast_data = {}

# ========== /settings KOMUTU ==========
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dil destekli admin paneli"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        user_lang = get_user_lang(user_id)
        await update.message.reply_text(ADMIN_TEXTS[user_lang]['admin_only'])
        return
    
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    buttons = BUTTON_TEXTS[user_lang]
    
    # Admin paneli butonları
    keyboard = [
        [InlineKeyboardButton(buttons['broadcast'], callback_data="admin_broadcast")],
        [InlineKeyboardButton(buttons['edit_help'], callback_data="admin_edit_help")],
        [InlineKeyboardButton(buttons['app_settings'], callback_data="admin_app_settings")],
        [InlineKeyboardButton(buttons['stats'], callback_data="admin_stats")],
        [InlineKeyboardButton(buttons['bot_settings'], callback_data="admin_bot_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(texts['panel_title'], reply_markup=reply_markup, parse_mode='Markdown')

# ========== DÜYURU SİSTEMİ ==========
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru oluşturmaya başla"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    
    # Kullanıcının duyuru verilerini sıfırla
    user_broadcast_data[user_id] = {
        'text': None,
        'photo': None,
        'video': None,
        'buttons': [],
        'state': 'waiting_content'
    }
    
    keyboard = [
        [InlineKeyboardButton(texts['cancel'], callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(texts['broadcast_title'], reply_markup=reply_markup, parse_mode='Markdown')

async def handle_broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuru içeriğini işle"""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_broadcast_data:
        return
    
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    
    # Mesaj tipine göre işle
    if update.message.text:
        # Metin mesajı
        user_broadcast_data[user_id]['text'] = update.message.text
        await update.message.reply_text(f"✅ {texts['button_added']}\n\n{texts['add_button']} / {texts['send_broadcast']}")
        
    elif update.message.photo:
        # Fotoğraf
        photo = update.message.photo[-1]  # En yüksek çözünürlüklü
        user_broadcast_data[user_id]['photo'] = photo.file_id
        caption = update.message.caption or ""
        user_broadcast_data[user_id]['text'] = caption
        await update.message.reply_text(f"✅ {texts['button_added']}\n\n{texts['add_button']} / {texts['send_broadcast']}")
        
    elif update.message.video:
        # Video
        video = update.message.video
        user_broadcast_data[user_id]['video'] = video.file_id
        caption = update.message.caption or ""
        user_broadcast_data[user_id]['text'] = caption
        await update.message.reply_text(f"✅ {texts['button_added']}\n\n{texts['add_button']} / {texts['send_broadcast']}")
    
    # Buton ekleme veya gönderme seçenekleri
    keyboard = [
        [
            InlineKeyboardButton(texts['add_button'], callback_data="broadcast_add_button"),
            InlineKeyboardButton(texts['send_broadcast'], callback_data="broadcast_send")
        ],
        [InlineKeyboardButton(texts['cancel'], callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(texts['broadcast_preview'].format(
        user_broadcast_data[user_id]['text'] or texts['no_content']
    ), reply_markup=reply_markup, parse_mode='Markdown')

async def add_broadcast_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuruya buton ekle"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    
    # Buton ekleme durumuna geç
    user_broadcast_data[user_id]['state'] = 'waiting_button_text'
    
    await query.message.reply_text(texts['enter_button_text'])

async def handle_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton metnini al"""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_broadcast_data or user_broadcast_data[user_id]['state'] != 'waiting_button_text':
        return
    
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    
    button_text = update.message.text
    user_broadcast_data[user_id]['button_temp'] = {'text': button_text}
    user_broadcast_data[user_id]['state'] = 'waiting_button_url'
    
    await update.message.reply_text(texts['enter_button_url'])

async def handle_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton URL'sini al"""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_broadcast_data or user_broadcast_data[user_id]['state'] != 'waiting_button_url':
        return
    
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    
    button_url = update.message.text
    button_text = user_broadcast_data[user_id]['button_temp']['text']
    
    # Butonu ekle
    user_broadcast_data[user_id]['buttons'].append({
        'text': button_text,
        'url': button_url
    })
    
    # Geçici veriyi temizle
    del user_broadcast_data[user_id]['button_temp']
    user_broadcast_data[user_id]['state'] = 'waiting_content'
    
    await update.message.reply_text(texts['button_added'])

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Duyuruyu gönder"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    if user_id not in user_broadcast_data:
        await query.message.reply_text("❌ No broadcast data found!")
        return
    
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    
    data = user_broadcast_data[user_id]
    
    if not data['text'] and not data['photo'] and not data['video']:
        await query.message.reply_text(texts['no_content'])
        return
    
    # Tüm kullanıcıları al
    user_data = load_user_data()
    user_ids = list(user_data.keys())
    
    # Butonları oluştur
    keyboard = []
    for btn in data['buttons']:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Gönderim sayacı
    sent_count = 0
    
    # Her kullanıcıya gönder
    for uid in user_ids:
        try:
            if data['photo']:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=data['photo'],
                    caption=data['text'] or "",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            elif data['video']:
                await context.bot.send_video(
                    chat_id=uid,
                    video=data['video'],
                    caption=data['text'] or "",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=uid,
                    text=data['text'],
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send to {uid}: {e}")
            continue
    
    # Veriyi temizle
    del user_broadcast_data[user_id]
    
    await query.message.reply_text(texts['broadcast_sent'].format(sent_count))

# ========== BUTON İŞLEMLERİ ==========
async def admin_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin butonlarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    buttons = BUTTON_TEXTS[user_lang]
    
    if not is_admin(user_id):
        await query.edit_message_text(texts['admin_only'])
        return
    
    if query.data == "admin_broadcast":
        # Duyuru gönderim paneli
        await start_broadcast(update, context)
    
    elif query.data == "admin_edit_help":
        # Help mesajını düzenle
        await query.edit_message_text(texts['edit_help'])
    
    elif query.data == "admin_app_settings":
        # App ayarları
        await query.edit_message_text(texts['app_settings'])
    
    elif query.data == "admin_stats":
        # İstatistikler
        try:
            user_data = load_user_data()
            total_users = len(user_data)
            
            # Dil dağılımı
            lang_dist = {}
            for user_info in user_data.values():
                lang = user_info.get('lang', 'unknown')
                lang_dist[lang] = lang_dist.get(lang, 0) + 1
            
            stats_text = f"{texts['stats_title']}\n\n"
            stats_text += f"{texts['total_users']} {total_users}\n\n"
            stats_text += f"{texts['lang_dist']}\n"
            
            for lang, count in lang_dist.items():
                percentage = (count / total_users * 100) if total_users > 0 else 0
                lang_name = LANG_NAMES[user_lang].get(lang, lang)
                stats_text += f"• {lang_name}: {count} ({percentage:.1f}%)\n"
            
            # Geri butonu
            keyboard = [[InlineKeyboardButton(texts['back'], callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await query.edit_message_text(f"❌ Error getting stats: {str(e)}")
    
    elif query.data == "admin_bot_settings":
        # Bot ayarları
        config = load_config()
        
        settings_text = f"{texts['bot_settings']}\n\n"
        settings_text += f"👑 Admin ID: {config.get('admin_id', 'Not specified')}\n"
        settings_text += f"{texts['channel']} {config.get('channel_username', 'Not set')}\n"
        settings_text += f"{texts['invite_link']} {config.get('channel_invite_link', 'Not set')}\n"
        settings_text += f"{texts['required_sub']} {texts['on'] if config.get('required_channel') else texts['off']}\n\n"
        settings_text += "Use /join command to change bot settings."
        
        keyboard = [[InlineKeyboardButton(texts['back'], callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(settings_text, reply_markup=reply_markup)
    
    elif query.data == "admin_back":
        # Ana panele dön
        buttons = BUTTON_TEXTS[user_lang]
        keyboard = [
            [InlineKeyboardButton(buttons['broadcast'], callback_data="admin_broadcast")],
            [InlineKeyboardButton(buttons['edit_help'], callback_data="admin_edit_help")],
            [InlineKeyboardButton(buttons['app_settings'], callback_data="admin_app_settings")],
            [InlineKeyboardButton(buttons['stats'], callback_data="admin_stats")],
            [InlineKeyboardButton(buttons['bot_settings'], callback_data="admin_bot_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(texts['panel_title'], reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == "broadcast_add_button":
        # Buton ekle
        await add_broadcast_button(update, context)
    
    elif query.data == "broadcast_send":
        # Duyuruyu gönder
        await send_broadcast(update, context)

# ========== KURULUM ==========
def setup(app):
    """Admin komutlarını bot'a ekler"""
    # Komutlar
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Buton işleyicileri
    app.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^broadcast_"))
    
    # Duyuru içeriği işleyicileri
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_broadcast_content
    ))
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE,
        handle_broadcast_content
    ))
    app.add_handler(MessageHandler(
        filters.VIDEO & filters.ChatType.PRIVATE,
        handle_broadcast_content
    ))
    
    # Buton metin ve URL işleyicileri
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_button_text
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_button_url
    ))
    
    print("✅ Admin extension loaded: /settings (multi-language, enhanced broadcast)")
