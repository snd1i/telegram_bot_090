import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from telegram.error import BadRequest

# Kendi dosyalarımızı import ediyoruz
import config
from database import Database, BannedUsers
from messages import get_message, LANGUAGES

# Log ayarı
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Veritabanı
db = Database()
banned_users = BannedUsers()

# ============ YARDIMCI FONKSİYONLAR ============
async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Kullanıcı kanalda mı kontrol et"""
    try:
        member = await context.bot.get_chat_member(
            chat_id=config.FORCE_CHANNEL,
            user_id=user_id
        )
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_owner(user_id: int) -> bool:
    """Kullanıcı owner mı kontrol et"""
    return user_id == config.OWNER_ID

def get_user_language(user_id):
    """Kullanıcının dilini getir"""
    user = db.get_user(user_id)
    if user:
        return user[4]  # language column
    return 'tr'  # Varsayılan Türkçe

# ============ /start KOMUTU ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Ban kontrolü
    if banned_users.is_banned(user_id):
        await update.message.reply_text("🚫 Bu botu kullanma izniniz yok.")
        return
    
    # Kullanıcıyı kaydet
    db.add_user(user_id, user.username, user.first_name, user.last_name or "")
    db.update_last_active(user_id)
    
    # Kullanıcıyı getir
    user_data = db.get_user(user_id)
    
    # İlk kez mi geliyor? (language yoksa veya 'tr' ise)
    if not user_data or user_data[4] == 'tr':
        # DİL SEÇİMİ GÖSTER
        keyboard = []
        row = []
        for lang_code, lang_info in LANGUAGES.items():
            button = InlineKeyboardButton(
                f"{lang_info['flag']} {lang_info['name']}",
                callback_data=f"lang_{lang_code}"
            )
            row.append(button)
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Welcome! / Hoşgeldiniz! / بەخێربێیت!\n\n"
            "🌍 **Please select your language:**\n"
            "**Lütfen dilinizi seçin:**\n"
            "**تکایە زمانێک هەڵبژێرە:**",
            reply_markup=reply_markup
        )
        return
    
    # Zaten dil seçmiş, abonelik kontrolü yap
    user_lang = user_data[4]
    is_subscribed = await is_user_subscribed(user_id, context)
    
    if is_subscribed:
        # Zaten abone, hoşgeldin mesajı (sadece ilk kez)
        if config.WELCOME_ACTIVE and user_data[6] == 0:  # is_subscribed = 0
            welcome_keyboard = [
                [InlineKeyboardButton("📢 Our Channel", url=f"https://t.me/{config.FORCE_CHANNEL[1:]}")],
                [InlineKeyboardButton("🤖 Prompt Library", callback_data="prompts")],
                [InlineKeyboardButton("🌐 Change Language", callback_data="change_lang")]
            ]
            reply_markup = InlineKeyboardMarkup(welcome_keyboard)
            
            await update.message.reply_text(
                f"🎉 **{get_message(user_lang, 'welcome_back')}**\n\n"
                f"✅ **{get_message(user_lang, 'already_sub')}**\n\n"
                f"🤖 Bot features are ready to use!\n"
                f"Use /help for commands.",
                reply_markup=reply_markup
            )
            db.update_subscription(user_id, 1)
        else:
            # Sessiz mod - sadece butonlar
            pass
    else:
        # ABONE OLMAYANLAR
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{config.FORCE_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{get_message(user_lang, 'force_sub')}\n"
            f"{config.FORCE_CHANNEL}",
            reply_markup=reply_markup
        )

# ============ BUTON İŞLEMLERİ ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Ban kontrolü
    if banned_users.is_banned(user_id):
        await query.edit_message_text("🚫 Access denied.")
        return
    
    data = query.data
    
    # DİL SEÇİMİ
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        db.update_user_language(user_id, lang_code)
        user_lang = lang_code
        
        # Abonelik kontrolü
        is_subscribed = await is_user_subscribed(user_id, context)
        
        if is_subscribed:
            # Zaten abone, direkt hoşgeldin
            db.update_subscription(user_id, 1)
            
            welcome_keyboard = [
                [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{config.FORCE_CHANNEL[1:]}")],
                [InlineKeyboardButton("🤖 Prompts", callback_data="prompts")],
                [InlineKeyboardButton("🌐 Language", callback_data="change_lang")]
            ]
            reply_markup = InlineKeyboardMarkup(welcome_keyboard)
            
            await query.edit_message_text(
                f"✅ **{get_message(user_lang, 'sub_success')}**\n\n"
                f"🎉 Welcome to the bot!\n"
                f"Your language: {LANGUAGES[lang_code]['flag']} {LANGUAGES[lang_code]['name']}\n\n"
                f"Use /help for commands.",
                reply_markup=reply_markup
            )
        else:
            # Abone değil, kanala yönlendir
            keyboard = [
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{config.FORCE_CHANNEL[1:]}")],
                [InlineKeyboardButton("✅ Check Subscription", callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{get_message(user_lang, 'force_sub')}\n"
                f"{config.FORCE_CHANNEL}",
                reply_markup=reply_markup
            )
    
    # ABONE KONTROLÜ
    elif data == "check_sub":
        user_lang = get_user_language(user_id)
        is_subscribed = await is_user_subscribed(user_id, context)
        
        if is_subscribed:
            db.update_subscription(user_id, 1)
            
            welcome_keyboard = [
                [InlineKeyboardButton("📢 Channel", url=f"https://t.me/{config.FORCE_CHANNEL[1:]}")],
                [InlineKeyboardButton("🤖 Prompts", callback_data="prompts")],
                [InlineKeyboardButton("🌐 Language", callback_data="change_lang")]
            ]
            reply_markup = InlineKeyboardMarkup(welcome_keyboard)
            
            await query.edit_message_text(
                f"✅ **{get_message(user_lang, 'sub_success')}**\n\n"
                f"🤖 Bot is ready!\n"
                f"Use /help for commands.",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                f"❌ {get_message(user_lang, 'sub_required')}\n"
                f"{config.FORCE_CHANNEL}"
            )
    
    # DİL DEĞİŞTİRME
    elif data == "change_lang":
        keyboard = []
        row = []
        for lang_code, lang_info in LANGUAGES.items():
            button = InlineKeyboardButton(
                f"{lang_info['flag']} {lang_info['name']}",
                callback_data=f"setlang_{lang_code}"
            )
            row.append(button)
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌍 Select your language:",
            reply_markup=reply_markup
        )
    
    # DİL AYARLA
    elif data.startswith("setlang_"):
        lang_code = data.split("_")[1]
        db.update_user_language(user_id, lang_code)
        await query.edit_message_text(
            f"✅ Language changed to {LANGUAGES[lang_code]['flag']} {LANGUAGES[lang_code]['name']}"
        )
    
    # PROMPT LİBRARY
    elif data == "prompts":
        user_lang = get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton("💬 ChatGPT Prompts", callback_data="chatgpt_prompts")],
            [InlineKeyboardButton("🎨 DALL-E Prompts", callback_data="dalle_prompts")],
            [InlineKeyboardButton("📝 Writing Prompts", callback_data="writing_prompts")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🤖 **Prompt Library**\n\n"
            "Select a category:",
            reply_markup=reply_markup
        )

# ============ YÖNETİCİ KOMUTLARI ============

# /band - Kullanıcı engelle
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /band @username")
        return
    
    username = context.args[0].replace("@", "")
    banned_users.add(username)
    
    await update.message.reply_text(f"✅ User @{username} has been banned.")

# /unband - Engeli kaldır
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unband @username")
        return
    
    username = context.args[0].replace("@", "")
    banned_users.remove(username)
    
    await update.message.reply_text(f"✅ User @{username} has been unbanned.")

# /bandlist - Engellenenler listesi
async def ban_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    banned_list = banned_users.load()
    if not banned_list:
        await update.message.reply_text("No banned users.")
        return
    
    users_text = "\n".join([f"• @{user}" for user in banned_list])
    await update.message.reply_text(f"🚫 **Banned Users:**\n\n{users_text}")

# /user - İstatistikler
async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    daily = db.get_user_count("daily")
    weekly = db.get_user_count("weekly")
    monthly = db.get_user_count("monthly")
    total = db.get_user_count("all")
    
    stats_text = f"""
