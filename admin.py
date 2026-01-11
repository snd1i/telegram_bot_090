import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import is_admin, ADMIN_IDS, CHANNEL_LINK, CHANNEL_ID
from database import db
from languages import get_text
from keyboards import language_keyboard

# JSON dosya yolları
MESSAGES_FILE = "bot_messages.json"
SETTINGS_FILE = "bot_settings.json"

def load_json_file(filename, default_data=None):
    """JSON dosyasını yükle"""
    if default_data is None:
        default_data = {}
    
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"JSON yükleme hatası {filename}: {e}")
    
    return default_data

def save_json_file(filename, data):
    """JSON dosyasına kaydet"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"JSON kaydetme hatası {filename}: {e}")
        return False

# ========== MANYBOT BENZERİ ADMIN KLAVYESİ ==========

def manybot_admin_keyboard():
    """Manybot benzeri admin klavyesi"""
    keyboard = [
        [
            InlineKeyboardButton("📢 Duyuru Gönder", callback_data="mb_broadcast"),
            InlineKeyboardButton("📝 Start Mesajı", callback_data="mb_start"),
        ],
        [
            InlineKeyboardButton("🔗 Kanal Linki", callback_data="mb_channel"),
            InlineKeyboardButton("📊 İstatistikler", callback_data="mb_stats"),
        ],
        [
            InlineKeyboardButton("⚙️ Ayarlar", callback_data="mb_settings"),
            InlineKeyboardButton("👥 Kullanıcılar", callback_data="mb_users"),
        ],
        [
            InlineKeyboardButton("❌ Kapat", callback_data="mb_close"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def broadcast_format_keyboard():
    """Duyuru formatı seçim klavyesi"""
    keyboard = [
        [
            InlineKeyboardButton("📝 HTML Format", callback_data="format_html"),
            InlineKeyboardButton("📄 Normal Metin", callback_data="format_normal"),
        ],
        [
            InlineKeyboardButton("↩️ Geri", callback_data="mb_back"),
            InlineKeyboardButton("❌ İptal", callback_data="mb_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def broadcast_preview_keyboard():
    """Duyuru önizleme klavyesi"""
    keyboard = [
        [
            InlineKeyboardButton("👁️ Önizleme", callback_data="broadcast_preview"),
            InlineKeyboardButton("🚀 Gönder", callback_data="broadcast_send"),
        ],
        [
            InlineKeyboardButton("✏️ Düzenle", callback_data="mb_back"),
            InlineKeyboardButton("❌ İptal", callback_data="mb_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def stats_period_keyboard():
    """İstatistik periyodu klavyesi"""
    keyboard = [
        [
            InlineKeyboardButton("📅 Bugün", callback_data="stats_today"),
            InlineKeyboardButton("📆 Bu Hafta", callback_data="stats_week"),
        ],
        [
            InlineKeyboardButton("📊 Bu Ay", callback_data="stats_month"),
            InlineKeyboardButton("📈 Tüm Zaman", callback_data="stats_total"),
        ],
        [
            InlineKeyboardButton("↩️ Geri", callback_data="mb_back"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard():
    """Ayarlar klavyesi"""
    keyboard = [
        [
            InlineKeyboardButton("🎨 Duyuru Formatı", callback_data="setting_format"),
            InlineKeyboardButton("🗑️ Otomatik Sil", callback_data="setting_auto_delete"),
        ],
        [
            InlineKeyboardButton("👋 Hoşgeldin Mesajı", callback_data="setting_welcome"),
            InlineKeyboardButton("🔄 Sıfırla", callback_data="setting_reset"),
        ],
        [
            InlineKeyboardButton("↩️ Geri", callback_data="mb_back"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== ADMIN KOMUTLARI ==========

def admin_command(update: Update, context: CallbackContext):
    """/admin komutu"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        update.message.reply_text("❌ Bu komutu kullanma yetkiniz yok!")
        return
    
    # Admin istatistikleri
    total_users = len(db.users)
    active_today = 0
    now = datetime.now()
    
    for user_data in db.users.values():
        if "last_seen" in user_data:
            last_seen = datetime.fromisoformat(user_data["last_seen"])
            if (now - last_seen).days < 1:
                active_today += 1
    
    admin_message = f"🔧 *ADMIN PANELİ*\n\n"
    admin_message += f"📊 *İstatistikler:*\n"
    admin_message += f"• 👥 Toplam Kullanıcı: {total_users}\n"
    admin_message += f"• 🟢 Bugün Aktif: {active_today}\n"
    admin_message += f"• 📈 Aktif Oranı: {int(active_today/total_users*100) if total_users > 0 else 0}%\n\n"
    admin_message += f"👇 Aşağıdaki seçeneklerden birini seçin:"
    
    update.message.reply_text(
        admin_message,
        parse_mode='Markdown',
        reply_markup=manybot_admin_keyboard()
    )

