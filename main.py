import logging
import sqlite3
import os
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import asyncio

# Basit logging ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token kontrolü
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN bulunamadı!")
    raise ValueError("BOT_TOKEN ayarlanmamış")

# Ayarlar
ADMIN_ID = 5541236874
CHANNEL_LINK = "https://t.me/+wet-9MZuj044ZGQy"
PROMPT_LINK = "https://t.me/PrompttAI_bot/Prompts"

# Database
DB_NAME = "bot_database.db"

def init_db():
    """Basit veritabanı başlatma"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Sadece gerekli tablolar
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (user_id INTEGER PRIMARY KEY, 
                     lang TEXT DEFAULT 'en',
                     joined_date DATE DEFAULT CURRENT_DATE,
                     banned INTEGER DEFAULT 0)''')
        
        conn.commit()
        conn.close()
        logger.info("Database başlatıldı")
    except Exception as e:
        logger.error(f"Database hatası: {e}")

init_db()

# Dil sistemi
LANGUAGES = {
    'tr': {'flag': '🇹🇷', 'name': 'Türkçe'},
    'en': {'flag': '🇬🇧', 'name': 'English'},
    'ku': {'flag': '🇹🇯', 'name': 'کوردی'},
    'ar': {'flag': '🇸🇦', 'name': 'العربية'}
}

def get_user_lang(user_id: int) -> str:
    """Kullanıcı dilini getir"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 'en'
    except:
        return 'en'

def save_user_lang(user_id: int, lang: str):
    """Kullanıcı dilini kaydet"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        today = date.today().isoformat()
        c.execute("""
            INSERT OR REPLACE INTO users (user_id, lang, joined_date) 
            VALUES (?, ?, ?)
        """, (user_id, lang, today))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Kullanıcı kaydetme hatası: {e}")

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botu başlat"""
    user = update.effective_user
    logger.info(f"Start: {user.id}")
    
    # Dil seçim ekranı
    keyboard = []
    for code, info in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"lang_{code}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 **Please choose your language / Lütfen dilinizi seçin:**",
        reply_markup=reply_markup
    )

# Dil seçimi
async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dil seçim işlemi"""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.split('_')[1]
    user_id = query.from_user.id
    
    # Dil kaydet
    save_user_lang(user_id, lang_code)
    
    # Hoşgeldin mesajı gönder
    await send_welcome(user_id, context.bot, lang_code)

async def send_welcome(user_id: int, bot, lang: str):
    """Hoşgeldin menüsü"""
    welcome_texts = {
        'tr': "🤖 **Hoş geldin!**\n\nAşağıdaki butonları kullanabilirsin:",
        'en': "🤖 **Welcome!**\n\nYou can use the buttons below:",
        'ku': "🤖 **بەخێربێیت!**\n\nدەتوانیت ئەم دوگمانەی خوارەوە بەکاربهێنیت:",
        'ar': "🤖 **أهلاً بك!**\n\nيمكنك استخدام الأزرار أدناه:"
    }
    
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
                callback_data="help"
            ),
            InlineKeyboardButton(
                button_texts['language'][lang],
                callback_data="change_lang"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=welcome_texts[lang],
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Hoşgeldin gönderme hatası: {e}")

# Yardım komutu
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım menüsü"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id
    
    user_lang = get_user_lang(user_id)
    
    help_texts = {
        'tr': """🤖 **Bot Kullanımı**

**Komutlar:**
• /start - Botu başlat
• /leng - Dil değiştir
• /app - Prompt linki
• /help - Yardım

**Butonlar:**
• Prompt Alma - Promptları görüntüle
• Kanalımız - Kanalımıza katıl
• Yardım - Bu mesajı göster
• Dil Değiştir - Dil tercihini değiştir""",
        'en': """🤖 **Bot Usage**

**Commands:**
• /start - Start bot
• /leng - Change language
• /app - Prompt link
• /help - Help

