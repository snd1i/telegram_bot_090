# extensions/admin.py - DİL DESTEKLİ ADMIN PANELİ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
import json
import os

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

# ========== DİL MESAJLARI ==========
ADMIN_TEXTS = {
    'ku': {
        'admin_only': "❌ تەنیا بەڕێوەبەر دەتوانێت ئەم فرمانە بەکاربهێنێت!",
        'panel_title': "👑 **پانێلی بەڕێوەبەری**\n\nخوارەوە دوگمەیەک هەڵبژێرە:",
        'broadcast_title': "📢 **ناردنی بڵاوکراوە**\n\nجۆری بڵاوکراوە هەڵبژێرە:",
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
        'text_broadcast': "📝 بڵاوکراوەی دەق",
        'photo_broadcast': "🖼️ بڵاوکراوەی وێنە",
        'video_broadcast': "🎬 بڵاوکراوەی ڤیدیۆ",
        'broadcast_feature': "📢 **ناردنی بڵاوکراوە**\n\nئەم تایبەتمەندیە لە پەرەپێداندایە.\nجۆری هەڵبژێردراو: {}\n\nکاتێک تەواو بوو:\n1. دەتوانیت ناوەڕۆکی بڵاوکراوە بنووسیت\n2. دەتوانیت دوگمە زیاد بکەیت\n3. دەتوانیت بزانیت چەند کەس گەیشتەت"
    },
    'en': {
        'admin_only': "❌ Only admin can use this command!",
        'panel_title': "👑 **Admin Panel**\n\nSelect a button below:",
        'broadcast_title': "📢 **Send Broadcast**\n\nSelect broadcast type:",
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
        'text_broadcast': "📝 Text Broadcast",
        'photo_broadcast': "🖼️ Photo Broadcast",
        'video_broadcast': "🎬 Video Broadcast",
        'broadcast_feature': "📢 **Broadcast Sending**\n\nThis feature is under development.\nSelected type: {}\n\nWhen completed:\n1. You can enter broadcast content\n2. You can add buttons\n3. You can see how many people received it"
    },
    'ar': {
        'admin_only': "❌ فقط المدير يمكنه استخدام هذا الأمر!",
        'panel_title': "👑 **لوحة المدير**\n\nاختر زرًا أدناه:",
        'broadcast_title': "📢 **إرسال بث**\n\nاختر نوع البث:",
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
        'text_broadcast': "📝 بث نصي",
        'photo_broadcast': "🖼️ بث صورة",
        'video_broadcast': "🎬 بث فيديو",
        'broadcast_feature': "📢 **إرسال البث**\n\nهذه الميزة قيد التطوير.\nالنوع المحدد: {}\n\nعند الانتهاء:\n1. يمكنك إدخال محتوى البث\n2. يمكنك إضافة أزرار\n3. يمكنك معرفة عدد الأشخاص الذين تلقوه"
    }
}

BUTTON_TEXTS = {
    'ku': {
        'broadcast': "📝 ناردنی بڵاوکراوە",
        'edit_help': "🔄 دەستکاری پەیامی یارمەتی",
        'app_settings': "📱 ڕێکخستنەکانی ئەپ",
        'stats': "📊 ئامارەکان",
        'bot_settings': "⚙️ ڕێکخستنەکانی بۆت",
        'text': "📝 بڵاوکراوەی دەق",
        'photo': "🖼️ بڵاوکراوەی وێنە",
        'video': "🎬 بڵاوکراوەی ڤیدیۆ"
    },
    'en': {
        'broadcast': "📝 Send Broadcast",
        'edit_help': "🔄 Edit Help Message",
        'app_settings': "📱 App Settings",
        'stats': "📊 Statistics",
        'bot_settings': "⚙️ Bot Settings",
        'text': "📝 Text Broadcast",
        'photo': "🖼️ Photo Broadcast",
        'video': "🎬 Video Broadcast"
    },
    'ar': {
        'broadcast': "📝 إرسال بث",
        'edit_help': "🔄 تحرير رسالة المساعدة",
        'app_settings': "📱 إعدادات التطبيق",
        'stats': "📊 الإحصائيات",
        'bot_settings': "⚙️ إعدادات البوت",
        'text': "📝 بث نصي",
        'photo': "🖼️ بث صورة",
        'video': "🎬 بث فيديو"
    }
}

LANG_NAMES = {
    'ku': {'ku': 'کوردی', 'en': 'ئینگلیزی', 'ar': 'عەرەبی'},
    'en': {'ku': 'Kurdish', 'en': 'English', 'ar': 'Arabic'},
    'ar': {'ku': 'الكردية', 'en': 'الإنجليزية', 'ar': 'العربية'}
}

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
    
    await update.message.reply_text(texts['panel_title'], reply_markup=reply_markup)

# ========== BUTON İŞLEMLERİ ==========
async def admin_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin butonlarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = ADMIN_TEXTS[user_lang]
    buttons = BUTON_TEXTS[user_lang]
    
    if not is_admin(user_id):
        await query.edit_message_text(texts['admin_only'])
        return
    
    if query.data == "admin_broadcast":
        # Duyuru gönderim paneli
        keyboard = [
            [InlineKeyboardButton(buttons['text'], callback_data="broadcast_text")],
            [InlineKeyboardButton(buttons['photo'], callback_data="broadcast_photo")],
            [InlineKeyboardButton(buttons['video'], callback_data="broadcast_video")],
            [InlineKeyboardButton(texts['back'], callback_data="admin_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(texts['broadcast_title'], reply_markup=reply_markup)
    
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
            
            await query.edit_message_text(stats_text, reply_markup=reply_markup)
            
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
        
        await query.edit_message_text(texts['panel_title'], reply_markup=reply_markup)
    
    elif query.data.startswith("broadcast_"):
        # Duyuru türü seçildi
        broadcast_type = query.data.replace("broadcast_", "")
        type_names = {
            'text': texts['text_broadcast'],
            'photo': texts['photo_broadcast'], 
            'video': texts['video_broadcast']
        }
        
        await query.edit_message_text(
            texts['broadcast_feature'].format(type_names.get(broadcast_type, 'Unknown'))
        )

# ========== KURULUM ==========
def setup(app):
    """Admin komutlarını bot'a ekler"""
    # Komutlar
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Buton işleyicileri
    app.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^broadcast_"))
    
    print("✅ Admin extension loaded: /settings (multi-language)")
