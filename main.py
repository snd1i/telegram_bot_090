import logging
import sqlite3
import os
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import asyncio

# Basit logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN ayarlanmamış!")

# Ayarlar
ADMIN_ID = 5541236874
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"
PROMPT_LINK = "https://t.me/PrompttAI_bot/Prompts"

# Database
DB_NAME = "bot_database.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (user_id INTEGER PRIMARY KEY, 
                     lang TEXT DEFAULT 'en',
                     joined_date DATE DEFAULT CURRENT_DATE,
                     banned INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()
        logger.info("Database hazır")
    except Exception as e:
        logger.error(f"Database hatası: {e}")

init_db()

# Dil sistemi
LANGUAGES = {
    'tr': '🇹🇷 Türkçe',
    'en': '🇬🇧 English', 
    'ku': '🇹🇯 کوردی',
    'ar': '🇸🇦 العربية'
}

def get_user_lang(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 'en'
    except:
        return 'en'

def save_user(user_id, lang):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        today = date.today().isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, lang, joined_date) VALUES (?, ?, ?)", 
                  (user_id, lang, today))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Kullanıcı kaydetme hatası: {e}")

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Yeni kullanıcı: {user.id}")
    
    # Dil seçim butonları
    keyboard = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇯 کوردی", callback_data="lang_ku")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 **Lütfen dilinizi seçin / Please choose your language:**",
        reply_markup=reply_markup
    )

