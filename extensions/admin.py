# extensions/admin.py - PROFESYONEL DUYURU SİSTEMİ (DÜZELTİLMİŞ)
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

def is_admin(user_id):
    """Admin kontrolü"""
    config = load_config()
    return str(user_id) == config.get('admin_id', "5541236874")

# ========== MESAJLAR (SADECE İNGİLİZCE) ==========
TEXTS = {
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
    'no_cancel': "❌ No, Cancel",
    'broadcast_cancelled': "📭 Broadcast cancelled."
}

# ========== BROADCAST VERİ YAPISI ==========
broadcast_data = {}

class BroadcastSession:
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.text = None
        self.photo = None
        self.video = None
        self.buttons = []
        self.state = None
    
    def get_summary(self):
        """İçerik özetini al"""
        summary = TEXTS['current_content']
        
        if self.text:
            summary += TEXTS['text_content'].format(self.text[:50] + ("..." if len(self.text) > 50 else ""))
        
        if self.photo:
            summary += TEXTS['media_content'].format("📷 Photo")
        elif self.video:
            summary += TEXTS['media_content'].format("🎬 Video")
        
        if self.buttons:
            button_texts = [btn['text'] for btn in self.buttons]
            summary += TEXTS['buttons_content'].format(", ".join(button_texts))
        
        if not self.text and not self.photo and not self.video:
            summary = TEXTS['no_content']
        
        return summary
    
    def reset(self):
        self.text = None
        self.photo = None
        self.video = None
        self.buttons = []
        self.state = None

def get_session(user_id):
    user_id_str = str(user_id)
    if user_id_str not in broadcast_data:
        broadcast_data[user_id_str] = BroadcastSession(user_id)
    return broadcast_data[user_id_str]

# ========== /settings KOMUTU ==========
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ana broadcast komutu"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(TEXTS['admin_only'])
        return
    
    session = get_session(user_id)
    session.reset()
    
    await show_main_panel(update, context)

# ========== ANA PANEL GÖSTER ==========
async def show_main_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ana paneli göster"""
    user_id = None
    message = None
    
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
    elif update.message:
        user_id = update.message.from_user.id
        message = update.message
    
    if not user_id or not message:
        return
    
    session = get_session(user_id)
    
    keyboard = [
        [InlineKeyboardButton(TEXTS['add_text'], callback_data="bc_add_text")],
        [InlineKeyboardButton(TEXTS['add_media'], callback_data="bc_add_media")],
        [InlineKeyboardButton(TEXTS['add_button'], callback_data="bc_add_button")],
        [
            InlineKeyboardButton(TEXTS['preview'], callback_data="bc_preview"),
            InlineKeyboardButton(TEXTS['send'], callback_data="bc_confirm")
        ],
        [
            InlineKeyboardButton(TEXTS['remove_last'], callback_data="bc_remove_last"),
            InlineKeyboardButton(TEXTS['clear_all'], callback_data="bc_clear_all")
        ],
        [InlineKeyboardButton(TEXTS['cancel'], callback_data="bc_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = TEXTS['panel_title'] + "\n\n" + session.get_summary()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ========== METİN EKLEME ==========
async def add_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metin ekleme başlat"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.state = 'waiting_text'
    
    await query.message.reply_text(TEXTS['enter_text'])

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metin girdisini al"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_text':
        return
    
    session.text = update.message.text
    session.state = None
    
    await update.message.reply_text(TEXTS['text_added'])
    await show_main_panel(update, context)

# ========== MEDİA EKLEME ==========
async def add_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Media ekleme başlat"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.state = 'waiting_media'
    
    await query.message.reply_text(TEXTS['send_photo_video'])

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Media girdisini al"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_media':
        return
    
    if update.message.photo:
        session.photo = update.message.photo[-1].file_id
        session.video = None
    elif update.message.video:
        session.video = update.message.video.file_id
        session.photo = None
    
    if update.message.caption:
        session.text = update.message.caption
    
    session.state = None
    
    await update.message.reply_text(TEXTS['media_added'])
    await show_main_panel(update, context)

# ========== BUTON EKLEME ==========
async def add_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton ekleme başlat"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.state = 'waiting_btn_text'
    
    await query.message.reply_text(TEXTS['enter_button_text'])

async def handle_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton metnini al"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_btn_text':
        return
    
    # Geçici saklama
    session.temp_button_text = update.message.text
    session.state = 'waiting_btn_url'
    
    await update.message.reply_text(TEXTS['enter_button_url'])

async def handle_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton URL'sini al"""
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.state != 'waiting_btn_url':
        return
    
    # Butonu ekle
    session.buttons.append({
        'text': session.temp_button_text,
        'url': update.message.text
    })
    
    # Temizle
    del session.temp_button_text
    session.state = None
    
    await update.message.reply_text(TEXTS['button_added'])
    await show_main_panel(update, context)

