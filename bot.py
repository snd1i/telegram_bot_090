import telebot
import os
import time

# Bot tokenini environment variable'dan al
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    print("HATA: BOT_TOKEN bulunamadı!")
    print("Lütfen Railway'de BOT_TOKEN environment variable ekleyin.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    welcome_text = f"""
    Merhaba {user.first_name}! 👋

    Bot başarıyla çalışıyor! 🎉
    
    ID: {user.id}
    Kullanıcı adı: @{user.username if user.username else 'yok'}
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Şu an sadece /start komutu çalışıyor. Mesajınız: {message.text}")

if __name__ == "__main__":
    print("🤖 Telegram Bot Başlatılıyor...")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")  # Güvenlik için sadece ilk 10 karakter
    print("Bot aktif! /start komutunu bekliyor...")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Hata oluştu: {e}")
            print("5 saniye sonra tekrar deneniyor...")
            time.sleep(5)