📊 **Bot Statistics:**

📈 Daily New Users: {daily}
📈 Weekly New Users: {weekly}
📈 Monthly New Users: {monthly}
👥 Total Users: {total}

✅ Active Features:
• Bot Status: {'🟢 Active' if config.BOT_ACTIVE else '🔴 Paused'}
• Welcome Msg: {'🟢 Active' if config.WELCOME_ACTIVE else '🔴 Disabled'}
• Force Channel: {config.FORCE_CHANNEL}
    """
    
    await update.message.reply_text(stats_text)

# /settings - Bot ayarları
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("🟢 Bot Active", callback_data="toggle_bot")],
        [InlineKeyboardButton("👋 Welcome Msg", callback_data="toggle_welcome")],
        [InlineKeyboardButton("📢 Change Channel", callback_data="change_channel")],
        [InlineKeyboardButton("📝 Edit Messages", callback_data="edit_messages")],
        [InlineKeyboardButton("➕ Add Command", callback_data="add_command")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ **Bot Settings Panel**\n\n"
        "Select an option to modify:",
        reply_markup=reply_markup
    )

# /help - Yardım
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_lang = get_user_language(user_id)
    
    help_text = get_message(user_lang, 'help')
    await update.message.reply_text(help_text, parse_mode='Markdown')

# /lang - Dil değiştir
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = []
    row = []
    for lang_code, lang_info in LANGUAGES.items():
        button = InlineKeyboardButton(
            f"{lang_info['flag']} {lang_info['name']}",
            callback_data=f"setlang_{lang_code}"
        )
        row.append(button)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌍 Select your language:",
        reply_markup=reply_markup
    )

# /app - App bilgisi
async def app_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = get_user_language(update.effective_user.id)
    
    await update.message.reply_text(
        "🤖 **Prompt Assistant Bot**\n\n"
        "Version: 1.0.0\n"
        "Creator: @snd1i\n\n"
        "Features:\n"
        "• Multi-language support\n"
        "• Prompt library\n"
        "• Channel subscription\n"
        "• User management"
    )

# ============ ANA FONKSİYON ============
def main():
    if not config.BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found!")
        return
    
    # Bot uygulamasını oluştur
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # KOMUTLARI EKLE
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lang", change_language))
    application.add_handler(CommandHandler("app", app_info))
    
    # YÖNETİCİ KOMUTLARI
    application.add_handler(CommandHandler("band", ban_user))
    application.add_handler(CommandHandler("unband", unban_user))
    application.add_handler(CommandHandler("bandlist", ban_list))
    application.add_handler(CommandHandler("user", user_stats))
    application.add_handler(CommandHandler("settings", settings))
    
    # BUTON İŞLEYİCİ
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # BOTU BAŞLAT
    logger.info("🤖 Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
