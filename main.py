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
    bot.reply_to(
        message,
        f"🤖 **Bot Aktif!**\n\n"
        f"📊 Kayıtlı kullanıcı: {len(users)}",
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

if __name__ == "__main__":
    # Duyuru modülünü başlat
    duyuru.init_bot(bot, users)
    
    print("=" * 40)
    print("🤖 DUYURU BOTU BAŞLATILDI")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Kullanıcı: {len(users)}")
    print("=" * 40)
    
    bot.infinity_polling()
