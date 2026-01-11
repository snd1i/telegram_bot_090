import os
import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Logging ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token kontrolü
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN bulunamadı! Railway Variables'dan ayarlayın.")
    raise SystemExit(1)

# Admin ID
ADMIN_ID = 5541236874

# Linkler
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"
PROMPT_LINK = "https://t.me/PrompttAI_bot/Prompts"

# Database
DB_FILE = "bot_data.db"

def init_database():
    """Veritabanını başlat"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'en',
            registered_date TEXT,
            last_active TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Veritabanı hazır")

init_database()

def get_user_language(user_id):
    """Kullanıcının dilini getir"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'en'
    except:
        return 'en'

def save_user(user_id, language='en'):
    """Kullanıcıyı kaydet"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, language, registered_date, last_active)
            VALUES (?, ?, ?, ?)
        ''', (user_id, language, now, now))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Kullanıcı kaydetme hatası: {e}")

# Diller
LANGUAGES = {
    'tr': '🇹🇷 Türkçe',
    'en': '🇬🇧 English',
    'ku': '🇹🇯 کوردی',
    'ar': '🇸🇦 العربية'
}

# /start komutu
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botu başlat"""
    user = update.effective_user
    
    # Dil seçim butonları
    buttons = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇯 کوردی", callback_data="lang_ku")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        "🌍 **Lütfen dilinizi seçin / Please select your language:**",
        reply_markup=keyboard
    )

# Dil seçimi
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dil seçimini işle"""
    query = update.callback_query
    await query.answer()
    
    language = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    # Kullanıcıyı kaydet
    save_user(user_id, language)
    
    # Hoşgeldin mesajı
    welcome_messages = {
        'tr': "🤖 **Hoş geldiniz!**\n\nAşağıdaki butonları kullanabilirsiniz:",
        'en': "🤖 **Welcome!**\n\nYou can use the buttons below:",
        'ku': "🤖 **بەخێربێیت!**\n\nدەتوانیت ئەم دوگمانەی خوارەوە بەکاربهێنیت:",
        'ar': "🤖 **أهلاً بك!**\n\nيمكنك استخدام الأزرار أدناه:"
    }
    
    # Buton metinleri
    button_texts = {
        'tr': {
            'prompts': '🚀 Prompt Alma',
            'channel': '📢 Kanalımız',
            'help': '❓ Yardım',
            'lang': '🌐 Dil Değiştir'
        },
        'en': {
            'prompts': '🚀 Get Prompts',
            'channel': '📢 Our Channel',
            'help': '❓ Help',
            'lang': '🌐 Change Language'
        },
        'ku': {
            'prompts': '🚀 پرۆمپت وەرگرن',
            'channel': '📢 کەناڵەکەمان',
            'help': '❓ یارمەتی',
            'lang': '🌐 زمان بگۆڕە'
        },
        'ar': {
            'prompts': '🚀 احصل على المحفزات',
            'channel': '📢 قناتنا',
            'help': '❓ مساعدة',
            'lang': '🌐 تغيير اللغة'
        }
    }
    
    texts = button_texts.get(language, button_texts['en'])
    
    # Butonlar
    buttons = [
        [
            InlineKeyboardButton(texts['prompts'], url=PROMPT_LINK),
            InlineKeyboardButton(texts['channel'], url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(texts['help'], callback_data="help"),
            InlineKeyboardButton(texts['lang'], callback_data="change_lang")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        welcome_messages.get(language, welcome_messages['en']),
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# Ana menü
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ana menüye dön"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = get_user_language(user_id)
    
    welcome_messages = {
        'tr': "🤖 **Ana Menü**\n\nAşağıdaki butonları kullanabilirsiniz:",
        'en': "🤖 **Main Menu**\n\nYou can use the buttons below:",
        'ku': "🤖 **مێنیوی سەرەکی**\n\nدەتوانیت ئەم دوگمانەی خوارەوە بەکاربهێنیت:",
        'ar': "🤖 **القائمة الرئيسية**\n\nيمكنك استخدام الأزرار أدناه:"
    }
    
    button_texts = {
        'tr': {
            'prompts': '🚀 Prompt Alma',
            'channel': '📢 Kanalımız',
            'help': '❓ Yardım',
            'lang': '🌐 Dil Değiştir'
        },
        'en': {
            'prompts': '🚀 Get Prompts',
            'channel': '📢 Our Channel',
            'help': '❓ Help',
            'lang': '🌐 Change Language'
        },
        'ku': {
            'prompts': '🚀 پرۆمپت وەرگرن',
            'channel': '📢 کەناڵەکەمان',
            'help': '❓ یارمەتی',
            'lang': '🌐 زمان بگۆڕە'
        },
        'ar': {
            'prompts': '🚀 احصل على المحفزات',
            'channel': '📢 قناتنا',
            'help': '❓ مساعدة',
            'lang': '🌐 تغيير اللغة'
        }
    }
    
    texts = button_texts.get(language, button_texts['en'])
    
    buttons = [
        [
            InlineKeyboardButton(texts['prompts'], url=PROMPT_LINK),
            InlineKeyboardButton(texts['channel'], url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton(texts['help'], callback_data="help"),
            InlineKeyboardButton(texts['lang'], callback_data="change_lang")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        welcome_messages.get(language, welcome_messages['en']),
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# Yardım
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yardım mesajı"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        edit_message = True
    else:
        user_id = update.effective_user.id
        edit_message = False
    
    language = get_user_language(user_id)
    
    help_texts = {
        'tr': """🤖 **Bot Kullanımı**

