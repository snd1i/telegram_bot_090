import logging
import json
import sqlite3
import os
from datetime import datetime, date
from typing import Dict, Optional, Tuple, List
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand, BotCommandScopeChat
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
    
    # Varsayılan hoşgeldin mesajları
    default_welcome = {
        'tr': 'Hoş geldin! Aşağıdaki seçenekleri kullanabilirsin.',
        'en': 'Welcome! You can use the options below.',
        'ku': 'بەخێربێیت! دەتوانیت ئەم هەڵبژاردانەی خوارەوە بەکاربهێنیت.',  # Düzeltildi
        'ar': 'أهلاً بك! يمكنك استخدام الخيارات أدناه.'
    }
    
    c.execute("SELECT key FROM messages WHERE key='welcome'")
    if not c.fetchone():
        c.execute("INSERT INTO messages (key, tr, en, ku, ar) VALUES (?, ?, ?, ?, ?)",
                  ('welcome', default_welcome['tr'], default_welcome['en'], 
                   default_welcome['ku'], default_welcome['ar']))
    
    conn.commit()
    conn.close()

init_db()

# 5) DİL SİSTEMİ - KÜRTÇE SORANİ DÜZELTİLDİ
LANGUAGES = {
    'tr': {'flag': '🇹🇷', 'name': 'Türkçe'},
    'en': {'flag': '🇬🇧', 'name': 'English'},
    'ku': {'flag': '🇹🇯', 'name': 'کوردی سۆرانی'},  # DÜZELTİLDİ: Arapça harflerle
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
    c.execute(f"SELECT {lang} FROM messages WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else f"[{key}]"

# 6) ZORUNLU KANAL KONTROLÜ
async def check_subscription(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Kanal kontrol hatası: {e}")
        return True

# 7) DİL SEÇİMİ EKRANI (SADECE İLK START)
async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT lang FROM users WHERE user_id=?", (user.id,))
    user_exists = c.fetchone()
    conn.close()
    
    if user_exists:
        if query:
            await query.answer()
            await query.delete_message()
        await send_welcome_menu(user.id, context.bot, user_exists[0])
        return
    
    keyboard = []
    for code, info in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"setlang_{code}"
        )])
    
    user_lang_code = user.language_code or 'en'
    welcome_texts = {
        'tr': 'Lütfen bir dil seçin:',
        'en': 'Please choose a language:',
        'ku': 'تکایە زمانێك هەڵبژێرە:',  # Düzeltildi
        'ar': 'الرجاء اختيار لغة:'
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
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
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
        'tr': 'Dil seçildi',
        'en': 'Language selected',
        'ku': 'زمان هەڵبژێردرا',  # Düzeltildi
        'ar': 'تم اختيار اللغة'
    }
    
    await query.edit_message_text(
        f"{LANGUAGES[lang_code]['flag']} {confirmation_texts[lang_code]}"
    )
    await send_welcome_menu(user_id, context.bot, lang_code)

