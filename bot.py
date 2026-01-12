# extensions/admin.py - BASİT VE ÇALIŞAN DUYURU SİSTEMİ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import json
import os

# ========== DOSYA İŞLEMLERİ ==========
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"admin_id": "5541236874"}

def load_user_data():
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def is_admin(user_id):
    config = load_config()
    return str(user_id) == config.get('admin_id', "5541236874")

# ========== MESAJLAR ==========
TEXTS = {
    'admin_only': "❌ Only admin can use this command!",
    'panel_title': "📢 **Send Broadcast**\n\nSelect an option below:",
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
    'no_content': "⚠️ No content yet!",
    'sending': "🔄 Sending...",
    'sent_success': "✅ Broadcast sent to {} people!",
    'sent_failed': "❌ Failed to reach {} people.",
    'current_content': "📋 **Current Content:**\n",
    'remove_last': "🗑️ Remove Last",
    'clear_all': "🧹 Clear All",
    'confirm_send': "⚠️ **Confirm Send?**\n\n{} people will receive it.",
    'yes_send': "✅ Yes, Send",
    'no_cancel': "❌ No, Cancel",
    'broadcast_cancelled': "📭 Broadcast cancelled."
}

# ========== BASİT VERİ YAPISI ==========
user_sessions = {}

def get_session(user_id):
    user_id_str = str(user_id)
    if user_id_str not in user_sessions:
        user_sessions[user_id_str] = {
            'text': None,
            'photo': None,
            'video': None,
            'buttons': [],
            'state': None,
            'temp_button_text': None
        }
    return user_sessions[user_id_str]

def get_content_summary(session):
    summary = TEXTS['current_content']
    
    if session['text']:
        summary += f"📝 Text: {session['text'][:50]}...\n" if len(session['text']) > 50 else f"📝 Text: {session['text']}\n"
    
    if session['photo']:
        summary += "🖼️ Media: 📷 Photo\n"
    elif session['video']:
        summary += "🖼️ Media: 🎬 Video\n"
    
    if session['buttons']:
        button_texts = [btn['text'] for btn in session['buttons']]
        summary += f"🔘 Buttons: {', '.join(button_texts)}\n"
    
    if not session['text'] and not session['photo'] and not session['video']:
        summary = TEXTS['no_content']
    
    return summary

# ========== ANA KOMUT ==========
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(TEXTS['admin_only'])
        return
    
    session = get_session(user_id)
    session.update({
        'text': None,
        'photo': None,
        'video': None,
        'buttons': [],
        'state': None,
        'temp_button_text': None
    })
    
    await show_panel(update, context, user_id)

