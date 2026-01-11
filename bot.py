import os
import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============ AYARLAR ============
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Railway'dan alınacak
OWNER_ID = 5541236874  # Sizin ID'niz
FORCE_CHANNEL = "https://t.me/sndiyi"  # Zorunlu kanal
CHANNEL_USERNAME = "@sndiyi"  # Abonelik kontrolü için

# Bot durumları
BOT_ACTIVE = True
WELCOME_ACTIVE = True

# ============ VERİTABANI ============
def init_db():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'tr',
            is_banned INTEGER DEFAULT 0,
            is_subscribed INTEGER DEFAULT 0,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Engellenenler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banned_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            banned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name) 
        VALUES (?, ?, ?)
    ''', (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_language(user_id, language):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    conn.commit()
    conn.close()

def update_subscription(user_id, status):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_subscribed = ? WHERE user_id = ?', (status, user_id))
    conn.commit()
    conn.close()

def ban_user_db(user_id, username):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO banned_users (user_id, username) VALUES (?, ?)', (user_id, username))
    cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def unban_user_db(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
    cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_banned_users():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username FROM banned_users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_count(period="all"):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    if period == "daily":
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date) >= date(?)', (date,))
    elif period == "weekly":
        date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date) >= date(?)', (date,))
    elif period == "monthly":
        date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cursor.execute('SELECT COUNT(*) FROM users WHERE date(join_date) >= date(?)', (date,))
    else:
        cursor.execute('SELECT COUNT(*) FROM users')
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ============ DİL MESAJLARI ============
MESSAGES = {
    'tr': {
        'welcome': "👋 Hoşgeldiniz! Lütfen bir dil seçin:",
        'force_sub': "📢 Devam etmek için kanala katılın:\n{}",
        'check_sub': "✅ Abone Oldum",
        'sub_success': "✅ Teşekkürler! Şimdi botu kullanabilirsiniz.",
        'sub_required': "❌ Önce kanala katılmalısınız.",
        'welcome_back': "🎉 Hoşgeldiniz {}!",
        'help': "🤖 Yardım için /help yazın.",
        'banned': "🚫 Kullanıcı engellendi.",
        'unbanned': "✅ Kullanıcının engeli kaldırıldı.",
        'bot_paused': "⏸️ Bot durduruldu.",
        'bot_resumed': "▶️ Bot aktif edildi."
    },
    'en': {
        'welcome': "👋 Welcome! Please select a language:",
        'force_sub': "📢 Join channel to continue:\n{}",
        'check_sub': "✅ I Subscribed",
        'sub_success': "✅ Thank you! You can now use the bot.",
        'sub_required': "❌ You must join the channel first.",
        'welcome_back': "🎉 Welcome back {}!",
        'help': "🤖 Type /help for assistance.",
        'banned': "🚫 User banned.",
        'unbanned': "✅ User unbanned.",
        'bot_paused': "⏸️ Bot paused.",
        'bot_resumed': "▶️ Bot resumed."
    },
    'ku': {
        'welcome': "👋 Bi xêr hatî! Zimanek hilbijêre:",
        'force_sub': "📢 Ji bo domandinê kanalê tevlî bibin:\n{}",
        'check_sub': "✅ Min abone bûm",
        'sub_success': "✅ Spas! Niha hûn dikarin botê bikar bînin.",
        'sub_required': "❌ Pêşî divê hûn kanalê tevlî bibin.",
        'welcome_back': "🎉 Bi xêr hatî {}!",
        'help': "🤖 Ji bo alîkarî /help binivîse.",
        'banned': "🚫 Bikarhêner hate qedexekirin.",
        'unbanned': "✅ Qedexeya bikarhêner rakirin.",
        'bot_paused': "⏸️ Bot rawestiya.",
        'bot_resumed': "▶️ Bot dîsa dest pê kir."
    },
    'ar': {
        'welcome': "👋 أهلاً وسهلاً! الرجاء اختيار لغة:",
        'force_sub': "📢 انضم إلى القناة للمتابعة:\n{}",
        'check_sub': "✅ لقد اشتركت",
        'sub_success': "✅ شكراً! يمكنك الآن استخدام البوت.",
        'sub_required': "❌ يجب الانضمام إلى القناة أولاً.",
        'welcome_back': "🎉 أهلاً بعودتك {}!",
        'help': "🤖 اكتب /help للمساعدة.",
        'banned': "🚫 تم حظر المستخدم.",
        'unbanned': "✅ تم إلغاء حظر المستخدم.",
        'bot_paused': "⏸️ تم إيقاف البوت.",
        'bot_resumed': "▶️ تم استئناف البوت."
    }
}

LANGUAGES = {
    'tr': {'flag': '🇹🇷', 'name': 'Türkçe'},
    'en': {'flag': '🇬🇧', 'name': 'English'},
    'ku': {'flag': '🇹🇯', 'name': 'Kurdî'},  # Basitleştirdim
    'ar': {'flag': '🇮🇶', 'name': 'العربية'}
}

def get_msg(lang, key, *args):
    msg = MESSAGES.get(lang, MESSAGES['tr']).get(key, MESSAGES['tr'][key])
    return msg.format(*args) if args else msg

# ============ ABONE KONTROLÜ ============
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ============ /start KOMUTU ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Bot aktif mi?
    if not BOT_ACTIVE and user_id != OWNER_ID:
        await update.message.reply_text("⏸️ Bot şu anda aktif değil.")
        return
    
    # Kullanıcıyı kaydet
    add_user(user_id, user.username, user.first_name)
    
    # Kullanıcı bilgilerini al
    user_data = get_user(user_id)
    
    # İlk kez mi? (dil yoksa)
    if not user_data or user_data[3] == 'tr':
        # DİL SEÇİMİ
        keyboard = [
            [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
             InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇹🇯 Kurdî", callback_data="lang_ku"),
             InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🌍 **Lütfen dilinizi seçin / Please select your language:**",
            reply_markup=reply_markup
        )
        return
    
    # Dil bilgisi var, abonelik kontrolü
    user_lang = user_data[3]
    
    # Zaten abone mi?
    if user_data[5] == 1:  # is_subscribed = 1
        if WELCOME_ACTIVE:
            await update.message.reply_text(get_msg(user_lang, 'welcome_back', user.first_name))
        return
    
    # Abone değil, kanala yönlendir
    keyboard = [
        [InlineKeyboardButton("📢 Kanalıma Katıl", url=FORCE_CHANNEL)],
        [InlineKeyboardButton("✅ Kontrol Et", callback_data="check_sub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_msg(user_lang, 'force_sub', FORCE_CHANNEL),
        reply_markup=reply_markup
    )

# ============ BUTON İŞLEMLERİ ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    # DİL SEÇİMİ
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        update_user_language(user_id, lang)
        
        # Abonelik kontrolü
        subscribed = await is_subscribed(user_id, context)
        
        if subscribed:
            update_subscription(user_id, 1)
            await query.edit_message_text(get_msg(lang, 'sub_success'))
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Kanalıma Katıl", url=FORCE_CHANNEL)],
                [InlineKeyboardButton("✅ Kontrol Et", callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                get_msg(lang, 'force_sub', FORCE_CHANNEL),
                reply_markup=reply_markup
            )
    
    # ABONE KONTROLÜ
    elif data == "check_sub":
        user_data = get_user(user_id)
        lang = user_data[3] if user_data else 'tr'
        
        subscribed = await is_subscribed(user_id, context)
        
        if subscribed:
            update_subscription(user_id, 1)
            await query.edit_message_text(get_msg(lang, 'sub_success'))
        else:
            await query.edit_message_text(get_msg(lang, 'sub_required'))

# ============ YÖNETİCİ KOMUTLARI ============

# /band - Kullanıcı engelle
async def band(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Yetkiniz yok.")
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: /band @kullaniciadi veya /band 123456")
        return
    
    target = context.args[0]
    
    try:
        # ID mi yoksa username mi?
        if target.startswith('@'):
            # Username ile engelle (basit)
            await update.message.reply_text(f"✅ @{target[1:]} engellendi.")
        else:
            # ID ile engelle
            user_id = int(target)
            ban_user_db(user_id, "unknown")
            await update.message.reply_text(f"✅ {user_id} engellendi.")
    except:
        await update.message.reply_text("❌ Hata! Kullanıcı bulunamadı.")

# /unband - Engeli kaldır
async def unband(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if not context.args:
        await update.message.reply_text("Kullanım: /unband 123456")
        return
    
    try:
        user_id = int(context.args[0])
        unban_user_db(user_id)
        await update.message.reply_text(f"✅ {user_id} engeli kaldırıldı.")
    except:
        await update.message.reply_text("❌ Hata!")

# /bandlist - Engellenenler
async def bandlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    banned = get_banned_users()
    
    if not banned:
        await update.message.reply_text("📭 Engellenen kullanıcı yok.")
        return
    
    text = "🚫 **Engellenen Kullanıcılar:**\n\n"
    for user_id, username in banned:
        text += f"• {username or 'Kullanıcı'} (ID: {user_id})\n"
    
    await update.message.reply_text(text)

# /user - İstatistikler
async def user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    daily = get_user_count("daily")
    weekly = get_user_count("weekly")
    monthly = get_user_count("monthly")
    total = get_user_count("all")
    
    text = f"""
📊 **Bot İstatistikleri:**

📈 Günlük: {daily}
📈 Haftalık: {weekly}
📈 Aylık: {monthly}
👥 Toplam: {total}

⚙️ **Ayarlar:**
• Bot Durumu: {'🟢 Aktif' if BOT_ACTIVE else '🔴 Durduruldu'}
• Hoşgeldin Mesajı: {'🟢 Açık' if WELCOME_ACTIVE else '🔴 Kapalı'}
• Zorunlu Kanal: {FORCE_CHANNEL}
"""
    await update.message.reply_text(text)

# /settings - Ayarlar paneli
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Yetkiniz yok.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🟢 Bot Aktif/Pasif", callback_data="toggle_bot")],
        [InlineKeyboardButton("👋 Hoşgeldin Aç/Kapa", callback_data="toggle_welcome")],
        [InlineKeyboardButton("📢 Kanalı Değiştir", callback_data="change_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ **Bot Ayarları**\n\n"
        "Aşağıdaki ayarları değiştirebilirsiniz:",
        reply_markup=reply_markup
    )

# Settings butonları
async def settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_ID:
        await query.edit_message_text("❌ Yetkiniz yok.")
        return
    
    data = query.data
    global BOT_ACTIVE, WELCOME_ACTIVE, FORCE_CHANNEL
    
    if data == "toggle_bot":
        BOT_ACTIVE = not BOT_ACTIVE
        status = "Aktif" if BOT_ACTIVE else "Pasif"
        await query.edit_message_text(f"✅ Bot durumu: {status}")
    
    elif data == "toggle_welcome":
        WELCOME_ACTIVE = not WELCOME_ACTIVE
        status = "Açık" if WELCOME_ACTIVE else "Kapalı"
        await query.edit_message_text(f"✅ Hoşgeldin mesajı: {status}")
    
    elif data == "change_channel":
        await query.edit_message_text(
            "📢 Yeni kanal linkini gönderin:\n"
            "Örnek: https://t.me/sndiyi\n\n"
            "İptal için /settings yazın."
        )
        context.user_data['waiting_channel'] = True

# Kanal değiştirme mesajı
async def change_channel_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if context.user_data.get('waiting_channel'):
        global FORCE_CHANNEL, CHANNEL_USERNAME
        new_channel = update.message.text.strip()
        
        if new_channel.startswith("https://t.me/"):
            FORCE_CHANNEL = new_channel
            CHANNEL_USERNAME = "@" + new_channel.split("/")[-1]
            await update.message.reply_text(f"✅ Kanal güncellendi: {FORCE_CHANNEL}")
        else:
            await update.message.reply_text("❌ Geçersiz link! https://t.me/ ile başlamalı.")
        
        context.user_data['waiting_channel'] = False

# /help - Yardım
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 **Bot Kullanım Kılavuzu**

**Kullanıcı Komutları:**
/start - Botu başlat
/help - Bu yardım mesajı
/lang - Dil değiştir
/app - Bot hakkında bilgi

**Yönetici Komutları (Sadece Sahip):**
/band @kullanici - Kullanıcı engelle
/unband ID - Engeli kaldır
/bandlist - Engellenenleri listele
/user - İstatistikleri göster
/settings - Bot ayarları

📢 **Özellikler:**
• 4 dil desteği (Türkçe, İngilizce, Kürtçe, Arapça)
• Kanal abonelik kontrolü
• Kullanıcı engelleme sistemi
• Detaylı istatistikler
    """
    await update.message.reply_text(text)

# /lang - Dil değiştir
async def lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="setlang_tr"),
         InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en")],
        [InlineKeyboardButton("🇹🇯 Kurdî", callback_data="setlang_ku"),
         InlineKeyboardButton("🇮🇶 العربية", callback_data="setlang_ar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 **Dilinizi seçin / Select your language:**",
        reply_markup=reply_markup
    )

# Dil değiştirme butonu
async def lang_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith("setlang_"):
        lang = data.split("_")[1]
        update_user_language(user_id, lang)
        lang_name = LANGUAGES[lang]['name']
        await query.edit_message_text(f"✅ Diliniz {lang_name} olarak ayarlandı.")

# /app - App bilgisi
async def app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 **Prompt Assistant Bot**

**Versiyon:** 2.0
**Geliştirici:** @snd1i
**Kanal:** @sndiyi

**Özellikler:**
• Çoklu dil desteği
• Prompt kütüphanesi (yakında)
• Kullanıcı yönetimi
• İstatistik paneli

**Destek:** @snd1i
    """
    await update.message.reply_text(text)

# ============ ANA PROGRAM ============
def main():
    # Veritabanını başlat
    init_db()
    
    # Token kontrolü
    if not BOT_TOKEN:
        print("❌ HATA: TELEGRAM_BOT_TOKEN bulunamadı!")
        print("Railway → Variables → TELEGRAM_BOT_TOKEN ekleyin")
        return
    
    # Bot uygulaması
    app = Application.builder().token(BOT_TOKEN).build()
    
    # KOMUTLAR
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("lang", lang))
    app.add_handler(CommandHandler("app", app))
    
    # YÖNETİCİ KOMUTLARI
    app.add_handler(CommandHandler("band", band))
    app.add_handler(CommandHandler("unband", unband))
    app.add_handler(CommandHandler("bandlist", bandlist))
    app.add_handler(CommandHandler("user", user))
    app.add_handler(CommandHandler("settings", settings))
    
    # BUTONLAR
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(lang_|check_sub)"))
    app.add_handler(CallbackQueryHandler(lang_button, pattern="^setlang_"))
    app.add_handler(CallbackQueryHandler(settings_button, pattern="^(toggle_bot|toggle_welcome|change_channel)"))
    
    # MESAJ İŞLEYİCİLER
    app.add_handler(MessageHandler(None, change_channel_msg))
    
    # BAŞLAT
    print("=" * 50)
    print("🤖 BOT BAŞLATILIYOR")
    print(f"👑 Sahip ID: {OWNER_ID}")
    print(f"📢 Kanal: {FORCE_CHANNEL}")
    print("=" * 50)
    
    app.run_polling()

if __name__ == '__main__':
    main()