**Komutlar:**
/start - Botu başlat
/language - Dil değiştir
/prompts - Prompt linki
/help - Bu mesajı göster

**Butonlar:**
• Prompt Alma - Promptları görüntüle
• Kanalımız - Resmi kanalımıza katıl
• Yardım - Yardım mesajı
• Dil Değiştir - Dil tercihinizi değiştirin""",
        
        'en': """🤖 **Bot Usage**

**Commands:**
/start - Start the bot
/language - Change language
/prompts - Get prompt links
/help - Show this message

**Buttons:**
• Get Prompts - View prompts
• Our Channel - Join our official channel
• Help - Help message
• Change Language - Change your language preference""",
        
        'ku': """🤖 **بەکارهێنانی بۆت**

**فەرمانەکان:**
/start - بۆتەکە دەستپێبکە
/language - زمان بگۆڕە
/prompts - لینکی پرۆمپتەکان
/help - ئەم پەیامە پیشان بدە

**دوگمەکان:**
• پرۆمپت وەرگرن - پرۆمپتەکان ببینە
• کەناڵەکەمان - بچۆ بۆ کەناڵە فەرمییەکەمان
• یارمەتی - پەیامی یارمەتی
• زمان بگۆڕە - هەڵبژاردنی زمان بگۆڕە""",
        
        'ar': """🤖 **استخدام البوت**

**الأوامر:**
/start - بدء البوت
/language - تغيير اللغة
/prompts - روابط المحفزات
/help - عرض هذه الرسالة