# ========== PANEL GÖSTER ==========
async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
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
            InlineKeyboardButton(TEXTS['remove_last'], callback_data="bc_remove"),
            InlineKeyboardButton(TEXTS['clear_all'], callback_data="bc_clear")
        ],
        [InlineKeyboardButton(TEXTS['cancel'], callback_data="bc_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = TEXTS['panel_title'] + "\n\n" + get_content_summary(session)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ========== BUTON İŞLEYİCİ ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text(TEXTS['admin_only'])
        return
    
    data = query.data
    session = get_session(user_id)
    
    if data == "bc_add_text":
        session['state'] = 'waiting_text'
        await query.message.reply_text(TEXTS['enter_text'])
    
    elif data == "bc_add_media":
        session['state'] = 'waiting_media'
        await query.message.reply_text(TEXTS['send_photo_video'])
    
    elif data == "bc_add_button":
        session['state'] = 'waiting_button_text'
        await query.message.reply_text(TEXTS['enter_button_text'])
    
    elif data == "bc_preview":
        # Önizleme
        keyboard = []
        for btn in session['buttons']:
            keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        preview_text = "👁️ **Broadcast Preview**\n\n" + get_content_summary(session)
        
        if session['photo']:
            await query.message.reply_photo(
                photo=session['photo'],
                caption=preview_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif session['video']:
            await query.message.reply_video(
                video=session['video'],
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
    
    elif data == "bc_confirm":
        # Onay
        user_data = load_user_data()
        total_users = len(user_data)
        
        keyboard = [
            [InlineKeyboardButton(TEXTS['yes_send'], callback_data="bc_send")],
            [InlineKeyboardButton(TEXTS['no_cancel'], callback_data="bc_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            TEXTS['confirm_send'].format(total_users),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == "bc_send":
        # Gönder
        await query.edit_message_text(TEXTS['sending'])
        
        # Butonlar
        keyboard = []
        for btn in session['buttons']:
            keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        # Tüm kullanıcılara gönder
        user_data = load_user_data()
        sent = 0
        failed = 0
        
        for uid in user_data.keys():
            try:
                if session['photo']:
                    await context.bot.send_photo(
                        chat_id=int(uid),
                        photo=session['photo'],
                        caption=session['text'],
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                elif session['video']:
                    await context.bot.send_video(
                        chat_id=int(uid),
                        video=session['video'],
                        caption=session['text'],
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_message(
                        chat_id=int(uid),
                        text=session['text'],
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                sent += 1
            except:
                failed += 1
        
        # Sonuç
        result = TEXTS['sent_success'].format(sent)
        if failed > 0:
            result += "\n" + TEXTS['sent_failed'].format(failed)
        
        await query.edit_message_text(result)
        
        # Temizle
        session.update({
            'text': None,
            'photo': None,
            'video': None,
            'buttons': [],
            'state': None,
            'temp_button_text': None
        })
        
        await show_panel(update, context, user_id)
    
    elif data == "bc_remove":
        # Son ekleneni sil
        if session['buttons']:
            session['buttons'].pop()
        elif session['video']:
            session['video'] = None
        elif session['photo']:
            session['photo'] = None
        elif session['text']:
            session['text'] = None
        
        await show_panel(update, context, user_id)
    
    elif data == "bc_clear":
        # Tümünü temizle
        session.update({
            'text': None,
            'photo': None,
            'video': None,
            'buttons': [],
            'state': None,
            'temp_button_text': None
        })
        
        await show_panel(update, context, user_id)
    
    elif data == "bc_cancel":
        # İptal
        session.update({
            'text': None,
            'photo': None,
            'video': None,
            'buttons': [],
            'state': None,
            'temp_button_text': None
        })
        
        await query.edit_message_text(TEXTS['broadcast_cancelled'])
    
    elif data == "bc_back":
        # Geri
        await show_panel(update, context, user_id)

# ========== MESAJ İŞLEYİCİLER ==========
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm mesajları tek fonksiyonda işle"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    session = get_session(user_id)
    
    # 1. METİN EKLEME
    if session['state'] == 'waiting_text':
        session['text'] = update.message.text
        session['state'] = None
        await update.message.reply_text(TEXTS['text_added'])
        await show_panel(update, context, user_id)
    
    # 2. MEDİA EKLEME
    elif session['state'] == 'waiting_media':
        if update.message.photo:
            session['photo'] = update.message.photo[-1].file_id
            session['video'] = None
        elif update.message.video:
            session['video'] = update.message.video.file_id
            session['photo'] = None
        
        if update.message.caption:
            session['text'] = update.message.caption
        
        session['state'] = None
        await update.message.reply_text(TEXTS['media_added'])
        await show_panel(update, context, user_id)
    
    # 3. BUTON METNİ
    elif session['state'] == 'waiting_button_text':
        session['temp_button_text'] = update.message.text
        session['state'] = 'waiting_button_url'
        await update.message.reply_text(TEXTS['enter_button_url'])
    
    # 4. BUTON URL'Sİ
    elif session['state'] == 'waiting_button_url':
        session['buttons'].append({
            'text': session['temp_button_text'],
            'url': update.message.text
        })
        
        session['temp_button_text'] = None
        session['state'] = None
        
        await update.message.reply_text(TEXTS['button_added'])
        await show_panel(update, context, user_id)

# ========== KURULUM ==========
def setup(app):
    """Basit ve çalışan kurulum"""
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^bc_"))
    
    # TEK MessageHandler - hepsini tek fonksiyonda işle
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO) & 
        filters.ChatType.PRIVATE,
        message_handler
    ))
    
    print("✅ Simple broadcast system loaded")