# 9) HOŞGELDİN MENÜSÜ
async def send_welcome_menu(user_id: int, bot, lang: str):
    welcome_text = get_message('welcome', lang)
    
    button_texts = {
        'prompt': {
            'tr': 'Prompt', 
            'en': 'Prompt', 
            'ku': 'پرۆمپت',  # Düzeltildi
            'ar': 'Prompt'
        },
        'channel': {
            'tr': 'Kanal', 
            'en': 'Channel', 
            'ku': 'کەناڵ',  # Düzeltildi
            'ar': 'قناة'
        },
        'help': {
            'tr': 'Yardım', 
            'en': 'Help', 
            'ku': 'یارمەتی',  # Düzeltildi
            'ar': 'مساعدة'
        }
    }
    
    keyboard = [
        [InlineKeyboardButton(
            button_texts['prompt'][lang],
            url="https://t.me/PrompttAI_bot/Prompts"
        )],
        [InlineKeyboardButton(
            button_texts['channel'][lang],
            url=CHANNEL_LINK
        )],
        [InlineKeyboardButton(
            button_texts['help'][lang],
            callback_data="help_menu"
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(
        chat_id=user_id,
        text=welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# 10) /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    if result and result[0] == 1:
        ban_texts = {
            'tr': 'Bu botu kullanma izniniz yok.',
            'en': 'You are not allowed to use this bot.',
            'ku': 'ئێوە ڕێگەتانی نییە ئەم بۆتە بەکاربهێنیت.',  # Düzeltildi
            'ar': 'غير مسموح لك باستخدام هذا البوت.'
        }
        user_lang = get_user_lang(user.id)
        await update.message.reply_text(ban_texts[user_lang])
        conn.close()
        return
    conn.close()
    
    if not await check_subscription(user.id, context.bot):
        await ask_for_subscription(update, context)
        return
    
    await language_selection(update, context)

# 11) ZORUNLU KANAL MESAJI
async def ask_for_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT lang FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    user_lang = result[0] if result else 'en'
    conn.close()
    
    messages = {
        'tr': "Devam etmek için lütfen kanala abone olun:",
        'en': "Please subscribe to the channel to continue:",
        'ku': "تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوامبوون:",  # Düzeltildi
        'ar': "يرجى الاشتراك في القناة للمتابعة:"
    }
    
    keyboard = [[
        InlineKeyboardButton("Kanal", url=CHANNEL_LINK),
        InlineKeyboardButton("Abone oldum ✅", callback_data="check_subscription")
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            messages[user_lang],
            reply_markup=reply_markup
        )
    elif update.callback_query:
        query = update.callback_query
        await query.edit_message_text(
            messages[user_lang],
            reply_markup=reply_markup
        )

# 12) ABONE KONTROLÜ BUTONU
async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await check_subscription(query.from_user.id, context.bot):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT lang FROM users WHERE user_id=?", (query.from_user.id,))
        result = c.fetchone()
        user_lang = result[0] if result else 'en'
        conn.close()
        
        if result:
            await send_welcome_menu(query.from_user.id, context.bot, user_lang)
        else:
            await language_selection(update, context)
    else:
        user_lang = get_user_lang(query.from_user.id)
        messages = {
            'tr': "Hala kanalda gözükmüyorsunuz. Lütfen abone olun ve tekrar deneyin.",
            'en': "You still don't appear in the channel. Please subscribe and try again.",
            'ku': "هێشتا لە کەناڵەکەدا دەرنەکەوتوویت. تکایە سەبسکرایب بکە و دووبارە هەوڵبدە.",  # Düzeltildi
            'ar': "لا تزال غير مرئي في القناة. يرجى الاشتراك والمحاولة مرة أخرى."
        }
        await query.edit_message_text(messages[user_lang])

# 13) YARDIM MENÜSÜ
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_lang = get_user_lang(query.from_user.id)
    
    help_texts = {
        'tr': """🤖 **Bot Kullanım Kılavuzu**

• /start - Botu başlatır
• /leng - Dil değiştirme
• /app - Prompt linki
• /help - Bu yardım mesajı

**Özellikler:**
- Çoklu dil desteği
- Zorunlu kanal aboneliği
- Admin duyuru sistemi""",
        'en': """🤖 **Bot Usage Guide**

• /start - Start the bot
• /leng - Change language
• /app - Prompt link
• /help - This help message

**Features:**
- Multi-language support
- Mandatory channel subscription
- Admin announcement system""",
        'ku': """🤖 **ڕێبەری بەکارهێنانی بۆت**

• /start - بۆتەکە دەستپێبکە
• /leng - زمان بگۆڕە
• /app - لینکی پرۆمپت
• /help - ئەم پەیامی یارمەتییە

**تایبەتمەندییەکان:**
- پشتگیری فرە زمان
- سەبسکرایبی ناچاری کەناڵ
- سیستەمی ڕاگەیاندنی ئەدمین""",  # Düzeltildi
        'ar': """🤖 **دليل استخدام البوت**

• /start - بدء البوت
• /leng - تغيير اللغة
• /app - رابط المحفزات
• /help - رسالة المساعدة هذه

**الميزات:**
- دعم متعدد اللغات
- اشتراك قناة إلزامي
- نظام إعلانات المسؤول"""
    }
    
    keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="back_to_welcome")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        help_texts[user_lang],
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 14) /leng KOMUTU
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    if result and result[0] == 1:
        await update.message.reply_text("Bu botu kullanma izniniz yok.")
        conn.close()
        return
    conn.close()
    
    if not await check_subscription(user.id, context.bot):
        await ask_for_subscription(update, context)
        return
    
    keyboard = []
    for code, info in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"changelang_{code}"
        )])
    
    user_lang = get_user_lang(user.id)
    messages = {
        'tr': 'Yeni bir dil seçin:',
        'en': 'Choose a new language:',
        'ku': 'زمانێکی نوێ هەڵبژێرە:',  # Düzeltildi
        'ar': 'اختر لغة جديدة:'
    }
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        messages[user_lang],
        reply_markup=reply_markup
    )

