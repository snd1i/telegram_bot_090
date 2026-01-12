# extensions/admin.py - SADECE PROFESYONEL DUYURU SİSTEMİ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
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
BROADCAST_TEXTS = {
    'ku': {
        'admin_only': "❌ تەنیا بەڕێوەبەر دەتوانێت ئەم فرمانە بەکاربهێنێت!",
        'panel_title': "📢 **ناردنی بڵاوکراوە**\n\nخوارەوە دوگمەیەک هەڵبژێرە:",
        'broadcast_created': "✅ بڵاوکراوە دروست کرا! ئێستا دەتوانیت:",
        'add_text': "📝 زیادکردنی دەق",
        'add_media': "🖼️ زیادکردنی وێنە/ڤیدیۆ",
        'add_button': "🔘 زیادکردنی دوگمە",
        'preview': "👁️ بینینی پێشوەخت",
        'send': "📤 ناردن بۆ هەموو کەس",
        'back': "🔙 گەڕانەوە",
        'cancel': "✖️ هەڵوەشاندنەوە",
        'enter_text': "📝 دەقی بڵاوکراوە بنووسە:",
        'text_added': "✅ دەق زیاد کرا!",
        'send_photo_video': "🖼️ وێنە یان ڤیدیۆ باربکە:",
        'media_added': "✅ وێنە/ڤیدیۆ زیاد کرا!",
        'enter_button_text': "🔘 دەقی دوگمە بنووسە:",
        'enter_button_url': "🔗 لینکی دوگمە بنووسە:",
        'button_added': "✅ دوگمە زیاد کرا!",
        'preview_title': "👁️ **پێشبینینی بڵاوکراوە**\n\n",
        'no_content': "⚠️ هیچ ناوەڕۆکێک نییە!",
        'sending': "🔄 ناردن...",
        'sent_success': "✅ بڵاوکراوە نێردرا بۆ {} کەس!",
        'sent_failed': "❌ بە {} کەس نەگەیشت.",
        'current_content': "📋 **ناوەڕۆکی ئێستا:**\n",
        'text_content': "📝 دەق: {}\n",
        'media_content': "🖼️ میدیا: {}",
        'buttons_content': "🔘 دوگمەکان: {}",
        'remove_last': "🗑️ سڕینەوەی دوایین",
        'clear_all': "🧹 پاککردنەوەی هەموو",
        'confirm_send': "⚠️ **دڵنیای لە ناردن؟**\n\nبڵاوکراوە بۆ هەموو کەس نێردرێت.\n\n{} کەس گەیشتەت.",
        'yes_send': "✅ بەڵێ، بنێرە",
        'no_cancel': "❌ نەخێر، هەڵبوەشێنە"
    },
    'en': {
        'admin_only': "❌ Only admin can use this command!",
        'panel_title': "📢 **Send Broadcast**\n\nSelect an option below:",
        'broadcast_created': "✅ Broadcast created! Now you can:",
        'add_text': "📝 Add Text",
        'add_media': "🖼️ Add Photo/Video",
        'add_button': "🔘 Add Button",
        'preview': "👁️ Preview",
        'send': "📤 Send to Everyone",
        'back': "🔙 Back",
        'cancel': "✖️ Cancel",
        'enter_text': "📝 Enter broadcast text:",
        'text_added': "✅ Text added!",
        'send_photo_video': "🖼️ Send photo or video:",
        'media_added': "✅ Photo/video added!",
        'enter_button_text': "🔘 Enter button text:",
        'enter_button_url': "🔗 Enter button URL:",
        'button_added': "✅ Button added!",
        'preview_title': "👁️ **Broadcast Preview**\n\n",
        'no_content': "⚠️ No content yet!",
        'sending': "🔄 Sending...",
        'sent_success': "✅ Broadcast sent to {} people!",
        'sent_failed': "❌ Failed to reach {} people.",
        'current_content': "📋 **Current Content:**\n",
        'text_content': "📝 Text: {}\n",
        'media_content': "🖼️ Media: {}",
        'buttons_content': "🔘 Buttons: {}",
        'remove_last': "🗑️ Remove Last",
        'clear_all': "🧹 Clear All",
        'confirm_send': "⚠️ **Confirm Send?**\n\nBroadcast will be sent to everyone.\n\n{} people will receive it.",
        'yes_send': "✅ Yes, Send",
        'no_cancel': "❌ No, Cancel"
    },
    'ar': {
        'admin_only': "❌ فقط المدير يمكنه استخدام هذا الأمر!",
        'panel_title': "📢 **إرسال بث**\n\nاختر خيارًا أدناه:",
        'broadcast_created': "✅ تم إنشاء البث! الآن يمكنك:",
        'add_text': "📝 إضافة نص",
        'add_media': "🖼️ إضافة صورة/فيديو",
        'add_button': "🔘 إضافة زر",
        'preview': "👁️ معاينة",
        'send': "📤 إرسال للجميع",
        'back': "🔙 رجوع",
        'cancel': "✖️ إلغاء",
        'enter_text': "📝 أدخل نص البث:",
        'text_added': "✅ تمت إضافة النص!",
        'send_photo_video': "🖼️ أرسل صورة أو فيديو:",
        'media_added': "✅ تمت إضافة الصورة/الفيديو!",
        'enter_button_text': "🔘 أدخل نص الزر:",
        'enter_button_url': "🔗 أدخل رابط الزر:",
        'button_added': "✅ تمت إضافة الزر!",
        'preview_title': "👁️ **معاينة البث**\n\n",
        'no_content': "⚠️ لا يوجد محتوى بعد!",
        'sending': "🔄 جاري الإرسال...",
        'sent_success': "✅ تم إرسال البث إلى {} شخص!",
        'sent_failed': "❌ فشل في الوصول إلى {} شخص.",
        'current_content': "📋 **المحتوى الحالي:**\n",
        'text_content': "📝 النص: {}\n",
        'media_content': "🖼️ الوسائط: {}",
        'buttons_content': "🔘 الأزرار: {}",
        'remove_last': "🗑️ حذف الأخير",
        'clear_all': "🧹 مسح الكل",
        'confirm_send': "⚠️ **تأكيد الإرسال؟**\n\nسيتم إرسال البث للجميع.\n\n{} شخص سيستلمه.",
        'yes_send': "✅ نعم، أرسل",
        'no_cancel': "❌ لا، ألغي"
    }
}