# ========== CALLBACK HANDLER'LARI ==========

def admin_callback_handler(update: Update, context: CallbackContext):
    """Admin callback'leri işle"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        query.edit_message_text("❌ Bu işlemi yapma yetkiniz yok!")
        return
    
    callback_data = query.data
    
    # Admin paneli ana menü
    if callback_data == "admin_panel" or callback_data == "mb_back":
        total_users = len(db.users)
        
        admin_message = f"🔧 *ADMIN PANELİ*\n\n"
        admin_message += f"📊 Toplam Kullanıcı: {total_users}\n\n"
        admin_message += f"👇 Aşağıdaki seçeneklerden birini seçin:"
        
        query.edit_message_text(
            admin_message,
            parse_mode='Markdown',
            reply_markup=manybot_admin_keyboard()
        )
    
    # Duyuru başlat
    elif callback_data == "mb_broadcast":
        query.edit_message_text(
            "📢 *DUYURU GÖNDERME*\n\n"
            "Duyurunuzu hangi formatta göndermek istersiniz?\n\n"
            "• **HTML**: <b>Kalın</b>, <i>İtalik</i>, <u>Altı Çizili</u>\n"
            "• **Normal**: Düz metin\n\n"
            "Bir format seçin:",
            parse_mode='Markdown',
            reply_markup=broadcast_format_keyboard()
        )
    
    # Duyuru formatı seçimi
    elif callback_data.startswith("format_"):
        format_type = callback_data.replace("format_", "")
        
        context.user_data['broadcast_format'] = format_type
        context.user_data['awaiting_broadcast'] = True
        
        format_names = {
            'html': 'HTML',
            'normal': 'Normal Metin'
        }
        
        query.edit_message_text(
            f"✅ *{format_names[format_type]} formatı seçildi!*\n\n"
            f"Şimdi duyuru mesajınızı gönderin:\n"
            f"(Metin, fotoğraf, video veya dosya olabilir)\n\n"
            f"❌ İptal etmek için: /cancel",
            parse_mode='Markdown'
        )
    
    # Start mesajı düzenleme
    elif callback_data == "mb_start":
        custom_messages = load_json_file(MESSAGES_FILE, {"start": {}})
        
        message_text = "📝 *START MESAJI DÜZENLEME*\n\n"
        message_text += "Mevcut start mesajlarınız:\n"
        
        for lang in ['tr', 'en', 'ckb', 'badini', 'ar']:
            msg = custom_messages.get("start", {}).get(lang, "Varsayılan mesaj kullanılıyor")
            lang_name = {
                'tr': 'Türkçe',
                'en': 'İngilizce',
                'ckb': 'Kürtçe Sorani',
                'badini': 'Kürtçe Badini',
                'ar': 'Arapça'
            }.get(lang, lang)
            message_text += f"\n{lang_name}: {msg[:50]}..."
        
        message_text += "\n\n✏️ Düzenlemek için dil seçin:"
        
        keyboard = []
        for lang in ['tr', 'en', 'ckb', 'badini', 'ar']:
            lang_name = {
                'tr': '🇹🇷 Türkçe',
                'en': '🇬🇧 İngilizce',
                'ckb': '🇹🇯 Kürtçe Sorani',
                'badini': '🇹🇯 Kürtçe Badini',
                'ar': '🇮🇶 Arapça'
            }.get(lang, lang)
            
            keyboard.append([
                InlineKeyboardButton(lang_name, callback_data=f"edit_start_{lang}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("↩️ Geri", callback_data="mb_back")
        ])
        
        query.edit_message_text(
            message_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Kanal linki değiştir
    elif callback_data == "mb_channel":
        settings = load_json_file(SETTINGS_FILE, {"channel_link": CHANNEL_LINK})
        current_link = settings.get("channel_link", CHANNEL_LINK)
        
        context.user_data['awaiting_channel_link'] = True
        
        query.edit_message_text(
            f"🔗 *KANAL LİNKİ DEĞİŞTİRME*\n\n"
            f"Mevcut link: {current_link}\n\n"
            f"Yeni kanal linkini gönderin:\n"
            f"(Örnek: https://t.me/kanal)\n\n"
            f"❌ İptal: /cancel",
            parse_mode='Markdown'
        )
    
    # İstatistikler
    elif callback_data == "mb_stats":
        query.edit_message_text(
            "📊 *İSTATİSTİK PERİYODU SEÇİN*\n\n"
            "Hangi periyot için istatistik görmek istersiniz?",
            parse_mode='Markdown',
            reply_markup=stats_period_keyboard()
        )
    
    # İstatistik periyodu seçimi
    elif callback_data.startswith("stats_"):
        period = callback_data.replace("stats_", "")
        show_period_stats(query, period)
    
    # Ayarlar
    elif callback_data == "mb_settings":
        settings = load_json_file(SETTINGS_FILE, {})
        
        message_text = "⚙️ *BOT AYARLARI*\n\n"
        message_text += f"• Kanal Linki: {settings.get('channel_link', CHANNEL_LINK)}\n"
        message_text += f"• Duyuru Formatı: {settings.get('broadcast_format', 'html').upper()}\n"
        message_text += f"• Otomatik Silme: {'✅ Açık' if settings.get('auto_delete') else '❌ Kapalı'}\n\n"
        message_text += "👇 Değiştirmek için bir seçenek seçin:"
        
        query.edit_message_text(
            message_text,
            parse_mode='Markdown',
            reply_markup=settings_keyboard()
        )
    
    # Ayarları değiştir
    elif callback_data.startswith("setting_"):
        setting_type = callback_data.replace("setting_", "")
        change_setting(query, setting_type)
    
    # Kullanıcılar
    elif callback_data == "mb_users":
        show_users_list(query)
    
    # Kapat
    elif callback_data == "mb_close":
        query.edit_message_text("✅ Admin paneli kapatıldı.")
    
    # İptal
    elif callback_data == "mb_cancel":
        # Temizlik
        for key in ['broadcast_format', 'awaiting_broadcast', 'awaiting_channel_link']:
            if key in context.user_data:
                del context.user_data[key]
        
        query.edit_message_text(
            "❌ *İşlem iptal edildi!*",
            parse_mode='Markdown',
            reply_markup=manybot_admin_keyboard()
        )

# ========== YARDIMCI FONKSİYONLAR ==========

def show_period_stats(query, period):
    """Periyodik istatistikleri göster"""
    total_users = len(db.users)
    now = datetime.now()
    
    # Dil dağılımı
    lang_counts = {}
    for user_data in db.users.values():
        lang = user_data.get('language', 'unknown')
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    lang_text = ""
    for lang, count in lang_counts.items():
        lang_name = {
            'tr': 'Türkçe',
            'en': 'İngilizce',
            'ckb': 'Kürtçe Sorani',
            'badini': 'Kürtçe Badini',
            'ar': 'Arapça',
            'unknown': 'Belirsiz'
        }.get(lang, lang)
        percentage = int(count / total_users * 100) if total_users > 0 else 0
        lang_text += f"  • {lang_name}: {count} ({percentage}%)\n"
    
    period_names = {
        'today': 'Bugün',
        'week': 'Bu Hafta',
        'month': 'Bu Ay',
        'total': 'Tüm Zaman'
    }
    
    period_name = period_names.get(period, period)
    
    stats_text = f"📊 *{period_name.upper()} İSTATİSTİKLER*\n\n"
    stats_text += f"👥 *Toplam Kullanıcı:* {total_users}\n\n"
    stats_text += f"🌍 *Dil Dağılımı:*\n{lang_text}\n"
    
    # Eğer veritabanı olsaydı burada periyodik istatistikler eklenirdi
    stats_text += f"📈 *{period_name} Analiz:*\n"
    stats_text += f"  • Aktif kullanıcı: {total_users}\n"
    stats_text += f"  • Yeni kayıtlar: Veritabanı gerekiyor\n"
    stats_text += f"  • Ortalama: Tüm kullanıcılar aktif\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Yenile", callback_data="mb_stats")],
        [InlineKeyboardButton("↩️ Geri", callback_data="mb_back")]
    ]
    
    query.edit_message_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def change_setting(query, setting_type):
    """Ayarı değiştir"""
    settings = load_json_file(SETTINGS_FILE, {})
    
    if setting_type == "format":
        current_format = settings.get("broadcast_format", "html")
        new_format = "normal" if current_format == "html" else "html"
        settings["broadcast_format"] = new_format
        save_json_file(SETTINGS_FILE, settings)
        
        query.edit_message_text(
            f"✅ *Duyuru formatı değiştirildi!*\n\n"
            f"Yeni format: {new_format.upper()}",
            parse_mode='Markdown',
            reply_markup=settings_keyboard()
        )
    
    elif setting_type == "auto_delete":
        current = settings.get("auto_delete", False)
        settings["auto_delete"] = not current
        save_json_file(SETTINGS_FILE, settings)
        
        status = "✅ Açık" if settings["auto_delete"] else "❌ Kapalı"
        
        query.edit_message_text(
            f"✅ *Otomatik silme değiştirildi!*\n\n"
            f"Yeni durum: {status}",
            parse_mode='Markdown',
            reply_markup=settings_keyboard()
        )
    
    elif setting_type == "reset":
        default_settings = {
            "channel_link": CHANNEL_LINK,
            "broadcast_format": "html",
            "auto_delete": False
        }
        save_json_file(SETTINGS_FILE, default_settings)
        
        query.edit_message_text(
            f"✅ *Ayarlar sıfırlandı!*\n\n"
            f"Tüm ayarlar varsayılan değerlere döndü.",
            parse_mode='Markdown',
            reply_markup=settings_keyboard()
        )

def show_users_list(query):
    """Kullanıcı listesini göster"""
    users = db.users
    total_users = len(users)
    
    if total_users == 0:
        query.edit_message_text(
            "👥 *KULLANICI LİSTESİ*\n\n"
            "Henüz hiç kullanıcı yok!",
            parse_mode='Markdown',
            reply_markup=manybot_admin_keyboard()
        )
        return
    
    # Son 10 kullanıcıyı göster
    recent_users = []
    for user_id, user_data in list(users.items())[-10:]:
        username = user_data.get('username', 'Yok')
        name = user_data.get('first_name', 'İsimsiz')
        lang = user_data.get('language', 'unknown')
        
        recent_users.append(f"• {name} (@{username}) - {lang}")
    
    users_text = "👥 *KULLANICI LİSTESİ*\n\n"
    users_text += f"📊 Toplam Kullanıcı: {total_users}\n\n"
    users_text += "📋 Son 10 Kullanıcı:\n"
    users_text += "\n".join(recent_users)
    users_text += "\n\n_Not: Tüm listeyi görmek için geliştirme gerekli._"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Yenile", callback_data="mb_users")],
        [InlineKeyboardButton("↩️ Geri", callback_data="mb_back")]
    ]
    
    query.edit_message_text(
        users_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
  )
