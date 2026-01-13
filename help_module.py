import telebot
from telebot import types
import diller

def setup_help_commands(bot):
    """/help komutlarını kur"""
    
    @bot.message_handler(commands=['help', 'yardim', 'h'])
    def help_command(message):
        """Yardım komutu - HERKES İÇİN"""
        user_id = message.from_user.id
        
        # Admin kontrolü - main.py'den users set'ini alalım
        from main import ADMIN_ID, users
        is_admin = (str(user_id) == ADMIN_ID)
        
        # Kullanıcı dilini al
        lang_data = diller.get_language_data(user_id)
        
        # Butonları oluştur
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(
                lang_data['button_support'], 
                url=lang_data['support_url']
            )
        )
        
        # Yardım mesajını oluştur
        if is_admin:
            # ADMIN için mesaj
            help_text = f"""
ℹ️ **{lang_data['help_title']}**

**📌 {lang_data['help_command']}:**
• /start - Botu başlat
• /language - Dil değiştir
• /help - {lang_data['help_title']}

**👑 Admin Komutları:**
• /send - Duyuru gönder
• /stats - İstatistikler

**🔗 Bağlantılar:**
• Kanal: {lang_data['channel_url']}
• Prompts: {lang_data['prompts_url']}

**❓ Sorularınız için:**
"""
        else:
            # NORMAL KULLANICI için mesaj
            help_text = f"""
ℹ️ **{lang_data['help_title']}**

**📌 {lang_data['help_command']}:**
• /start - Botu başlat
• /language - Dil değiştir
• /help - {lang_data['help_title']}

**🔗 Bağlantılar:**
• Kanal: {lang_data['channel_url']}
• Prompts: {lang_data['prompts_url']}

**❓ Sorularınız için:**
"""
        
        # Mesajı gönder
        bot.send_message(
            message.chat.id,
            help_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    print("✅ /help komutu kuruldu")