# ========== ÖNİZLEME ==========
async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Önizleme göster"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    
    # Butonları oluştur
    keyboard = []
    for btn in session.buttons:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    preview_text = TEXTS['preview_title'] + session.get_summary()
    
    try:
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
    except Exception as e:
        await query.message.reply_text(f"❌ Preview error: {str(e)}")

# ========== ONAY VE GÖNDERİM ==========
async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gönderim onayı"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    
    if not session.text and not session.photo and not session.video:
        await query.message.reply_text(TEXTS['no_content'])
        return
    
    user_data = load_user_data()
    total_users = len(user_data)
    
    keyboard = [
        [
            InlineKeyboardButton(TEXTS['yes_send'], callback_data="bc_send_final"),
            InlineKeyboardButton(TEXTS['no_cancel'], callback_data="bc_back")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        TEXTS['confirm_send'].format(total_users),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def send_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast'i gönder"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    
    # Butonları oluştur
    keyboard = []
    for btn in session.buttons:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    user_data = load_user_data()
    user_ids = list(user_data.keys())
    
    await query.edit_message_text(TEXTS['sending'])
    
    sent = 0
    failed = 0
    
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
            sent += 1
        except Exception as e:
            print(f"Failed to {uid}: {e}")
            failed += 1
    
    session.reset()
    
    result = TEXTS['sent_success'].format(sent)
    if failed > 0:
        result += "\n" + TEXTS['sent_failed'].format(failed)
    
    await query.edit_message_text(result)
    await show_main_panel(update, context)

# ========== YARDIMCI FONKSİYONLAR ==========
async def remove_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Son ekleneni sil"""
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
    
    await show_main_panel(update, context)

async def clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tümünü temizle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.reset()
    
    await show_main_panel(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """İptal et"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    session.reset()
    
    await query.edit_message_text(TEXTS['broadcast_cancelled'])

# ========== BUTON İŞLEYİCİ ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm butonları işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text(TEXTS['admin_only'])
        return
    
    data = query.data
    
    if data == "bc_add_text":
        await add_text(update, context)
    elif data == "bc_add_media":
        await add_media(update, context)
    elif data == "bc_add_button":
        await add_button(update, context)
    elif data == "bc_preview":
        await preview(update, context)
    elif data == "bc_confirm":
        await confirm_send(update, context)
    elif data == "bc_send_final":
        await send_final(update, context)
    elif data == "bc_remove_last":
        await remove_last(update, context)
    elif data == "bc_clear_all":
        await clear_all(update, context)
    elif data == "bc_cancel":
        await cancel(update, context)
    elif data == "bc_back":
        await show_main_panel(update, context)

# ========== KURULUM ==========
def setup(app):
    """Extension'ı kur"""
    # Komut
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Butonlar
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^bc_"))
    
    # Mesajlar
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_text
    ))
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE,
        handle_media
    ))
    app.add_handler(MessageHandler(
        filters.VIDEO & filters.ChatType.PRIVATE,
        handle_media
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_button_text
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_button_url
    ))
    
    print("✅ Broadcast system loaded: /settings (English only, fixed)")