# ========== GLOBAL BROADCAST DATA ==========
# Her admin için broadcast verisi saklar
broadcast_sessions = {}

class BroadcastSession:
    """Broadcast oturumu yönetimi"""
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.text = None
        self.photo = None
        self.video = None
        self.buttons = []
        self.state = None  # 'waiting_text', 'waiting_media', 'waiting_button_text', 'waiting_button_url'
    
    def get_content_summary(self, lang='en'):
        """İçerik özetini getir"""
        texts = BROADCAST_TEXTS[lang]
        summary = texts['current_content']
        
        if self.text:
            summary += texts['text_content'].format(self.text[:50] + ("..." if len(self.text) > 50 else ""))
        
        if self.photo:
            summary += texts['media_content'].format("📷 Photo")
        elif self.video:
            summary += texts['media_content'].format("🎬 Video")
        
        if self.buttons:
            button_texts = [btn['text'] for btn in self.buttons]
            summary += texts['buttons_content'].format(", ".join(button_texts))
        
        if not self.text and not self.photo and not self.video:
            summary = texts['no_content']
        
        return summary
    
    def reset(self):
        """Oturumu sıfırla"""
        self.text = None
        self.photo = None
        self.video = None
        self.buttons = []
        self.state = None

def get_session(user_id):
    """Kullanıcı için broadcast oturumu al"""
    user_id_str = str(user_id)
    if user_id_str not in broadcast_sessions:
        broadcast_sessions[user_id_str] = BroadcastSession(user_id)
    return broadcast_sessions[user_id_str]