# Dil seçimi
async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    # Kullanıcıyı kaydet
    save_user(user_id, lang_code)
    
    # Hoşgeldin mesajı
    welcome_texts = {
        'tr': "🤖 **Hoş geldin!**\n\nAşağıdaki butonları kullanabilirsin:",
        'en': "🤖 **Welcome!**\n\nYou can use the buttons below:",
        'ku': "🤖 **بەخێربێیت!**\n\nدەتوانیت ئەم دوگمانەی خوارەوە بەکاربهێنیت:",
        'ar': "🤖 **أهلاً بك!**\n\nيمكنك استخدام الأزرار أدناه:"
    }
    
    button_texts = {
        'tr': {
            'prompt': '🚀 Prompt Alma',
            'channel': '📢 Kanalımız',
            'help': '❓ Yardım',
            'lang': '🌐 Dil Değiştir'
        },
        'en': {
            'prompt': '🚀 Get Prompts',
            'channel': '📢 Our Channel',
            'help': '❓ Help',
            'lang': '🌐 Change Language'
        },
        'ku': {
            'prompt': '🚀 پرۆمپت وەرگرن',
            'channel': '📢 کەناڵەکەمان',
            'help': '❓ یارمەتی',
            'lang': '🌐 زمان بگۆڕە'
        },
        'ar': {
            'prompt': '🚀 احصل على المحفزات',
            'channel': '📢 قناتنا',
            'help': '❓ مساعدة',
            'lang': '🌐 تغيير اللغة'
        }
    }
    
    texts = button_texts.get(lang_code, button_texts['en'])
    
    keyboard = [
        [
            InlineKeyboardButton(texts['prompt'], url=PROMPT_LINK),
            InlineKeyboardButton(texts['channel'], url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(texts['help'], callback_data="help_menu"),
            InlineKeyboardButton(texts['lang'], callback_data="change_lang")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        welcome_texts.get(lang_code, welcome_texts['en']),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# Ana menü
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    
    welcome_texts = {
        'tr': "🤖 **Ana Menü**\n\nAşağıdaki butonları kullanabilirsin:",
        'en': "🤖 **Main Menu**\n\nYou can use the buttons below:",
        'ku': "🤖 **مێنیوی سەرەکی**\n\nدەتوانیت ئەم دوگمانەی خوارەوە بەکاربهێنیت:",
        'ar': "🤖 **القائمة الرئيسية**\n\nيمكنك استخدام الأزرار أدناه:"
    }
    
    button_texts = {
        'tr': {
            'prompt': '🚀 Prompt Alma',
            'channel': '📢 Kanalımız',
            'help': '❓ Yardım',
            'lang': '🌐 Dil Değiştir'
        },
        'en': {
            'prompt': '🚀 Get Prompts',
            'channel': '📢 Our Channel',
            'help': '❓ Help',
            'lang': '🌐 Change Language'
        },
        'ku': {
            'prompt': '🚀 پرۆمپت وەرگرن',
            'channel': '📢 کەناڵەکەمان',
            'help': '❓ یارمەتی',
            'lang': '🌐 زمان بگۆڕە'
        },
        'ar': {
            'prompt': '🚀 احصل على المحفزات',
            'channel': '📢 قناتنا',
            'help': '❓ مساعدة',
            'lang': '🌐 تغيير اللغة'
        }
    }
    
    texts = button_texts.get(user_lang, button_texts['en'])
    
    keyboard = [
        [
            InlineKeyboardButton(texts['prompt'], url=PROMPT_LINK),
            InlineKeyboardButton(texts['channel'], url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(texts['help'], callback_data="help_menu"),
            InlineKeyboardButton(texts['lang'], callback_data="change_lang")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        welcome_texts.get(user_lang, welcome_texts['en']),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# Yardım
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        is_callback = True
    else:
        user_id = update.effective_user.id
        is_callback = False
    
    user_lang = get_user_lang(user_id)
    
    help_texts = {
        'tr': """🤖 **Bot Kullanımı**

**Komutlar:**
/start - Botu başlat
/leng - Dil değiştir
/app - Prompt linki
/help - Yardım

**Admin Komutları:**
/admin - Admin paneli""",
        
        'en': """🤖 **Bot Usage**

**Commands:**
/start - Start bot
/leng - Change language
/app - Prompt link
/help - Help

**Admin Commands:**
/admin - Admin panel""",
        
        'ku': """🤖 **بەکارهێنانی بۆت**

**فەرمانەکان:**
/start - بۆت دەستپێبکە
/leng - زمان بگۆڕە
/app - لینکی پرۆمپت
/help - یارمەتی

**فەرمانەکانی ئەدمین:**
/admin - پانێلی ئەدمین""",
        
        'ar': """🤖 **استخدام البوت**

**الأوامر:**
/start - بدء البوت
/leng - تغيير اللغة
/app - رابط المحفزات
/help - مساعدة

**أوامر المسؤول:**
/admin - لوحة المسؤول"""
    }
    
    keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = help_texts.get(user_lang, help_texts['en'])
    
    if is_callback:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

# Dil değiştirme
async def change_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇯 کوردی", callback_data="lang_ku")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🌍 **Yeni dil seçin / Choose new language:**",
        reply_markup=reply_markup
    )

# /app komutu
async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_lang = get_user_lang(user.id)
    
    texts = {
        'tr': "🚀 **Prompt almak için butona tıklayın:**",
        'en': "🚀 **Click the button to get prompts:**",
        'ku': "🚀 **کرتە لە دوگمەکە بکە بۆ وەرگرتنی پرۆمپت:**",
        'ar': "🚀 **انقر فوق الزر للحصول على المحفزات:**"
    }
    
    button_texts = {
        'tr': "🔥 Prompt Alma",
        'en': "🔥 Get Prompts", 
        'ku': "🔥 پرۆمپت وەربگرن",
        'ar': "🔥 احصل على المحفزات"
    }
    
    keyboard = [[
        InlineKeyboardButton(
            button_texts.get(user_lang, button_texts['en']),
            url=PROMPT_LINK
        )
    ]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts.get(user_lang, texts['en']),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

# /leng komutu
async def leng_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇯 کوردی", callback_data="lang_ku")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 **Yeni dil seçin / Choose new language:**",
        reply_markup=reply_markup
    )

# /admin komutu
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Yetkiniz yok!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="admin_quickbtn")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👑 **Admin Paneli**",
        reply_markup=reply_markup
    )

# İstatistikler
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE banned=1")
        banned = c.fetchone()[0]
        
        c.execute("SELECT lang, COUNT(*) FROM users GROUP BY lang")
        langs = c.fetchall()
        
        conn.close()
        
        stats = f"📊 **İstatistikler**\n\n"
        stats += f"• Toplam Kullanıcı: {total}\n"
        stats += f"• Banlı Kullanıcı: {banned}\n\n"
        stats += "**Diller:**\n"
        
        for lang, count in langs:
            lang_name = LANGUAGES.get(lang, lang)
            stats += f"  {lang_name}: {count}\n"
        
        keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await query.edit_message_text("❌ Hata!")

# Hızlı buton
async def admin_quickbtn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚡ **Hızlı Buton Oluştur**\n\n"
        "Buton adı ve linkini gönderin:\n"
        "Örnek: `Promtlar https://t.me/link`"
    )
    
    context.user_data['quick_button'] = True

# Broadcast
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📢 **Duyuru Gönder**\n\n"
        "Duyuru metnini gönderin:"
    )
    
    context.user_data['broadcast'] = True

# Admin mesajları
async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    # Hızlı buton
    if context.user_data.get('quick_button'):
        text = update.message.text
        
        if 'http' in text:
            # Basit parsing
            parts = text.split('http')
            if len(parts) >= 2:
                btn_name = parts[0].strip()
                btn_url = 'http' + parts[1].strip()
                
                # Buton gönder
                keyboard = [[InlineKeyboardButton(btn_name, url=btn_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                try:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("SELECT user_id FROM users WHERE banned=0")
                    users = c.fetchall()
                    conn.close()
                    
                    sent = 0
                    for user_row in users:
                        try:
                            await context.bot.send_message(
                                user_row[0],
                                "🔗 **Yeni bağlantı!**",
                                reply_markup=reply_markup
                            )
                            sent += 1
                            await asyncio.sleep(0.1)
                        except:
                            continue
                    
                    await update.message.reply_text(f"✅ {sent} kullanıcıya gönderildi!")
                    
                except Exception as e:
                    await update.message.reply_text(f"❌ Hata: {e}")
        
        context.user_data.pop('quick_button', None)
        return
    
    # Broadcast
    if context.user_data.get('broadcast'):
        text = update.message.text
        
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT user_id FROM users WHERE banned=0")
            users = c.fetchall()
            conn.close()
            
            sent = 0
            for user_row in users:
                try:
                    await context.bot.send_message(
                        user_row[0],
                        text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent += 1
                    await asyncio.sleep(0.1)
                except:
                    continue
            
            await update.message.reply_text(f"✅ {sent} kullanıcıya gönderildi!")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")
        
        context.user_data.pop('broadcast', None)
        return

# Admin geri
async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="admin_quickbtn")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "👑 **Admin Paneli**",
        reply_markup=reply_markup
    )

# Hata handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Hata: {context.error}")

# Ana fonksiyon
def main():
    # Application oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("leng", leng_command))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Callback'ler
    application.add_handler(CallbackQueryHandler(select_language, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(help_menu, pattern="^help_menu$"))
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(change_language_menu, pattern="^change_lang$"))
    
    # Admin callback'ler
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_quickbtn, pattern="^admin_quickbtn$"))
    application.add_handler(CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_back, pattern="^admin_back$"))
    
    # Admin mesajları
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
        handle_admin_messages
    ))
    
    # Hata handler
    application.add_error_handler(error_handler)
    
    # Botu başlat
    logger.info("Bot başlatılıyor...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
