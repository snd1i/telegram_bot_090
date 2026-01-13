import os
import telebot
from telebot import types
import duyuru

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = "5541236874"

bot = telebot.TeleBot(TOKEN)

# Tüm kullanıcıları sakla
users = set()

@bot.message_handler(commands=['start'])
def start(message):
    users.add(message.from_user.id)
    
    # ADMIN ise istatistik göster, değilse sadece basit mesaj
    if str(message.from_user.id) == ADMIN_ID:
        bot.reply_to(
            message,
            f"🤖 **Bot Aktif!**\n\n"
            f"📊 Kayıtlı kullanıcı: {len(users)}\n"
            f"🔧 Duyuru göndermek için: /send",
            parse_mode='Markdown'
        )
    else:
        # NORMAL KULLANICI - istatistik gösterme
        bot.reply_to(
            message,
            "🤖 Bot aktif! Duyurular buradan gönderilecek.",
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['send'])
def send_command(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "⛔ Bu komutu kullanma yetkiniz yok.")
        return
    
    msg = bot.send_message(
        message.chat.id,
        "📝 **Duyuru metnini yazın:**\n\n"
        "Yazdıktan sonra gönder butonuna basın.",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, duyuru.process_duyuru_text)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    # SADECE ADMIN istatistik görebilir
    if str(message.from_user.id) == ADMIN_ID:
        bot.reply_to(
            message,
            f"📊 **Admin İstatistikleri**\n\n"
            f"• 👥 Toplam Kullanıcı: {len(users)}\n"
            f"• 🤖 Bot Durumu: Aktif\n"
            f"• 🔑 Admin ID: {ADMIN_ID}",
            parse_mode='Markdown'
        )

# Callback handler
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    duyuru.handle_duyuru_callbacks(call)

# Fotoğraf handler
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    duyuru.process_duyuru_photo(message)

# Diğer mesajlar
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    users.add(message.from_user.id)
    
    # Normal kullanıcılar için basit cevap
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(
            message,
            "🤖 Bu bot sadece duyuru almak içindir.\n"
            "Duyurular yönetici tarafından gönderilecektir."
        )

if __name__ == "__main__":
    # Duyuru modülünü başlat
    duyuru.init_bot(bot, users)
    
    print("=" * 40)
    print("🤖 DUYURU BOTU BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(users)} (SADECE ADMIN GÖRÜR)")
    print("=" * 40)
    
    bot.infinity_polling()