# 15) DİL DEĞİŞTİRME CALLBACK
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
        'tr': 'Diliniz başarıyla değiştirildi!',
        'en': 'Your language has been changed successfully!',
        'ku': 'زمانەکەت بە سەرکەوتوویی گۆڕدرا!',  # Düzeltildi
        'ar': 'تم تغيير لغتك بنجاح!'
    }
    
    await query.edit_message_text(
        f"{LANGUAGES[lang_code]['flag']} {confirmation[lang_code]}"
    )
    await send_welcome_menu(user_id, context.bot, lang_code)

# 16) /app KOMUTU
async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id=?", (user.id,))
    result = c.fetchone()
    if result and result[0] == 1:
        await update.message.reply_text("Bu botu kullanma izniniz yok.")
        conn.close()
        return
    conn.close()
    
    if not await check_subscription(user.id, context.bot):
        await ask_for_subscription(update, context)
        return
    
    user_lang = get_user_lang(user.id)
    
    texts = {
        'tr': "Aşağıdaki butondan prompts sayfasına gidebilirsiniz:",
        'en': "You can go to the prompts page from the button below:",
        'ku': "دەتوانیت لە بڕگەی خوارەوە بچیتە سەر پەیجی پرۆمپتەکان:",  # Düzeltildi
        'ar': "يمكنك الانتقال إلى صفحة المحفزات من الزر أدناه:"
    }
    
    button_texts = {
        'tr': "Prompts 🔥",
        'en': "Prompts 🔥",
        'ku': "پرۆمپتەکان 🔥",  # Düzeltildi
        'ar': "المحفزات 🔥"
    }
    
    keyboard = [[
        InlineKeyboardButton(
            button_texts[user_lang],
            url="https://t.me/+wet-9MZuj044ZGQy"
        )
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts[user_lang],
        reply_markup=reply_markup
    )

# 17) GERİ BUTONU
async def back_to_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    
    await send_welcome_menu(user_id, context.bot, user_lang)

# 18) ADMIN KOMUTLARI
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Bu komut sadece adminler içindir.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("✏️ Hoşgeldin Mesajı Düzenle", callback_data="admin_edit_welcome")],
        [InlineKeyboardButton("🌍 Dil Mesajlarını Düzenle", callback_data="admin_edit_lang")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton("🚫 Ban/Unban Kullanıcı", callback_data="admin_ban")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "**Admin Paneli**\nAşağıdaki seçeneklerden birini seçin:",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# 19) İSTATİSTİKLER (/stats)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Bu komut sadece adminler içindir.")
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

• Toplam Kullanıcı: `{total_users}`
• Bugün Kaydolan: `{today_users}`
• Banlı Kullanıcılar: `{banned_users}`

**Dil Dağılımı:**
"""
    
    for lang, count in lang_dist:
        lang_name = LANGUAGES.get(lang, {}).get('name', lang)
        stats_text += f"  {LANGUAGES.get(lang, {}).get('flag', '')} {lang_name}: `{count}`\n"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

# 20) BAN/UNBAN SİSTEMİ
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Bu komut sadece adminler içindir.")
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: `/ban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        target_id = int(context.args[0])
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET banned=1 WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"Kullanıcı `{target_id}` banlandı.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("Geçersiz kullanıcı ID'si.")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Bu komut sadece adminler içindir.")
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: `/unban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        target_id = int(context.args[0])
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET banned=0 WHERE user_id=?", (target_id,))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"Kullanıcı `{target_id}` banı kaldırıldı.", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("Geçersiz kullanıcı ID'si.")

# 21) /test KOMUTU
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("Bu komut sadece adminler içindir.")
        return
    
    for lang_code in LANGUAGES:
        await send_welcome_menu(user.id, context.bot, lang_code)
        await asyncio.sleep(1)
    
    await update.message.reply_text("✅ Tüm dil versiyonları test edildi.")

# 22) HATA YAKALAMA
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception occurred:", exc_info=context.error)
    
    try:
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Bot hatası:\n{context.error}"
            )
    except:
        pass

# 23) ANA UYGULAMA
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("leng", change_language))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("help", lambda u,c: help_menu(u,c) if u.callback_query else None))
    
    application.add_handler(CallbackQueryHandler(set_language, pattern="^setlang_"))
    application.add_handler(CallbackQueryHandler(change_language_callback, pattern="^changelang_"))
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(help_menu, pattern="^help_menu$"))
    application.add_handler(CallbackQueryHandler(back_to_welcome, pattern="^back_to_welcome$"))
    
    application.add_error_handler(error_handler)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
