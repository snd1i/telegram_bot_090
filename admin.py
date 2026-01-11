import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import is_admin, CHANNEL_LINK, CHANNEL_ID
from database import db

# ========== ADMIN KLAVYELERİ ==========

def admin_keyboard():
    """Ana admin klavyesi"""
    keyboard = [
        [InlineKeyboardButton("📢 Duyuru Gönder", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 İstatistikler", callback_data="admin_stats")],
        [InlineKeyboardButton("❌ Kapat", callback_data="admin_close")],
    ]
    return InlineKeyboardMarkup(keyboard)

def broadcast_options_keyboard():
    """Duyuru seçenekleri"""
    keyboard = [
        [InlineKeyboardButton("📝 Metin Duyurusu", callback_data="broadcast_text")],
        [InlineKeyboardButton("🔗 Butonlu Duyuru", callback_data="broadcast_button")],
        [InlineKeyboardButton("↩️ Geri", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard():
    """İptal klavyesi"""
    keyboard = [
        [InlineKeyboardButton("❌ İptal Et", callback_data="admin_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== ADMIN KOMUTLARI ==========

def admin_command(update: Update, context: CallbackContext):
    """Admin komutu"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        update.message.reply_text("❌ Bu komut sadece adminler için!")
        return
    
    total_users = len(db.users)
    
    message = f"🔧 *ADMIN PANELİ*\n\n"
    message += f"👥 Toplam Kullanıcı: {total_users}\n"
    message += f"👇 Aşağıdaki seçeneklerden birini seçin:"
    
    update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )

def cancel_command(update: Update, context: CallbackContext):
    """/cancel komutu"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        update.message.reply_text("Bu komutu kullanma yetkiniz yok!")
        return
    
    # Tüm bekleme durumlarını temizle
    for key in ['awaiting_broadcast', 'awaiting_button_text', 'awaiting_button_url']:
        if key in context.user_data:
            del context.user_data[key]
    
    update.message.reply_text(
        "✅ Tüm işlemler iptal edildi!",
        reply_markup=admin_keyboard()
    )

# ========== ADMIN CALLBACK HANDLER ==========

def admin_callback_handler(update: Update, context: CallbackContext):
    """Admin callback'leri işle"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        query.edit_message_text("❌ Bu işlemi yapma yetkiniz yok!")
        return
    
    data = query.data
    
    # Ana admin paneli
    if data == "admin_back":
        total_users = len(db.users)
        query.edit_message_text(
            f"🔧 *ADMIN PANELİ*\n\nToplam Kullanıcı: {total_users}",
            parse_mode='Markdown',
            reply_markup=admin_keyboard()
        )
    
    # Duyuru başlat
    elif data == "admin_broadcast":
        query.edit_message_text(
            "📢 *DUYURU GÖNDERME*\n\nDuyuru tipini seçin:",
            parse_mode='Markdown',
            reply_markup=broadcast_options_keyboard()
        )
    
    # Metin duyurusu
    elif data == "broadcast_text":
        context.user_data['awaiting_broadcast'] = True
        context.user_data['broadcast_type'] = 'text'
        
        query.edit_message_text(
            "📝 *METİN DUYURUSU*\n\n"
            "Duyuru mesajınızı gönderin:\n"
            "(HTML formatını kullanabilirsiniz)\n\n"
            "❌ İptal: /cancel",
            parse_mode='Markdown',
            reply_markup=cancel_keyboard()
        )
    
    # Butonlu duyuru
    elif data == "broadcast_button":
        context.user_data['awaiting_broadcast'] = True
        context.user_data['broadcast_type'] = 'button'
        context.user_data['broadcast_step'] = 'message'
        
        query.edit_message_text(
            "🔗 *BUTONLU DUYURU*\n\n"
            "Önce duyuru mesajınızı gönderin:\n"
            "(HTML formatını kullanabilirsiniz)\n\n"
            "❌ İptal: /cancel",
            parse_mode='Markdown',
            reply_markup=cancel_keyboard()
        )
    
    # İstatistikler
    elif data == "admin_stats":
        total_users = len(db.users)
        
        # Dil dağılımı
        lang_counts = {}
        for user_data in db.users.values():
            lang = user_data.get('language', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        stats_text = "📊 *İSTATİSTİKLER*\n\n"
        stats_text += f"👥 Toplam Kullanıcı: {total_users}\n\n"
        stats_text += "🌍 Dil Dağılımı:\n"
        
        for lang, count in lang_counts.items():
            percentage = int(count / total_users * 100) if total_users > 0 else 0
            stats_text += f"• {lang}: {count} ({percentage}%)\n"
        
        query.edit_message_text(
            stats_text,
            parse_mode='Markdown',
            reply_markup=admin_keyboard()
        )
    
    # Kapat
    elif data == "admin_close":
        query.edit_message_text("✅ Admin paneli kapatıldı.")
    
    # İptal
    elif data == "admin_cancel":
        # Temizlik
        for key in ['awaiting_broadcast', 'broadcast_type', 'broadcast_step', 
                   'awaiting_button_text', 'awaiting_button_url']:
            if key in context.user_data:
                del context.user_data[key]
        
        query.edit_message_text(
            "❌ İşlem iptal edildi!",
            reply_markup=admin_keyboard()
        )

# ========== MESAJ HANDLER (Duyuru için) ==========

def handle_admin_messages(update: Update, context: CallbackContext):
    """Admin mesajlarını işle (duyuru için)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return
    
    # Duyuru mesajı bekleniyor mu?
    if context.user_data.get('awaiting_broadcast'):
        message = update.message
        
        # Normal metin duyurusu
        if context.user_data.get('broadcast_type') == 'text':
            # Mesajı kaydet
            context.user_data['broadcast_message'] = message
            
            # Önizleme göster
            preview_text = message.text[:200] + "..." if len(message.text) > 200 else message.text
            
            update.message.reply_text(
                f"✅ *Mesaj kaydedildi!*\n\n"
                f"📄 Önizleme:\n{preview_text}\n\n"
                f"👥 Gönderilecek: {len(db.users)} kullanıcı\n\n"
                f"Duyuruyu göndermek istiyor musunuz?",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Evet, Gönder", callback_data="confirm_send")],
                    [InlineKeyboardButton("❌ Hayır, İptal", callback_data="admin_cancel")]
                ])
            )
            
            # Bekleme durumunu temizle
            del context.user_data['awaiting_broadcast']
        
        # Butonlu duyuru - mesaj adımı
        elif (context.user_data.get('broadcast_type') == 'button' and 
              context.user_data.get('broadcast_step') == 'message'):
            
            # Mesajı kaydet
            context.user_data['broadcast_message'] = message
            context.user_data['broadcast_step'] = 'button_text'
            
            update.message.reply_text(
                "✅ *Mesaj kaydedildi!*\n\n"
                "Şimdi buton metnini gönderin:\n"
                "(Örnek: Kanalımız, Web Sitemiz)\n\n"
                "❌ İptal: /cancel",
                reply_markup=cancel_keyboard()
            )
        
        # Butonlu duyuru - buton metni adımı
        elif (context.user_data.get('broadcast_type') == 'button' and 
              context.user_data.get('broadcast_step') == 'button_text'):
            
            button_text = update.message.text.strip()
            
            if len(button_text) > 20:
                update.message.reply_text(
                    "❌ Buton metni çok uzun! En fazla 20 karakter.\n"
                    "Tekrar gönderin:",
                    reply_markup=cancel_keyboard()
                )
                return
            
            context.user_data['button_text'] = button_text
            context.user_data['broadcast_step'] = 'button_url'
            
            update.message.reply_text(
                f"✅ *Buton metni kaydedildi:* {button_text}\n\n"
                f"Şimdi buton linkini gönderin:\n"
                f"(Örnek: https://t.me/kanal)\n\n"
                f"❌ İptal: /cancel"
            )
        
        # Butonlu duyuru - buton linki adımı
        elif (context.user_data.get('broadcast_type') == 'button' and 
              context.user_data.get('broadcast_step') == 'button_url'):
            
            button_url = update.message.text.strip()
            
            # URL kontrolü
            if not button_url.startswith(('http://', 'https://', 't.me/')):
                update.message.reply_text(
                    "❌ Geçersiz link! https:// veya t.me/ ile başlamalı.\n"
                    "Tekrar gönderin:",
                    reply_markup=cancel_keyboard()
                )
                return
            
            context.user_data['button_url'] = button_url
            context.user_data['broadcast_step'] = 'preview'
            
            # Önizleme göster
            message = context.user_data['broadcast_message']
            button_text = context.user_data['button_text']
            
            preview = message.text[:150] + "..." if len(message.text) > 150 else message.text
            
            update.message.reply_text(
                f"✅ *Buton bilgileri kaydedildi!*\n\n"
                f"🔘 Buton: {button_text}\n"
                f"🔗 Link: {button_url}\n\n"
                f"📄 Önizleme:\n{preview}\n\n"
                f"👥 Gönderilecek: {len(db.users)} kullanıcı\n\n"
                f"Duyuruyu göndermek istiyor musunuz?",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Evet, Gönder", callback_data="confirm_send")],
                    [InlineKeyboardButton("❌ Hayır, İptal", callback_data="admin_cancel")]
                ])
            )
    
    # Kanal linki değiştirme
    elif context.user_data.get('awaiting_channel_link'):
        new_link = update.message.text.strip()
        
        # URL kontrolü
        if not new_link.startswith(('http://', 'https://', 't.me/')):
            update.message.reply_text("❌ Geçersiz link formatı!")
            return
        
        # Ayarları kaydet (basit JSON)
        settings = {"channel_link": new_link}
        try:
            with open("bot_settings.json", "w") as f:
                json.dump(settings, f)
        except:
            pass
        
        del context.user_data['awaiting_channel_link']
        
        update.message.reply_text(
            f"✅ Kanal linki güncellendi!\nYeni link: {new_link}",
            reply_markup=admin_keyboard()
        )

# ========== DUYURU GÖNDERME ==========

def send_broadcast_callback(update: Update, context: CallbackContext):
    """Duyuruyu gönder"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        return
    
    message = context.user_data.get('broadcast_message')
    button_text = context.user_data.get('button_text')
    button_url = context.user_data.get('button_url')
    total_users = len(db.users)
    
    if not message:
        query.edit_message_text("❌ Gönderilecek mesaj bulunamadı!")
        return
    
    # Buton oluştur
    reply_markup = None
    if button_text and button_url:
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(button_text, url=button_url)
        ]])
    
    sent = 0
    failed = 0
    
    # İlerleme mesajı
    progress_msg = query.edit_message_text(
        f"🚀 Duyuru gönderiliyor...\n0/{total_users}"
    )
    
    # Her kullanıcıya gönder
    for user_id_str in db.users.keys():
        try:
            if message.text:
                context.bot.send_message(
                    chat_id=int(user_id_str),
                    text=message.text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            elif message.photo:
                context.bot.send_photo(
                    chat_id=int(user_id_str),
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            
            sent += 1
            
            # Her 10 gönderimde güncelle
            if sent % 10 == 0:
                progress_msg.edit_text(f"🚀 Duyuru gönderiliyor...\n{sent}/{total_users}")
            
        except Exception as e:
            failed += 1
    
    # Sonuç
    result = f"✅ *DUYURU TAMAMLANDI!*\n\n"
    result += f"✅ Başarılı: {sent}\n"
    result += f"❌ Başarısız: {failed}\n"
    result += f"📊 Toplam: {total_users}"
    
    if button_text:
        result += f"\n🔘 Buton: {button_text}"
    
    query.edit_message_text(
        result,
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )
    
    # Temizlik
    keys = ['broadcast_message', 'broadcast_type', 'broadcast_step',
            'button_text', 'button_url', 'awaiting_broadcast']
    for key in keys:
        if key in context.user_data:
            del context.user_data[key]