**Buttons:**
• Get Prompts - View prompts
• Our Channel - Join our channel
• Help - Show this message
• Change Language - Change language preference""",
        'ku': """🤖 **بەکارهێنانی بۆت**

**فەرمانەکان:**
• /start - بۆت دەستپێبکە
• /leng - زمان بگۆڕە
• /app - لینکی پرۆمپت
• /help - یارمەتی

**دوگمەکان:**
• پرۆمپت وەرگرن - پرۆمپتەکان ببینە
• کەناڵەکەمان - بچۆ بۆ کەناڵەکەمان
• یارمەتی - ئەم پەیامە پیشان بدە
• زمان بگۆڕە - هەڵبژاردنی زمان بگۆڕە""",
        'ar': """🤖 **استخدام البوت**

**الأوامر:**
• /start - بدء البوت
• /leng - تغيير اللغة
• /app - رابط المحفزات
• /help - مساعدة

**الأزرار:**
• احصل على المحفزات - عرض المحفزات
• قناتنا - انضم إلى قناتنا
• مساعدة - عرض هذه الرسالة
• تغيير اللغة - تغيير تفضيل اللغة"""
    }
    
    keyboard = [[InlineKeyboardButton("◀️ Geri", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = help_texts.get(user_lang, help_texts['en'])
    
    if update.callback_query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

# Geri butonu
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ana menüye dön"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    
    await send_welcome(user_id, context.bot, user_lang)

# Dil değiştirme
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dil değiştir"""
    user = update.effective_user
    
    keyboard = []
    for code, info in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{info['flag']} {info['name']}",
            callback_data=f"lang_{code}"
        )])
    
    user_lang = get_user_lang(user.id)
    messages = {
        'tr': '🌍 **Yeni dil seçin:**',
        'en': '🌍 **Choose new language:**',
        'ku': '🌍 **زمانێکی نوێ هەڵبژێرە:**',
        'ar': '🌍 **اختر لغة جديدة:**'
    }
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            messages.get(user_lang, messages['en']),
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            messages.get(user_lang, messages['en']),
            reply_markup=reply_markup
        )

# /app komutu
async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt linki"""
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
    """Dil değiştirme komutu"""
    await change_language(update, context)

# /admin komutu
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin paneli"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece adminler içindir.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="broadcast")],
        [InlineKeyboardButton("⚡ Hızlı Buton", callback_data="quickbtn")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="stats")],
        [InlineKeyboardButton("🚫 Kullanıcı Banla", callback_data="ban")],
        [InlineKeyboardButton("✅ Kullanıcı Ban Kaldır", callback_data="unban")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👑 **Admin Paneli**",
        reply_markup=reply_markup
    )

# Hızlı buton
async def quick_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hızlı buton oluştur"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚡ **Hızlı Buton Oluştur**\n\n"
        "Buton adı ve linkini şu şekilde gönderin:\n"
        "`Buton Adı https://link.com`\n\n"
        "Örnek:\n"
        "`Promptlar https://t.me/PrompttAI_bot`"
    )
    
    context.user_data['waiting_button'] = True

# Hızlı buton mesajı
async def handle_button_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hızlı buton mesajını işle"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if not context.user_data.get('waiting_button'):
        return
    
    message = update.message.text.strip()
    
    # Basit URL kontrolü
    if 'http' in message:
        parts = message.split('http')
        if len(parts) >= 2:
            button_name = parts[0].strip()
            button_url = 'http' + parts[1].strip()
            
            # Tüm kullanıcıları al
            try:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("SELECT user_id FROM users WHERE banned=0")
                users = c.fetchall()
                conn.close()
                
                # Buton oluştur
                keyboard = [[InlineKeyboardButton(button_name, url=button_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                success = 0
                for user_row in users:
                    try:
                        await context.bot.send_message(
                            chat_id=user_row[0],
                            text="🔗 **Yeni bağlantı!**",
                            reply_markup=reply_markup
                        )
                        success += 1
                        await asyncio.sleep(0.1)
                    except:
                        continue
                
                await update.message.reply_text(
                    f"✅ Buton {success} kullanıcıya gönderildi!\n"
                    f"Adı: {button_name}\n"
                    f"URL: {button_url}"
                )
                
            except Exception as e:
                logger.error(f"Buton gönderme hatası: {e}")
                await update.message.reply_text(f"❌ Hata: {e}")
            
            context.user_data.pop('waiting_button', None)
            return
    
    await update.message.reply_text("❌ Geçersiz format! Örnek: `Promptlar https://t.me/link`")

# İstatistikler
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İstatistikleri göster"""
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
        
        stats_text = f"📊 **İstatistikler**\n\n"
        stats_text += f"• Toplam Kullanıcı: {total}\n"
        stats_text += f"• Banlı Kullanıcı: {banned}\n\n"
        stats_text += "**Dil Dağılımı:**\n"
        
        for lang, count in langs:
            lang_name = LANGUAGES.get(lang, {}).get('name', lang)
            stats_text += f"  {LANGUAGES.get(lang, {}).get('flag', '')} {lang_name}: {count}\n"
        
        await query.edit_message_text(stats_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"İstatistik hatası: {e}")
        await query.edit_message_text("❌ İstatistikler alınamadı")

