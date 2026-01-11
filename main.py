import logging
import json
import sqlite3
import os
import re
from datetime import datetime, date
from typing import Dict, Optional, Tuple, List
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand, BotCommandScopeChat, InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode
import asyncio

# 1) LOGLAMA AYARI
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2) TOKEN'ı Railway Environment Variable'dan al
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable bulunamadı!")
    logger.error("Lütfen Railway dashboard'da Variables sekmesine BOT_TOKEN ekleyin")
    raise ValueError("BOT_TOKEN environment variable ayarlanmamış")

# 3) DİĞER AYARLAR
ADMIN_ID = 5541236874
CHANNEL_ID = -1002072605977
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"
PROMPT_LINK = "https://t.me/PrompttAI_bot/Prompts"

# 4) VERİTABANI BAĞLANTISI
DB_NAME = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, lang TEXT, joined_date DATE, banned INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (key TEXT PRIMARY KEY, tr TEXT, en TEXT, ku TEXT, ar TEXT)''')
    conn.commit()
    
    default_messages = {
        'welcome': {
            'tr': '🤖 **Hoş geldin!**\n\nAşağıdaki seçenekleri kullanabilirsin:',
            'en': '🤖 **Welcome!**\n\nYou can use the options below:',
            'ku': '🤖 **بەخێربێیت!**\n\nدەتوانیت ئەم هەڵبژاردانەی خوارەوە بەکاربهێنیت:',
            'ar': '🤖 **أهلاً بك!**\n\nيمكنك استخدام الخيارات أدناه:'
        }
    }
    
    for key, texts in default_messages.items():
        c.execute("SELECT key FROM messages WHERE key=?", (key,))
        if not c.fetchone():
            c.execute("INSERT INTO messages (key, tr, en, ku, ar) VALUES (?, ?, ?, ?, ?)",
                     (key, texts['tr'], texts['en'], texts['ku'], texts['ar']))
    
    conn.commit()
    conn.close()

init_db()

# 5) DİL SİSTEMİ
LANGUAGES = {
    'tr': {'flag': '🇹🇷', 'name': 'Türkçe'},
    'en': {'flag': '🇬🇧', 'name': 'English'},
    'ku': {'flag': '🇹🇯', 'name': 'کوردی سۆرانی'},
    'ar': {'flag': '🇸🇦', 'name': 'العربية'}
}

def get_user_lang(user_id: int) -> str:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'en'

def get_message(key: str, lang: str) -> str:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(f"SELECT {lang} FROM messages WHERE key=?", (key,))
        result = c.fetchone()
        return result[0] if result else f"[{key}]"
    except:
        return f"[{key}]"
    finally:
        conn.close()

# 6) ZORUNLU KANAL KONTROLÜ
async def check_subscription(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Kanal kontrol hatası: {e}")
        return True

# 7) DİL SEÇİMİ EKRANI
async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, is_change=False):
    user = update.effective_user
    
    # Kullanıcı zaten kayıtlıysa doğrudan hoşgeldin menüsüne yönlendir
    if not is_change:
        user_lang = get_user_lang(user.id)
        if user_lang != 'en':  # 'en' sadece default, gerçek kayıt yoksa 'en'
            await send_welcome_menu(user.id, context.bot, user_lang)
            return
    
    keyboard = []
    for code, info in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"setlang_{code}"
        )])
    
    user_lang_code = user.language_code or 'en'
    welcome_texts = {
        'tr': '🌍 **Lütfen bir dil seçin:**',
        'en': '🌍 **Please choose a language:**',
        'ku': '🌍 **تکایە زمانێك هەڵبژێرە:**',
        'ar': '🌍 **الرجاء اختيار لغة:**'
    }
    
    if user_lang_code.startswith('tr'):
        text = welcome_texts['tr']
    elif user_lang_code.startswith('ar'):
        text = welcome_texts['ar']
    elif user_lang_code.startswith('ku'):
        text = welcome_texts['ku']
    else:
        text = welcome_texts['en']
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=user.id,
            text=text,
            reply_markup=reply_markup
        )

# 8) DİL SEÇİLDİĞİNDE
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("INSERT OR REPLACE INTO users (user_id, lang, joined_date) VALUES (?, ?, ?)",
              (user_id, lang_code, today))
    conn.commit()
    conn.close()
    
    confirmation_texts = {
        'tr': '✅ Dil seçildi!',
        'en': '✅ Language selected!',
        'ku': '✅ زمان هەڵبژێردرا!',
        'ar': '✅ تم اختيار اللغة!'
    }
    
    await query.edit_message_text(
        f"{LANGUAGES[lang_code]['flag']} {confirmation_texts[lang_code]}"
    )
    await send_welcome_menu(user_id, context.bot, lang_code)

# 9) PROFESYONEL HOŞGELDİN MENÜSÜ
async def send_welcome_menu(user_id: int, bot, lang: str):
    welcome_text = get_message('welcome', lang)
    
    button_texts = {
        'prompt': {
            'tr': '🚀 Prompt Alma',
            'en': '🚀 Get Prompts',
            'ku': '🚀 پرۆمپت وەرگرن',
            'ar': '🚀 احصل على المحفزات'
        },
        'channel': {
            'tr': '📢 Kanalımız',
            'en': '📢 Our Channel',
            'ku': '📢 کەناڵەکەمان',
            'ar': '📢 قناتنا'
        },
        'help': {
            'tr': '❓ Yardım',
            'en': '❓ Help',
            'ku': '❓ یارمەتی',
            'ar': '❓ مساعدة'
        },
        'language': {
            'tr': '🌐 Dil Değiştir',
            'en': '🌐 Change Language',
            'ku': '🌐 زمان بگۆڕە',
            'ar': '🌐 تغيير اللغة'
        }
    }
    
    # Grid düzeni için butonları 2'li sıralar halinde düzenle
    keyboard = [
        [
            InlineKeyboardButton(
                button_texts['prompt'][lang],
                url=PROMPT_LINK
            ),
            InlineKeyboardButton(
                button_texts['channel'][lang],
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                button_texts['help'][lang],
                callback_data="help_menu"
            ),
            InlineKeyboardButton(
                button_texts['language'][lang],
                callback_data="change_lang_menu"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Hoşgeldin menüsü gönderilemedi: {e}")

# 10) /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Ban kontrolü
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    if result and result[0] == 1:
        ban_texts = {
            'tr': '🚫 Bu botu kullanma izniniz yok.',
            'en': '🚫 You are not allowed to use this bot.',
            'ku': '🚫 ئێوە ڕێگەتانی نییە ئەم بۆتە بەکاربهێنیت.',
            'ar': '🚫 غير مسموح لك باستخدام هذا البوت.'
        }
        user_lang = get_user_lang(user.id)
        await update.message.reply_text(ban_texts[user_lang])
        conn.close()
        return
    conn.close()
    
    # Kanal aboneliği kontrolü
    if not await check_subscription(user.id, context.bot):
        await ask_for_subscription(update, context)
        return
    
    await language_selection(update, context)

# 11) ZORUNLU KANAL MESAJI
async def ask_for_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_lang = get_user_lang(user.id)
    
    messages = {
        'tr': "📢 **Devam etmek için lütfen kanala abone olun:**",
        'en': "📢 **Please subscribe to the channel to continue:**",
        'ku': "📢 **تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوامبوون:**",
        'ar': "📢 **يرجى الاشتراك في القناة للمتابعة:**"
    }
    
    keyboard = [
        [
            InlineKeyboardButton("📢 Kanalımız", url=CHANNEL_LINK),
            InlineKeyboardButton("✅ Abone oldum", callback_data="check_subscription")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            messages[user_lang],
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    elif hasattr(update, 'callback_query') and update.callback_query:
        query = update.callback_query
        await query.edit_message_text(
            messages[user_lang],
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

# 12) ABONE KONTROLÜ BUTONU
async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if await check_subscription(user_id, context.bot):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            user_lang = result[0]
            await send_welcome_menu(user_id, context.bot, user_lang)
        else:
            await language_selection(update, context)
    else:
        user_lang = get_user_lang(user_id)
        messages = {
            'tr': "❌ Hala kanalda gözükmüyorsunuz. Lütfen abone olun ve tekrar deneyin.",
            'en': "❌ You still don't appear in the channel. Please subscribe and try again.",
            'ku': "❌ هێشتا لە کەناڵەکەدا دەرنەکەوتوویت. تکایە سەبسکرایب بکە و دووبارە هەوڵبدە.",
            'ar': "❌ لا تزال غير مرئي في القناة. يرجى الاشتراك والمحاولة مرة أخرى."
        }
        await query.edit_message_text(messages[user_lang])

# 13) YARDIM MENÜSÜ
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id
    
    user_lang = get_user_lang(user_id)
    
    help_texts = {
        'tr': """🤖 **Bot Kullanım Kılavuzu**

**Komutlar:**
• /start - Botu başlatır
• /leng - Dil değiştirme
• /app - Prompt linki
• /help - Bu yardım mesajı

**Özellikler:**
• Çoklu dil desteği
• Zorunlu kanal aboneliği
• Admin duyuru sistemi
• Hızlı buton oluşturma""",
        'en': """🤖 **Bot Usage Guide**

**Commands:**
• /start - Start the bot
• /leng - Change language
• /app - Prompt link
• /help - This help message

**Features:**
• Multi-language support
• Mandatory channel subscription
• Admin announcement system
• Quick button creation""",
        'ku': """🤖 **ڕێبەری بەکارهێنانی بۆت**

**فەرمانەکان:**
• /start - بۆتەکە دەستپێبکە
• /leng - زمان بگۆڕە
• /app - لینکی پرۆمپت
• /help - ئەم پەیامی یارمەتییە

**تایبەتمەندییەکان:**
• پشتگیری فرە زمان
• سەبسکرایبی ناچاری کەناڵ
• سیستەمی ڕاگەیاندنی ئەدمین
• دروستکردنی دوگمەی خێرا""",
        'ar': """🤖 **دليل استخدام البوت**

**الأوامر:**
• /start - بدء البوت
• /leng - تغيير اللغة
• /app - رابط المحفزات
• /help - رسالة المساعدة هذه

**الميزات:**
• دعم متعدد اللغات
• اشتراك قناة إلزامي
• نظام إعلانات المسؤول
• إنشاء زر سريع"""
    }
    
    keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="back_to_welcome")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(
            help_texts[user_lang],
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=help_texts[user_lang],
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

# 14) /leng KOMUTU
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Ban kontrolü
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    if result and result[0] == 1:
        await update.message.reply_text("🚫 Bu botu kullanma izniniz yok.")
        conn.close()
        return
    conn.close()
    
    # Kanal kontrolü
    if not await check_subscription(user.id, context.bot):
        await ask_for_subscription(update, context)
        return
    
    await language_selection(update, context, is_change=True)

# 15) DİL DEĞİŞTİRME MENÜSÜ
async def change_lang_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for code, info in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"changelang_{code}"
        )])
    
    user_lang = get_user_lang(query.from_user.id)
    messages = {
        'tr': '🌍 **Yeni bir dil seçin:**',
        'en': '🌍 **Choose a new language:**',
        'ku': '🌍 **زمانێکی نوێ هەڵبژێرە:**',
        'ar': '🌍 **اختر لغة جديدة:**'
    }
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        messages[user_lang],
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 16) DİL DEĞİŞTİRME CALLBACK
async def change_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET lang=? WHERE user_id=?", (lang_code, user_id))
    conn.commit()
    conn.close()
    
    confirmation = {
        'tr': '✅ Diliniz başarıyla değiştirildi!',
        'en': '✅ Your language has been changed successfully!',
        'ku': '✅ زمانەکەت بە سەرکەوتوویی گۆڕدرا!',
        'ar': '✅ تم تغيير لغتك بنجاح!'
    }
    
    await query.edit_message_text(
        f"{LANGUAGES[lang_code]['flag']} {confirmation[lang_code]}"
    )
    await send_welcome_menu(user_id, context.bot, lang_code)

# 17) /app KOMUTU
async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Ban kontrolü
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    if result and result[0] == 1:
        await update.message.reply_text("🚫 Bu botu kullanma izniniz yok.")
        conn.close()
        return
    conn.close()
    
    # Kanal kontrolü
    if not await check_subscription(user.id, context.bot):
        await ask_for_subscription(update, context)
        return
    
    user_lang = get_user_lang(user.id)
    
    texts = {
        'tr': "🚀 **Aşağıdaki butondan prompts sayfasına gidebilirsiniz:**",
        'en': "🚀 **You can go to the prompts page from the button below:**",
        'ku': "🚀 **دەتوانیت لە بڕگەی خوارەوە بچیتە سەر پەیجی پرۆمپتەکان:**",
        'ar': "🚀 **يمكنك الانتقال إلى صفحة المحفزات من الزر أدناه:**"
    }
    
    button_texts = {
        'tr': "🔥 Prompts Alma",
        'en': "🔥 Get Prompts",
        'ku': "🔥 پرۆمپتەکان وەربگرن",
        'ar': "🔥 احصل على المحفزات"
    }
    
    keyboard = [[
        InlineKeyboardButton(
            button_texts[user_lang],
            url=PROMPT_LINK
        )
    ], [
        InlineKeyboardButton("🏠 Ana Menü", callback_data="back_to_welcome")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts[user_lang],
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 18) GERİ BUTONU
async def back_to_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    
    await send_welcome_menu(user_id, context.bot, user_lang)

# ============================
# DUYURU SİSTEMİ
# ============================

# 19) ADMIN KOMUTLARI
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="start_broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="quick_button")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton("🧪 Test Mesajı", callback_data="admin_test")],
        [InlineKeyboardButton("🚫 Kullanıcı Banla", callback_data="admin_ban_menu")],
        [InlineKeyboardButton("✅ Kullanıcı Ban Kaldır", callback_data="admin_unban_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👑 **Admin Paneli**\n\nAşağıdaki seçeneklerden birini seçin:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 20) HIZLI BUTON SİSTEMİ
async def quick_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚡ **Hızlı Buton Oluşturma**\n\n"
        "**Format:**\n"
        "`Buton Adı https://link.com`\n\n"
        "**Örnek:**\n"
        "`Prompt Aç https://t.me/PrompttAI_bot`\n"
        "`Kanalımız https://t.me/+wet-9MZuj044ZGQy`\n\n"
        "Şimdi buton bilgilerini yazın:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['waiting_for_quick_button'] = True

# 21) HIZLI BUTON MESAJI ALMA
async def receive_quick_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if not context.user_data.get('waiting_for_quick_button'):
        return
    
    message = update.message.text.strip()
    
    # URL kontrolü için regex
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, message)
    
    if urls:
        button_url = urls[0]
        # URL'yi mesajdan çıkar ve geri kalanı buton adı olarak al
        button_name = message.replace(button_url, '').strip()
        
        if not button_name:
            button_name = "Linke Git"
        
        # Onay mesajı
        keyboard = [
            [
                InlineKeyboardButton("✅ Evet, Gönder", callback_data=f"send_quick_button:{button_name}:{button_url}"),
                InlineKeyboardButton("❌ Hayır, İptal", callback_data="cancel_quick_button")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚡ **Buton Bilgileri:**\n\n"
            f"**Buton Adı:** {button_name}\n"
            f"**Buton Link:** {button_url}\n\n"
            f"Bu buton tüm kullanıcılara gönderilecek.\n"
            f"Onaylıyor musunuz?",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            "❌ Link bulunamadı! Lütfen formatı doğru yazın:\n\n"
            "`Buton Adı https://link.com`\n\n"
            "Örnek: `Prompt Aç https://t.me/PrompttAI_bot`"
        )

# 22) HIZLI BUTON GÖNDERME
async def send_quick_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    button_name = data[1]
    button_url = data[2]
    
    await query.edit_message_text("⚡ Buton gönderiliyor...")
    
    # Tüm kullanıcıları al
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, lang FROM users WHERE banned=0")
    users = c.fetchall()
    conn.close()
    
    total_users = len(users)
    success = 0
    failed = 0
    
    # Her dil için mesaj hazırla
    messages = {
        'tr': f"🔗 **Yeni Bağlantı**\n\n{button_name} butonuna tıklayın:",
        'en': f"🔗 **New Link**\n\nClick the {button_name} button:",
        'ku': f"🔗 **بەستەری نوێ**\n\nکرتە لە دوگمەی {button_name} بکە:",
        'ar': f"🔗 **رابط جديد**\n\nانقر فوق زر {button_name}:"
    }
    
    # Buton oluştur
    keyboard = [[InlineKeyboardButton(button_name, url=button_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Her kullanıcıya gönder
    for i, (user_id, user_lang) in enumerate(users):
        try:
            message_text = messages.get(user_lang, messages['en'])
            
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
            success += 1
            
            if i % 10 == 0:
                await asyncio.sleep(0.5)
                
        except Exception as e:
            failed += 1
            logger.error(f"Buton gönderilemedi {user_id}: {e}")
    
    result_text = (
        f"✅ **BUTON GÖNDERİLDİ**\n\n"
        f"📊 **İstatistikler:**\n"
        f"• Toplam Kullanıcı: {total_users}\n"
        f"• Başarılı: {success}\n"
        f"• Başarısız: {failed}\n\n"
        f"**Buton:** {button_name}\n"
        f"**Link:** {button_url}"
    )
    
    keyboard = [[InlineKeyboardButton("🏠 Ana Menü", callback_data="admin_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data.pop('waiting_for_quick_button', None)

# 23) HIZLI BUTON İPTAL
async def cancel_quick_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❌ Buton iptal edildi")
    
    context.user_data.pop('waiting_for_quick_button', None)
    
    await query.edit_message_text(
        "❌ Buton iptal edildi.\n\n"
        "Ana menüye dönmek için /admin yazın."
    )

# 24) DUYURU BAŞLATMA
async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Duyuru verilerini temizle
    context.user_data['broadcast_data'] = {
        'text': '',
        'photo': None,
        'video': None,
        'button_text': '',
        'button_url': '',
        'step': 'text'
    }
    
    await query.edit_message_text(
        "📢 **Duyuru Oluşturma**\n\n"
        "1️⃣ **Metin:** Duyuru metnini yazın\n"
        "2️⃣ **Medya (İsteğe bağlı):** Resim veya video gönderin\n"
        "3️⃣ **Buton (İsteğe bağlı):** Buton metni ve linki\n\n"
        "**Şimdi duyuru metnini yazın:**\n"
        "(İptal için /cancel)",
        parse_mode=ParseMode.MARKDOWN
    )

# 25) DUYURU METNİ ALMA
async def receive_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if 'broadcast_data' not in context.user_data:
        await update.message.reply_text("❌ Lütfen önce /admin yazıp duyuru başlatın.")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    if broadcast_data.get('step') != 'text':
        await update.message.reply_text("❌ Yanlış adım. Lütfen önce duyuru metnini yazın.")
        return
    
    broadcast_data['text'] = update.message.text
    broadcast_data['step'] = 'media'
    
    keyboard = [
        [InlineKeyboardButton("🖼️ Resim Ekle", callback_data="add_photo")],
        [InlineKeyboardButton("📹 Video Ekle", callback_data="add_video")],
        [InlineKeyboardButton("🔘 Buton Ekle", callback_data="add_button")],
        [InlineKeyboardButton("📤 Hemen Gönder", callback_data="send_now")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ **Metin kaydedildi!**\n\n"
        f"**Ne yapmak istiyorsunuz?**\n"
        f"• Resim/Video ekleyebilirsiniz\n"
        f"• Buton ekleyebilirsiniz\n"
        f"• Direkt gönderebilirsiniz",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 26) RESİM EKLEME
async def add_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if 'broadcast_data' not in context.user_data:
        await query.edit_message_text("❌ Duyuru verisi bulunamadı. Lütfen /admin ile yeniden başlayın.")
        return
    
    context.user_data['broadcast_data']['step'] = 'waiting_photo'
    
    await query.edit_message_text(
        "🖼️ **Resim Ekleyin**\n\n"
        "Lütfen duyuruya eklemek istediğiniz resmi gönderin.\n"
        "(İptal için /cancel)",
        parse_mode=ParseMode.MARKDOWN
    )

# 27) VIDEO EKLEME
async def add_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if 'broadcast_data' not in context.user_data:
        await query.edit_message_text("❌ Duyuru verisi bulunamadı. Lütfen /admin ile yeniden başlayın.")
        return
    
    context.user_data['broadcast_data']['step'] = 'waiting_video'
    
    await query.edit_message_text(
        "📹 **Video Ekleyin**\n\n"
        "Lütfen duyuruya eklemek istediğiniz videoyu gönderin.\n"
        "(İptal için /cancel)",
        parse_mode=ParseMode.MARKDOWN
    )

# 28) MEDYA ALMA (Resim/Video)
async def receive_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if 'broadcast_data' not in context.user_data:
        await update.message.reply_text("❌ Duyuru verisi bulunamadı. Lütfen /admin ile yeniden başlayın.")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    if broadcast_data.get('step') == 'waiting_photo' and update.message.photo:
        photo = update.message.photo[-1]
        broadcast_data['photo'] = photo.file_id
        broadcast_data['step'] = 'media_done'
        
        await show_broadcast_preview(update, context, "✅ Resim eklendi!")
        
    elif broadcast_data.get('step') == 'waiting_video' and update.message.video:
        video = update.message.video
        broadcast_data['video'] = video.file_id
        broadcast_data['step'] = 'media_done'
        
        await show_broadcast_preview(update, context, "✅ Video eklendi!")
    else:
        await update.message.reply_text("Lütfen resim veya video gönderin.")

# 29) BUTON EKLEME
async def add_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if 'broadcast_data' not in context.user_data:
        await query.edit_message_text("❌ Duyuru verisi bulunamadı. Lütfen /admin ile yeniden başlayın.")
        return
    
    context.user_data['broadcast_data']['step'] = 'button_text'
    
    await query.edit_message_text(
        "🔘 **Buton Ekleme**\n\n"
        "1️⃣ **Buton metnini yazın:**\n"
        "Örnek: 'Katıl', 'İndir', 'Web Sitemiz'\n\n"
        "(İptal için /cancel)",
        parse_mode=ParseMode.MARKDOWN
    )

# 30) BUTON METNİ ALMA
async def receive_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if 'broadcast_data' not in context.user_data:
        await update.message.reply_text("❌ Lütfen önce /admin yazıp duyuru başlatın.")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    if broadcast_data.get('step') != 'button_text':
        await update.message.reply_text("⚠️ Şu anda buton metni beklenmiyor. Lütfen önce '🔘 Buton Ekle' butonuna tıklayın.")
        return
    
    broadcast_data['button_text'] = update.message.text
    broadcast_data['step'] = 'button_url'
    
    await update.message.reply_text(
        f"✅ **Buton metni:** {update.message.text}\n\n"
        f"2️⃣ **Şimdi buton linkini yazın:**\n"
        f"Örnek: https://t.me/kanal_linki\n\n"
        f"(İptal için /cancel)",
        parse_mode=ParseMode.MARKDOWN
    )

# 31) BUTON LİNKİ ALMA
async def receive_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if 'broadcast_data' not in context.user_data:
        await update.message.reply_text("❌ Lütfen önce /admin yazıp duyuru başlatın.")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    if broadcast_data.get('step') != 'button_url':
        await update.message.reply_text("⚠️ Şu anda buton linki beklenmiyor. Lütfen önce buton metnini yazın.")
        return
    
    broadcast_data['button_url'] = update.message.text
    broadcast_data['step'] = 'media'
    
    await show_broadcast_preview(update, context, "✅ Buton eklendi!")

# 32) DUYURU ÖNİZLEME GÖSTER
async def show_broadcast_preview(update: Update, context: ContextTypes.DEFAULT_TYPE, message=""):
    if 'broadcast_data' not in context.user_data:
        if hasattr(update, 'message'):
            await update.message.reply_text("❌ Duyuru verisi bulunamadı.")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    preview_text = "📢 **DUYURU ÖNİZLEME**\n\n"
    
    if broadcast_data.get('photo'):
        preview_text += "🖼️ **Resim:** ✓ Var\n"
    elif broadcast_data.get('video'):
        preview_text += "📹 **Video:** ✓ Var\n"
    else:
        preview_text += "📝 **Medya:** Yok\n"
    
    if broadcast_data.get('button_text') and broadcast_data.get('button_url'):
        preview_text += f"🔘 **Buton:** {broadcast_data['button_text']}\n"
        preview_text += f"🔗 **Link:** {broadcast_data['button_url']}\n"
    else:
        preview_text += "🔘 **Buton:** Yok\n"
    
    preview_text += f"\n**Metin:**\n{broadcast_data.get('text', '')}\n"
    
    keyboard = []
    
    media_buttons = []
    if not broadcast_data.get('photo') and not broadcast_data.get('video'):
        media_buttons.append(InlineKeyboardButton("🖼️ Resim Ekle", callback_data="add_photo"))
        media_buttons.append(InlineKeyboardButton("📹 Video Ekle", callback_data="add_video"))
    
    if not broadcast_data.get('button_text'):
        media_buttons.append(InlineKeyboardButton("🔘 Buton Ekle", callback_data="add_button"))
    else:
        media_buttons.append(InlineKeyboardButton("✏️ Butonu Düzenle", callback_data="add_button"))
    
    if media_buttons:
        keyboard.append(media_buttons)
    
    keyboard.append([
        InlineKeyboardButton("📤 Gönder", callback_data="confirm_send_broadcast"),
        InlineKeyboardButton("✏️ Metni Düzenle", callback_data="edit_broadcast"),
        InlineKeyboardButton("❌ İptal", callback_data="cancel_broadcast_final")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(
            f"{message}\n\n{preview_text}" if message else preview_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    elif hasattr(update, 'callback_query'):
        query = update.callback_query
        try:
            await query.edit_message_text(
                f"{message}\n\n{preview_text}" if message else preview_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"{message}\n\n{preview_text}" if message else preview_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )

# 33) SEND_NOW (Direkt gönder)
async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await confirm_send_broadcast(update, context)

# 34) DUYURU GÖNDERME ONAY
async def confirm_send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if 'broadcast_data' not in context.user_data:
        await query.edit_message_text("❌ Duyuru verisi bulunamadı!")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    if not broadcast_data.get('text'):
        await query.edit_message_text("❌ Duyuru metni bulunamadı!")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Evet, Gönder", callback_data="execute_broadcast"),
            InlineKeyboardButton("❌ Hayır, İptal", callback_data="cancel_broadcast_final")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚠️ **SON ONAY**\n\n"
        "Bu duyuru TÜM kullanıcılara gönderilecek.\n"
        "Emin misiniz?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 35) DUYURUYU GERÇEKTEN GÖNDER
async def execute_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("📤 Duyuru gönderiliyor... Lütfen bekleyin.")
    
    if 'broadcast_data' not in context.user_data:
        await query.edit_message_text("❌ Duyuru verisi bulunamadı!")
        return
    
    broadcast_data = context.user_data.get('broadcast_data', {})
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE banned=0")
    users = c.fetchall()
    conn.close()
    
    total_users = len(users)
    success = 0
    failed = 0
    
    reply_markup = None
    if broadcast_data.get('button_text') and broadcast_data.get('button_url'):
        keyboard = [[InlineKeyboardButton(
            broadcast_data['button_text'],
            url=broadcast_data['button_url']
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    for i, user in enumerate(users):
        try:
            user_id = user[0]
            
            if broadcast_data.get('photo'):
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=broadcast_data['photo'],
                    caption=broadcast_data['text'],
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            elif broadcast_data.get('video'):
                await context.bot.send_video(
                    chat_id=user_id,
                    video=broadcast_data['video'],
                    caption=broadcast_data['text'],
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=broadcast_data['text'],
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            success += 1
            
            if i % 10 == 0:
                await asyncio.sleep(0.5)
                
        except Exception as e:
            failed += 1
            logger.error(f"Duyuru gönderilemedi {user[0]}: {e}")
    
    result_text = (
        f"✅ **DUYURU TAMAMLANDI**\n\n"
        f"📊 **İstatistikler:**\n"
        f"• Toplam Kullanıcı: {total_users}\n"
        f"• Başarılı: {success}\n"
        f"• Başarısız: {failed}\n\n"
        f"⏱️ **Gönderim süresi:** Tamamlandı"
    )
    
    keyboard = [[InlineKeyboardButton("🏠 Ana Menü", callback_data="admin_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data.pop('broadcast_data', None)

# 36) DÜZENLEME
async def edit_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await start_broadcast(update, context)

# 37) İPTAL
async def cancel_broadcast_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❌ Duyuru iptal edildi")
    
    context.user_data.pop('broadcast_data', None)
    
    await query.edit_message_text(
        "❌ Duyuru iptal edildi.\n\n"
        "Ana menüye dönmek için /admin yazın."
    )

# 38) ADMIN İSTATİSTİKLER
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    today = date.today().isoformat()
    c.execute("SELECT COUNT(*) FROM users WHERE joined_date=?", (today,))
    today_users = c.fetchone()[0]
    
    c.execute("SELECT lang, COUNT(*) FROM users GROUP BY lang")
    lang_dist = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM users WHERE banned=1")
    banned_users = c.fetchone()[0]
    
    week_ago = date.today().isoformat()
    c.execute("SELECT COUNT(*) FROM users WHERE joined_date >= ?", (week_ago,))
    active_users = c.fetchone()[0]
    
    conn.close()
    
    stats_text = f"""📊 **Bot İstatistikleri**

• 👥 Toplam Kullanıcı: `{total_users}`
• 📈 Bugün Kaydolan: `{today_users}`
• 🔥 Son 7 Gün Aktif: `{active_users}`
• 🚫 Banlı Kullanıcılar: `{banned_users}`

**🌍 Dil Dağılımı:**
"""
    
    for lang, count in lang_dist:
        lang_name = LANGUAGES.get(lang, {}).get('name', lang)
        stats_text += f"  {LANGUAGES.get(lang, {}).get('flag', '')} {lang_name}: `{count}`\n"
    
    keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="admin_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        stats_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 39) ADMIN TEST MESAJI
async def admin_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🧪 Test mesajları gönderiliyor...")
    
    for lang_code in LANGUAGES:
        await send_welcome_menu(query.from_user.id, context.bot, lang_code)
        await asyncio.sleep(1)
    
    keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="admin_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "✅ Tüm dil versiyonları test edildi!",
        reply_markup=reply_markup
    )

# 40) ADMIN BAN MENÜ
async def admin_ban_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🚫 **Kullanıcı Banlama**\n\n"
        "Kullanıcıyı banlamak için komutu kullanın:\n"
        "`/ban <user_id>`\n\n"
        "**Örnek:**\n"
        "`/ban 1234567890`\n\n"
        "◀️ Geri dönmek için aşağıdaki butonu kullanın.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Geri", callback_data="admin_main")]])
    )

# 41) ADMIN UNBAN MENÜ
async def admin_unban_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Kullanıcı Ban Kaldırma**\n\n"
        "Kullanıcının banını kaldırmak için komutu kullanın:\n"
        "`/unban <user_id>`\n\n"
        "**Örnek:**\n"
        "`/unban 1234567890`\n\n"
        "◀️ Geri dönmek için aşağıdaki butonu kullanın.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Geri", callback_data="admin_main")]])
    )

# 42) ADMIN ANA MENÜ
async def admin_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="start_broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="quick_button")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton("🧪 Test Mesajı", callback_data="admin_test")],
        [InlineKeyboardButton("🚫 Kullanıcı Banla", callback_data="admin_ban_menu")],
        [InlineKeyboardButton("✅ Kullanıcı Ban Kaldır", callback_data="admin_unban_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            "👑 **Admin Paneli**\n\nAşağıdaki seçeneklerden birini seçin:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="👑 **Admin Paneli**\n\nAşağıdaki seçeneklerden birini seçin:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

# 43) İSTATİSTİKLER (/stats)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    today = date.today().isoformat()
    c.execute("SELECT COUNT(*) FROM users WHERE joined_date=?", (today,))
    today_users = c.fetchone()[0]
    
    c.execute("SELECT lang, COUNT(*) FROM users GROUP BY lang")
    lang_dist = c.fetchall()
    
    c.execute("SELECT COUNT(*) FROM users WHERE banned=1")
    banned_users = c.fetchone()[0]
    
    conn.close()
    
    stats_text = f"""📊 **Bot İstatistikleri**

• 👥 Toplam Kullanıcı: `{total_users}`
• 📈 Bugün Kaydolan: `{today_users}`
• 🚫 Banlı Kullanıcılar: `{banned_users}`

**🌍 Dil Dağılımı:**
"""
    
    for lang, count in lang_dist:
        lang_name = LANGUAGES.get(lang, {}).get('name', lang)
        stats_text += f"  {LANGUAGES.get(lang, {}).get('flag', '')} {lang_name}: `{count}`\n"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

# 44) BAN/UNBAN SİSTEMİ
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Kullanım: `/ban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        target_id = int(context.args[0])
        
        if target_id == ADMIN_ID:
            await update.message.reply_text("❌ Kendinizi banlayamazsınız!")
            return
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT user_id FROM users WHERE user_id=?", (target_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (user_id, lang, joined_date, banned) VALUES (?, ?, ?, ?)",
                     (target_id, 'en', date.today().isoformat(), 1))
        else:
            c.execute("UPDATE users SET banned=1 WHERE user_id=?", (target_id,))
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"✅ Kullanıcı `{target_id}` başarıyla banlandı.", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ban hatası: {e}")
        await update.message.reply_text("❌ Geçersiz kullanıcı ID'si veya bir hata oluştu.")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Kullanım: `/unban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        target_id = int(context.args[0])
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET banned=0 WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"✅ Kullanıcı `{target_id}` banı kaldırıldı.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("❌ Geçersiz kullanıcı ID'si.")

# 45) /test KOMUTU
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    await update.message.reply_text("🧪 Test mesajları gönderiliyor...")
    
    for lang_code in LANGUAGES:
        await send_welcome_menu(user.id, context.bot, lang_code)
        await asyncio.sleep(1)
    
    await update.message.reply_text("✅ Tüm dil versiyonları test edildi.")

# 46) HATA YAKALAMA
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception occurred:", exc_info=context.error)
    
    try:
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🤖 **Bot hatası:**\n\n```{context.error}```"
            )
    except:
        pass

# 47) İPTAL KOMUTU
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    context.user_data.pop('broadcast_data', None)
    context.user_data.pop('waiting_for_quick_button', None)
    
    await update.message.reply_text(
        "❌ İşlem iptal edildi.\n\n"
        "Ana menüye dönmek için /admin yazın."
    )

# 48) ADMIN MESAJ HANDLER
async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    # Hızlı buton için kontrol
    if context.user_data.get('waiting_for_quick_button'):
        await receive_quick_button(update, context)
        return
    
    # Duyuru için kontrol
    if 'broadcast_data' in context.user_data:
        broadcast_data = context.user_data.get('broadcast_data', {})
        current_step = broadcast_data.get('step', 'unknown')
        
        if current_step == 'text':
            await receive_broadcast_text(update, context)
        elif current_step == 'button_text':
            await receive_button_text(update, context)
        elif current_step == 'button_url':
            await receive_button_url(update, context)
        elif current_step in ['waiting_photo', 'waiting_video']:
            await update.message.reply_text(f"⚠️ Şu anda {current_step} adımındasınız. Lütfen bekleneni yapın.")
        elif current_step in ['media', 'media_done']:
            await update.message.reply_text("ℹ️ Duyurunuz hazır. Lütfen önizlemedeki butonları kullanın.")

# 49) ANA UYGULAMA
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komut handler'ları
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("leng", change_language))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Callback query handler'ları
    application.add_handler(CallbackQueryHandler(set_language, pattern="^setlang_"))
    application.add_handler(CallbackQueryHandler(change_language_callback, pattern="^changelang_"))
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(help_menu, pattern="^help_menu$"))
    application.add_handler(CallbackQueryHandler(back_to_welcome, pattern="^back_to_welcome$"))
    application.add_handler(CallbackQueryHandler(change_lang_menu, pattern="^change_lang_menu$"))
    
    # Admin callback handler'ları
    application.add_handler(CallbackQueryHandler(start_broadcast, pattern="^start_broadcast$"))
    application.add_handler(CallbackQueryHandler(quick_button, pattern="^quick_button$"))
    application.add_handler(CallbackQueryHandler(add_photo, pattern="^add_photo$"))
    application.add_handler(CallbackQueryHandler(add_video, pattern="^add_video$"))
    application.add_handler(CallbackQueryHandler(add_button, pattern="^add_button$"))
    application.add_handler(CallbackQueryHandler(send_now, pattern="^send_now$"))
    application.add_handler(CallbackQueryHandler(confirm_send_broadcast, pattern="^confirm_send_broadcast$"))
    application.add_handler(CallbackQueryHandler(execute_broadcast, pattern="^execute_broadcast$"))
    application.add_handler(CallbackQueryHandler(send_quick_button, pattern="^send_quick_button:"))
    application.add_handler(CallbackQueryHandler(cancel_quick_button, pattern="^cancel_quick_button$"))
    application.add_handler(CallbackQueryHandler(edit_broadcast, pattern="^edit_broadcast$"))
    application.add_handler(CallbackQueryHandler(cancel_broadcast_final, pattern="^cancel_broadcast_final$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_test, pattern="^admin_test$"))
    application.add_handler(CallbackQueryHandler(admin_ban_menu, pattern="^admin_ban_menu$"))
    application.add_handler(CallbackQueryHandler(admin_unban_menu, pattern="^admin_unban_menu$"))
    application.add_handler(CallbackQueryHandler(admin_main, pattern="^admin_main$"))
    
    # Mesaj handler'ları
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
        handle_admin_messages
    ))
    
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO) & filters.User(ADMIN_ID),
        receive_media
    ))
    
    # Hata handler
    application.add_error_handler(error_handler)
    
    # Botu başlat
    logger.info("Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