# ========== /settings KOMUTU ==========
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sadece broadcast sistemi"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        user_lang = get_user_lang(user_id)
        await update.message.reply_text(BROADCAST_TEXTS[user_lang]['admin_only'])
        return
    
    # Oturumu sıfırla
    session = get_session(user_id)
    session.reset()
    
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    # Ana broadcast paneli
    keyboard = [
        [InlineKeyboardButton(texts['add_text'], callback_data="broadcast_add_text")],
        [InlineKeyboardButton(texts['add_media'], callback_data="broadcast_add_media")],
        [InlineKeyboardButton(texts['add_button'], callback_data="broadcast_add_button")],
        [
            InlineKeyboardButton(texts['preview'], callback_data="broadcast_preview"),
            InlineKeyboardButton(texts['send'], callback_data="broadcast_confirm_send")
        ],
        [
            InlineKeyboardButton(texts['remove_last'], callback_data="broadcast_remove_last"),
            InlineKeyboardButton(texts['clear_all'], callback_data="broadcast_clear_all")
        ],
        [InlineKeyboardButton(texts['cancel'], callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        texts['panel_title'] + "\n\n" + session.get_content_summary(user_lang),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ========== METİN EKLEME ==========
async def add_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metin ekleme işlemi"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    session.state = 'waiting_text'
    
    await query.message.reply_text(texts['enter_text'])

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metin girdisini işle"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_text':
        return
    
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session.text = update.message.text
    session.state = None
    
    await update.message.reply_text(texts['text_added'])
    await show_broadcast_panel(update, context)

# ========== MEDİA EKLEME ==========
async def add_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Media ekleme işlemi"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    session.state = 'waiting_media'
    
    await query.message.reply_text(texts['send_photo_video'])

async def handle_media_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Media girdisini işle"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_media':
        return
    
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    if update.message.photo:
        session.photo = update.message.photo[-1].file_id
        session.video = None
    elif update.message.video:
        session.video = update.message.video.file_id
        session.photo = None
    
    # Eğer caption varsa, text olarak kaydet
    if update.message.caption:
        session.text = update.message.caption
    
    session.state = None
    
    await update.message.reply_text(texts['media_added'])
    await show_broadcast_panel(update, context)

# ========== BUTON EKLEME ==========
async def add_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton ekleme işlemi"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    session.state = 'waiting_button_text'
    
    await query.message.reply_text(texts['enter_button_text'])

async def handle_button_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton metni girdisini işle"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_button_text':
        return
    
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    # Geçici olarak buton metnini sakla
    if not hasattr(session, 'temp_button'):
        session.temp_button = {}
    session.temp_button['text'] = update.message.text
    session.state = 'waiting_button_url'
    
    await update.message.reply_text(texts['enter_button_url'])

async def handle_button_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton URL girdisini işle"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_button_url':
        return
    
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    # Butonu tamamla
    button_text = session.temp_button['text']
    button_url = update.message.text
    
    session.buttons.append({
        'text': button_text,
        'url': button_url
    })
    
    # Geçici veriyi temizle
    del session.temp_button
    session.state = None
    
    await update.message.reply_text(texts['button_added'])
    await show_broadcast_panel(update, context)

# ========== ÖNİZLEME ==========
async def preview_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast önizlemesi"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    
    # Butonları oluştur
    keyboard = []
    for btn in session.buttons:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    preview_text = texts['preview_title'] + session.get_content_summary(user_lang)
    
    if session.photo:
        await query.message.reply_photo(
            photo=session.photo,
            caption=preview_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif session.video:
        await query.message.reply_video(
            video=session.video,
            caption=preview_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await query.message.reply_text(
            preview_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# ========== GÖNDERİM ONAYI ==========
async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gönderim onayı"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    
    # Kontrol: İçerik var mı?
    if not session.text and not session.photo and not session.video:
        await query.message.reply_text(texts['no_content'])
        return
    
    # Kaç kişiye gidecek?
    user_data = load_user_data()
    total_users = len(user_data)
    
    keyboard = [
        [
            InlineKeyboardButton(texts['yes_send'], callback_data="broadcast_final_send"),
            InlineKeyboardButton(texts['no_cancel'], callback_data="broadcast_back")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        texts['confirm_send'].format(total_users),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ========== GERÇEK GÖNDERİM ==========
async def send_broadcast_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast'i tüm kullanıcılara gönder"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    
    # Butonları oluştur
    keyboard = []
    for btn in session.buttons:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Tüm kullanıcıları al
    user_data = load_user_data()
    user_ids = list(user_data.keys())
    
    await query.edit_message_text(texts['sending'])
    
    # Gönderim istatistikleri
    sent_count = 0
    failed_count = 0
    
    # Her kullanıcıya gönder
    for uid in user_ids:
        try:
            if session.photo:
                await context.bot.send_photo(
                    chat_id=int(uid),
                    photo=session.photo,
                    caption=session.text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            elif session.video:
                await context.bot.send_video(
                    chat_id=int(uid),
                    video=session.video,
                    caption=session.text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=session.text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            sent_count += 1
        except Exception as e:
            print(f"❌ Failed to send to {uid}: {e}")
            failed_count += 1
    
    # Oturumu temizle
    session.reset()
    
    # Sonuç mesajı
    result_text = texts['sent_success'].format(sent_count)
    if failed_count > 0:
        result_text += "\n" + texts['sent_failed'].format(failed_count)
    
    await query.edit_message_text(result_text)
    await show_broadcast_panel(update, context)

# ========== YARDIMCI FONKSİYONLAR ==========
async def show_broadcast_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast panelini göster"""
    user_id = None
    
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    elif update.message:
        user_id = update.message.from_user.id
    
    if not user_id:
        return
    
    user_lang = get_user_lang(user_id)
    texts = BROADCAST_TEXTS[user_lang]
    
    session = get_session(user_id)
    
    # Ana broadcast paneli
    keyboard = [
        [InlineKeyboardButton(texts['add_text'], callback_data="broadcast_add_text")],
        [InlineKeyboardButton(texts['add_media'], callback_data="broadcast_add_media")],
        [InlineKeyboardButton(texts['add_button'], callback_data="broadcast_add_button")],
        [
            InlineKeyboardButton(texts['preview'], callback_data="broadcast_preview"),
            InlineKeyboardButton(texts['send'], callback_data="broadcast_confirm_send")
        ],
        [
            InlineKeyboardButton(texts['remove_last'], callback_data="broadcast_remove_last"),
            InlineKeyboardButton(texts['clear_all'], callback_data="broadcast_clear_all")
        ],
        [InlineKeyboardButton(texts['cancel'], callback_data="broadcast_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            texts['panel_title'] + "\n\n" + session.get_content_summary(user_lang),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.message:
        await update.message.reply_text(
            texts['panel_title'] + "\n\n" + session.get_content_summary(user_lang),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def remove_last_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Son ekleneni kaldır"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    
    if session.buttons:
        session.buttons.pop()
    elif session.video:
        session.video = None
    elif session.photo:
        session.photo = None
    elif session.text:
        session.text = None
    
    await show_broadcast_panel(update, context)

async def clear_all_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tümünü temizle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.reset()
    
    await show_broadcast_panel(update, context)

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast'i iptal et"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.reset()
    
    user_lang = get_user_lang(user_id)
    await query.edit_message_text("📭 Broadcast cancelled.")

# ========== BUTON İŞLEMLERİ ==========
async def broadcast_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast butonlarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        user_lang = get_user_lang(user_id)
        await query.edit_message_text(BROADCAST_TEXTS[user_lang]['admin_only'])
        return
    
    if query.data == "broadcast_add_text":
        await add_text_handler(update, context)
    
    elif query.data == "broadcast_add_media":
        await add_media_handler(update, context)
    
    elif query.data == "broadcast_add_button":
        await add_button_handler(update, context)
    
    elif query.data == "broadcast_preview":
        await preview_broadcast(update, context)
    
    elif query.data == "broadcast_confirm_send":
        await confirm_send(update, context)
    
    elif query.data == "broadcast_final_send":
        await send_broadcast_to_all(update, context)
    
    elif query.data == "broadcast_remove_last":
        await remove_last_item(update, context)
    
    elif query.data == "broadcast_clear_all":
        await clear_all_items(update, context)
    
    elif query.data == "broadcast_cancel":
        await cancel_broadcast(update, context)
    
    elif query.data == "broadcast_back":
        await show_broadcast_panel(update, context)

# ========== KURULUM ==========
def setup(app):
    """Sadece broadcast sistemi"""
    # Komut
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Buton işleyicileri
    app.add_handler(CallbackQueryHandler(broadcast_button_callback, pattern="^broadcast_"))
    
    # Mesaj işleyicileri
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_text_input
    ))
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE,
        handle_media_input
    ))
    app.add_handler(MessageHandler(
        filters.VIDEO & filters.ChatType.PRIVATE,
        handle_media_input
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_button_text_input
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_button_url_input
    ))
    
    print("✅ Broadcast system loaded: /settings (professional)")