# Ban/Unban
async def ban_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban menüsü"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Banlamak için: `/ban user_id`\nÖrnek: `/ban 123456789`")

async def unban_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban menüsü"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Ban kaldırmak için: `/unban user_id`\nÖrnek: `/unban 123456789`")

# Broadcast
async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast menüsü"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📢 **Duyuru Gönder**\n\n"
        "Duyuru metnini gönderin. Tüm kullanıcılara iletilecektir.\n"
        "İptal için: /cancel"
    )
    context.user_data['waiting_broadcast'] = True

# Broadcast mesajı
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast mesajını işle"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    if not context.user_data.get('waiting_broadcast'):
        return
    
    message = update.message.text
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE banned=0")
        users = c.fetchall()
        conn.close()
        
        success = 0
        for user_row in users:
            try:
                await context.bot.send_message(
                    chat_id=user_row[0],
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                success += 1
                await asyncio.sleep(0.1)
            except:
                continue
        
        await update.message.reply_text(f"✅ Duyuru {success} kullanıcıya gönderildi!")
        
    except Exception as e:
        logger.error(f"Broadcast hatası: {e}")
        await update.message.reply_text(f"❌ Hata: {e}")
    
    context.user_data.pop('waiting_broadcast', None)

# /cancel komutu
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İşlem iptal"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    
    context.user_data.pop('waiting_button', None)
    context.user_data.pop('waiting_broadcast', None)
    
    await update.message.reply_text("❌ İşlem iptal edildi.")

# Hata handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hataları yakala"""
    logger.error(f"Hata: {context.error}")
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Bot hatası:\n{context.error}"
        )
    except:
        pass

# Ana fonksiyon
def main():
    """Botu başlat"""
    try:
        # Application oluştur
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Komutlar
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("leng", leng_command))
        application.add_handler(CommandHandler("app", app_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("admin", admin_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        
        # Callback'ler
        application.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back$"))
        application.add_handler(CallbackQueryHandler(change_language, pattern="^change_lang$"))
        application.add_handler(CallbackQueryHandler(quick_button, pattern="^quickbtn$"))
        application.add_handler(CallbackQueryHandler(show_stats, pattern="^stats$"))
        application.add_handler(CallbackQueryHandler(ban_menu, pattern="^ban$"))
        application.add_handler(CallbackQueryHandler(unban_menu, pattern="^unban$"))
        application.add_handler(CallbackQueryHandler(broadcast_menu, pattern="^broadcast$"))
        
        # Mesaj handler'ları
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
            handle_admin_messages
        ))
        
        # Hata handler
        application.add_error_handler(error_handler)
        
        # Botu başlat
        logger.info("Bot başlatılıyor...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"Bot başlatma hatası: {e}")

if __name__ == '__main__':
    main()
