# extensions/admin.py - PROFESYONEL DUYURU SİSTEMİ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import json
import os

# ========== DOSYA İŞLEMLERİ ==========
CONFIG_FILE = 'config.json'
USER_DATA_FILE = 'user_data.json'

def load_config():
    """Config dosyasını yükle"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"admin_id": "5541236874"}
    except:
        return {"admin_id": "5541236874"}

def load_user_data():
    """Kullanıcı verilerini yükle"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except:
        return {}

def is_admin(user_id):
    """Admin kontrolü"""
    config = load_config()
    return str(user_id) == config.get('admin_id', "5541236874")

# ========== MESAJLAR ==========
TEXTS = {
    'admin_only': "❌ Only admin can use this command!",
    'panel_title': "📢 **Broadcast Panel**\n\nSelect an option below:",
    'add_text': "📝 Add Text",
    'add_media': "🖼️ Add Media",
    'add_button': "🔘 Add Button",
    'preview': "👁️ Preview",
    'send': "📤 Send",
    'back': "🔙 Back",
    'cancel': "✖️ Cancel",
    'enter_text': "📝 Please send the broadcast text:",
    'text_added': "✅ Text added successfully!",
    'send_media': "🖼️ Please send a photo or video:",
    'media_added': "✅ Media added successfully!",
    'enter_button_text': "🔘 Please enter button text:",
    'enter_button_url': "🔗 Please enter button URL:",
    'button_added': "✅ Button added successfully!",
    'no_content': "⚠️ No content added yet!",
    'sending': "🔄 Sending broadcast to all users...",
    'sent_success': "✅ Broadcast sent to {} users!",
    'sent_failed': "❌ Failed to send to {} users.",
    'current_content': "📋 **Current Content:**\n",
    'text_content': "📝 Text: {}\n",
    'media_content': "🖼️ Media: {}\n",
    'buttons_content': "🔘 Buttons: {}\n",
    'remove_last': "🗑️ Remove Last",
    'clear_all': "🧹 Clear All",
    'confirm_send': "⚠️ **Confirm Broadcast**\n\nSend to {} users?",
    'yes_send': "✅ Yes, Send",
    'no_cancel': "❌ Cancel",
    'broadcast_cancelled': "📭 Broadcast cancelled.",
    'preview_title': "👁️ **Broadcast Preview**\n\n"
}

# ========== SESSION YÖNETİMİ ==========
broadcast_sessions = {}

class BroadcastSession:
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.text = None
        self.photo = None
        self.video = None
        self.buttons = []
        self.state = None
        self.temp_button_text = None
    
    def get_summary(self):
        """İçerik özetini al"""
        summary = TEXTS['current_content']
        
        if self.text:
            text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
            summary += TEXTS['text_content'].format(text_preview)
        
        if self.photo:
            summary += TEXTS['media_content'].format("Photo")
        elif self.video:
            summary += TEXTS['media_content'].format("Video")
        
        if self.buttons:
            button_texts = [btn['text'] for btn in self.buttons]
            summary += TEXTS['buttons_content'].format(", ".join(button_texts))
        
        if not self.text and not self.photo and not self.video and not self.buttons:
            summary = TEXTS['no_content']
        
        return summary
    
    def reset(self):
        """Session'ı sıfırla"""
        self.text = None
        self.photo = None
        self.video = None
        self.buttons = []
        self.state = None
        self.temp_button_text = None

def get_session(user_id):
    """Kullanıcı için session al veya oluştur"""
    user_id_str = str(user_id)
    if user_id_str not in broadcast_sessions:
        broadcast_sessions[user_id_str] = BroadcastSession(user_id)
    return broadcast_sessions[user_id_str]

# ========== ANA KOMUT ==========
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/settings komutu"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(TEXTS['admin_only'])
        return
    
    session = get_session(user_id)
    session.reset()
    
    await show_main_panel(update, context)