**الأزرار:**
• احصل على المحفزات - عرض المحفزات
• قناتنا - انضم إلى قناتنا الرسمية
• مساعدة - رسالة المساعدة
• تغيير اللغة - تغيير تفضيل اللغة"""
    }
    
    buttons = [[InlineKeyboardButton("◀️ Geri", callback_data="main_menu")]]
    keyboard = InlineKeyboardMarkup(buttons)
    
    text = help_texts.get(language, help_texts['en'])
    
    if edit_message:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

# Dil değiştirme
async def change_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dil değiştirme menüsü"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        edit_message = True
    else:
        edit_message = False
    
    buttons = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇯 کوردی", callback_data="lang_ku")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    text = "🌍 **Yeni dilinizi seçin / Select your new language:**"
    
    if edit_message:
        await query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)

# /prompts komutu
async def prompts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt linki göster"""
    user = update.effective_user
    language = get_user_language(user.id)
    
    messages = {
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
    
    button = InlineKeyboardButton(
        button_texts.get(language, button_texts['en']),
        url=PROMPT_LINK
    )
    
    keyboard = InlineKeyboardMarkup([[button]])
    
    await update.message.reply_text(
        messages.get(language, messages['en']),
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# /language komutu
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dil değiştirme komutu"""
    await change_language_command(update, context)

# /admin komutu
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin paneli"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Bu komut sadece adminler içindir.")
        return
    
    buttons = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="admin_quick_button")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        "👑 **Admin Paneli**\n\nAşağıdaki seçeneklerden birini seçin:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# İstatistikler
async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """İstatistikleri göster"""
    query = update.callback_query
    await query.answer()
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Toplam kullanıcı
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Dil dağılımı
        cursor.execute("SELECT language, COUNT(*) FROM users GROUP BY language")
        language_stats = cursor.fetchall()
        
        conn.close()
        
        stats_text = "📊 **Bot İstatistikleri**\n\n"
        stats_text += f"• Toplam Kullanıcı: {total_users}\n\n"
        stats_text += "**Dil Dağılımı:**\n"
        
        for lang, count in language_stats:
            lang_name = LANGUAGES.get(lang, lang)
            stats_text += f"  {lang_name}: {count}\n"
        
        buttons = [[InlineKeyboardButton("◀️ Geri", callback_data="admin_back")]]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"İstatistik hatası: {e}")
        await query.edit_message_text("❌ İstatistikler alınamadı.")

# Hızlı buton
async def admin_quick_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hızlı buton oluştur"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚡ **Hızlı Buton Oluşturma**\n\n"
        "Buton adı ve linkini şu şekilde gönderin:\n"
        "`Buton Adı https://ornek.link`\n\n"
        "Örnek:\n"
        "`Promtlar https://t.me/PrompttAI_bot`"
    )
    
    context.user_data['waiting_for_button'] = True

# Broadcast
async def admin_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Broadcast mesajı oluştur"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📢 **Duyuru Oluşturma**\n\n"
        "Duyuru metnini gönderin. Bu mesaj tüm kullanıcılara iletilecektir.\n\n"
        "İptal etmek için: /cancel"
    )
    
    context.user_data['waiting_for_broadcast'] = True

# Admin geri dönüş
async def admin_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin paneline geri dön"""
    query = update.callback_query
    await query.answer()
    
    buttons = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="admin_quick_button")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        "👑 **Admin Paneli**\n\nAşağıdaki seçeneklerden birini seçin:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# Admin mesaj işleme
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin mesajlarını işle"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    # Hızlı buton mesajı
    if context.user_data.get('waiting_for_button'):
        message_text = update.message.text
        
        # Basit parsing
        if 'http' in message_text:
            parts = message_text.split('http')
            if len(parts) >= 2:
                button_name = parts[0].strip()
                button_url = 'http' + parts[1].strip()
                
                # Tüm kullanıcılara gönder
                try:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id FROM users")
                    users = cursor.fetchall()
                    conn.close()
                    
                    # Buton oluştur
                    button = InlineKeyboardButton(button_name, url=button_url)
                    keyboard = InlineKeyboardMarkup([[button]])
                    
                    sent_count = 0
                    for user_row in users:
                        try:
                            await context.bot.send_message(
                                chat_id=user_row[0],
                                text="🔗 **Yeni bağlantı!**",
                                reply_markup=keyboard,
                                parse_mode=ParseMode.MARKDOWN
                            )
                            sent_count += 1
                        except:
                            continue
                    
                    await update.message.reply_text(
                        f"✅ Buton {sent_count} kullanıcıya gönderildi!\n\n"
                        f"**Buton:** {button_name}\n"
                        f"**URL:** {button_url}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
                except Exception as e:
                    await update.message.reply_text(f"❌ Hata: {e}")
        
        context.user_data.pop('waiting_for_button', None)
        return
    
    # Broadcast mesajı
    if context.user_data.get('waiting_for_broadcast'):
        message_text = update.message.text
        
        # Tüm kullanıcılara gönder
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()
            conn.close()
            
            sent_count = 0
            for user_row in users:
                try:
                    await context.bot.send_message(
                        chat_id=user_row[0],
                        text=message_text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent_count += 1
                except:
                    continue
            
            await update.message.reply_text(
                f"✅ Duyuru {sent_count} kullanıcıya gönderildi!",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}")
        
        context.user_data.pop('waiting_for_broadcast', None)
        return

# /cancel komutu
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """İşlem iptali"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    context.user_data.pop('waiting_for_button', None)
    context.user_data.pop('waiting_for_broadcast', None)
    
    await update.message.reply_text("❌ İşlem iptal edildi.")

# Hata handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hataları yakala"""
    logger.error(f"Hata: {context.error}")

# Ana fonksiyon
def main() -> None:
    """Botu başlat"""
    # Application oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Komut handler'ları
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("prompts", prompts_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Callback query handler'ları
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(change_language_command, pattern="^change_lang$"))
    
    # Admin callback handler'ları
    application.add_handler(CallbackQueryHandler(admin_stats_callback, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_quick_button_callback, pattern="^admin_quick_button$"))
    application.add_handler(CallbackQueryHandler(admin_broadcast_callback, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_back_callback, pattern="^admin_back$"))
    
    # Admin mesaj handler'ı
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
        handle_admin_message
    ))
    
    # Hata handler
    application.add_error_handler(error_handler)
    
    # Botu başlat
    logger.info("Bot başlatılıyor...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()
