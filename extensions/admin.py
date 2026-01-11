# extensions/admin.py - ADMIN PANELİ
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
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

def is_admin(user_id):
    """Admin kontrolü"""
    config = load_config()
    return str(user_id) == config.get('admin_id', "5541236874")

# ========== /settings KOMUTU ==========
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin paneli"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu komutu sadece admin kullanabilir!")
        return
    
    # Admin paneli butonları
    keyboard = [
        [InlineKeyboardButton("📝 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔄 Help Mesajını Düzenle", callback_data="admin_edit_help")],
        [InlineKeyboardButton("📱 App Ayarları", callback_data="admin_app_settings")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton("⚙️ Bot Ayarları", callback_data="admin_bot_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👑 **Admin Paneli**\n\n"
        "Aşağıdaki butonlardan birini seçin:",
        reply_markup=reply_markup
    )

# ========== BUTON İŞLEMLERİ ==========
async def admin_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin butonlarını işle"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ Yetkiniz yok!")
        return
    
    if query.data == "admin_broadcast":
        # Duyuru gönderim paneli
        keyboard = [
            [InlineKeyboardButton("📝 Metin Duyurusu", callback_data="broadcast_text")],
            [InlineKeyboardButton("🖼️ Resimli Duyuru", callback_data="broadcast_photo")],
            [InlineKeyboardButton("🎬 Videolu Duyuru", callback_data="broadcast_video")],
            [InlineKeyboardButton("🔙 Geri", callback_data="admin_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📢 **Duyuru Gönder**\n\n"
            "Duyuru türünü seçin:",
            reply_markup=reply_markup
        )
    
    elif query.data == "admin_edit_help":
        # Help mesajını düzenle
        await query.edit_message_text(
            "🔄 **Help Mesajını Düzenle**\n\n"
            "Şu anda bu özellik geliştirme aşamasında.\n"
            "Yakında kullanıma sunulacak."
        )
    
    elif query.data == "admin_app_settings":
        # App ayarları
        await query.edit_message_text(
            "📱 **App Ayarları**\n\n"
            "App özellikleri yakında eklenecek."
        )
    
    elif query.data == "admin_stats":
        # İstatistikler
        try:
            with open('user_data.json', 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            total_users = len(user_data)
            
            # Dil dağılımı
            lang_dist = {}
            for user_info in user_data.values():
                lang = user_info.get('lang', 'unknown')
                lang_dist[lang] = lang_dist.get(lang, 0) + 1
            
            stats_text = f"📊 **Bot İstatistikleri**\n\n"
            stats_text += f"👥 Toplam Kullanıcı: {total_users}\n\n"
            stats_text += "🌍 **Dil Dağılımı:**\n"
            
            for lang, count in lang_dist.items():
                percentage = (count / total_users * 100) if total_users > 0 else 0
                lang_name = {'ku': 'Kürtçe', 'en': 'İngilizce', 'ar': 'Arapça'}.get(lang, lang)
                stats_text += f"• {lang_name}: {count} kişi (%{percentage:.1f})\n"
            
            # Geri butonu
            keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(stats_text, reply_markup=reply_markup)
            
        except Exception as e:
            await query.edit_message_text(f"❌ İstatistik alınırken hata: {str(e)}")
    
    elif query.data == "admin_bot_settings":
        # Bot ayarları
        config = load_config()
        
        settings_text = (
            "⚙️ **Bot Ayarları**\n\n"
            f"👑 Admin ID: {config.get('admin_id', 'Belirtilmemiş')}\n"
            f"📢 Kanal: {config.get('channel_username', 'Ayarlanmamış')}\n"
            f"🔗 Davet Linki: {config.get('channel_invite_link', 'Ayarlanmamış')}\n"
            f"📌 Zorunlu Abonelik: {'✅ Açık' if config.get('required_channel') else '❌ Kapalı'}\n\n"
            "Bot ayarlarını değiştirmek için /join komutunu kullanın."
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Geri", callback_data="admin_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(settings_text, reply_markup=reply_markup)
    
    elif query.data == "admin_back":
        # Ana panele dön
        keyboard = [
            [InlineKeyboardButton("📝 Duyuru Gönder", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔄 Help Mesajını Düzenle", callback_data="admin_edit_help")],
            [InlineKeyboardButton("📱 App Ayarları", callback_data="admin_app_settings")],
            [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
            [InlineKeyboardButton("⚙️ Bot Ayarları", callback_data="admin_bot_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👑 **Admin Paneli**\n\n"
            "Aşağıdaki butonlardan birini seçin:",
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("broadcast_"):
        # Duyuru türü seçildi
        broadcast_type = query.data.replace("broadcast_", "")
        type_names = {"text": "Metin", "photo": "Resim", "video": "Video"}
        
        await query.edit_message_text(
            f"📢 **{type_names.get(broadcast_type, 'Duyuru')} Gönderimi**\n\n"
            "Bu özellik yakında eklenecek.\n"
            f"Seçilen tür: {type_names.get(broadcast_type, 'Bilinmeyen')}\n\n"
            "Özellik tamamlandığında:\n"
            "1. Duyuru içeriğini girebileceksiniz\n"
            "2. Buton ekleyebileceksiniz\n"
            "3. Kaç kişiye ulaştığını görebileceksiniz"
        )

# ========== KURULUM ==========
def setup(app):
    """Admin komutlarını bot'a ekler"""
    # Komutlar
    app.add_handler(CommandHandler("settings", settings_command))
    
    # Buton işleyicileri
    app.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(admin_button_callback, pattern="^broadcast_"))
    
    print("✅ Admin extension loaded: /settings")