# ========== ANA PANEL ==========
async def show_main_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ana paneli göster"""
    user_id = None
    message = None
    
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
        query = update.callback_query
    elif update.message:
        user_id = update.message.from_user.id
        message = update.message
    
    if not user_id:
        return
    
    session = get_session(user_id)
    
    # Klavye oluştur
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
    
    # Mesaj metni
    text = TEXTS['panel_title'] + "\n\n" + session.get_summary()
    
    # Mesajı gönder veya düzenle
    try:
        if update.callback_query:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"Panel error: {e}")
        if update.message:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

# ========== BUTON İŞLEYİCİ ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback butonlarını işle"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text(TEXTS['admin_only'])
        return
    
    session = get_session(user_id)
    data = query.data
    
    # BUTON İŞLEMLERİ
    if data == "bc_add_text":
        session.state = "waiting_text"
        await query.message.reply_text(TEXTS['enter_text'])
    
    elif data == "bc_add_media":
        session.state = "waiting_media"
        await query.message.reply_text(TEXTS['send_media'])
    
    elif data == "bc_add_button":
        session.state = "waiting_button_text"
        await query.message.reply_text(TEXTS['enter_button_text'])
    
    elif data == "bc_preview":
        await preview_broadcast(query, session)
    
    elif data == "bc_confirm":
        await confirm_broadcast(query, session)
    
    elif data == "bc_send_final":
        await send_broadcast_final(update, context, session)
    
    elif data == "bc_remove_last":
        await remove_last_item(session)
        await show_main_panel(update, context)
    
    elif data == "bc_clear_all":
        session.reset()
        await show_main_panel(update, context)
    
    elif data == "bc_cancel":
        session.reset()
        await query.edit_message_text(TEXTS['broadcast_cancelled'])
    
    elif data == "bc_back":
        await show_main_panel(update, context)

# ========== ÖNİZLEME ==========
async def preview_broadcast(query, session):
    """Broadcast önizlemesi göster"""
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
                text=preview_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        await query.message.reply_text(f"❌ Preview error: {str(e)}")

# ========== ONAY ==========
async def confirm_broadcast(query, session):
    """Gönderim onayı"""
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
        text=TEXTS['confirm_send'].format(total_users),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ========== GÖNDERİM ==========
async def send_broadcast_final(update: Update, context: ContextTypes.DEFAULT_TYPE, session):
    """Broadcast'i gönder"""
    query = update.callback_query
    await query.edit_message_text(TEXTS['sending'])
    
    # Butonları oluştur
    keyboard = []
    for btn in session.buttons:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Tüm kullanıcılara gönder
    user_data = load_user_data()
    sent = 0
    failed = 0
    
    for user_id in user_data.keys():
        try:
            if session.photo:
                await context.bot.send_photo(
                    chat_id=int(user_id),
                    photo=session.photo,
                    caption=session.text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            elif session.video:
                await context.bot.send_video(
                    chat_id=int(user_id),
                    video=session.video,
                    caption=session.text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=session.text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            sent += 1
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            failed += 1
    
    # Sonuç
    result = TEXTS['sent_success'].format(sent)
    if failed > 0:
        result += "\n" + TEXTS['sent_failed'].format(failed)
    
    session.reset()
    
    await query.edit_message_text(result)
    await show_main_panel(update, context)

# ========== SİLME ==========
async def remove_last_item(session):
    """Son eklenen öğeyi sil"""
    if session.buttons:
        session.buttons.pop()
    elif session.video:
        session.video = None
    elif session.photo:
        session.photo = None
    elif session.text:
        session.text = None

# ========== MESAJ İŞLEYİCİ ==========
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin mesajlarını işle"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    session = get_session(user_id)
    
    # METİN EKLEME
    if session.state == "waiting_text":
        session.text = update.message.text
        session.state = None
        await update.message.reply_text(TEXTS['text_added'])
        await show_main_panel(update, context)
    
    # MEDİA EKLEME
    elif session.state == "waiting_media":
        if update.message.photo:
            session.photo = update.message.photo[-1].file_id
        elif update.message.video:
            session.video = update.message.video.file_id
        
        if update.message.caption:
            session.text = update.message.caption
        
        session.state = None
        await update.message.reply_text(TEXTS['media_added'])
        await show_main_panel(update, context)
    
    # BUTON METNİ
    elif session.state == "waiting_button_text":
        session.temp_button_text = update.message.text
        session.state = "waiting_button_url"
        await update.message.reply_text(TEXTS['enter_button_url'])
    
    # BUTON URL'Sİ
    elif session.state == "waiting_button_url":
        if hasattr(session, 'temp_button_text'):
            session.buttons.append({
                'text': session.temp_button_text,
                'url': update.message.text
            })
            session.temp_button_text = None
        
        session.state = None
        await update.message.reply_text(TEXTS['button_added'])
        await show_main_panel(update, context)

# ========== KURULUM ==========
def setup(app):
    """Extension'ı kur"""
    # Komutlar
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Buton işleyicisi
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^bc_"))
    
    # Mesaj işleyici (TEK TANE - hepsini tek fonksiyonda işle)
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO,
        message_handler
    ))
    
    print("✅ Admin broadcast system loaded successfully!")
