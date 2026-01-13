import os
import telebot
from telebot import types

# Token'i al
TOKEN = os.getenv('BOT_TOKEN')
# ADMIN_ID'yi buraya kendi Telegram ID'nizi yazın (Bunu nasıl bulacağınızı aşağıda anlattım)
ADMIN_ID = "BURAYA_SIZIN_TELEGRAM_ID_NIZI_YAZIN"  # Örnek: "123456789"

bot = telebot.TeleBot(TOKEN)

# Kullanıcı ID'lerini saklamak için basit bir liste
# Not: Bot restart olursa sıfırlanır, kalıcı olmasını isterseniz dosyaya kaydedebiliriz
user_ids = set()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_ids.add(user_id)  # Kullanıcıyı kaydet
    
    bot.reply_to(message, "🤖 Bot aktif! /duyuru komutu ile duyuru gönderebilirsiniz.")

@bot.message_handler(commands=['duyuru'])
def duyuru(message):
    user_id = str(message.from_user.id)
    
    # Sadece admin duyuru gönderebilir
    if user_id != ADMIN_ID:
        bot.reply_to(message, "⛔ Bu komutu kullanma yetkiniz yok.")
        return
    
    # Admin ise duyuru mesajını iste
    msg = bot.reply_to(message, "📢 Duyuru mesajını yazın:")
    bot.register_next_step_handler(msg, send_announcement)

def send_announcement(message):
    announcement_text = message.text
    admin_id = message.from_user.id
    
    bot.send_message(admin_id, f"📤 Duyuru gönderiliyor... ({len(user_ids)} kullanıcıya)")
    
    successful = 0
    failed = 0
    
    # Tüm kullanıcılara duyuru gönder
    for user_id in user_ids:
        try:
            bot.send_message(user_id, f"📢 **DUYURU**\n\n{announcement_text}")
            successful += 1
        except:
            failed += 1
    
    # Admin'e rapor gönder
    bot.send_message(
        admin_id,
        f"✅ Duyuru tamamlandı!\n\n"
        f"✓ Başarılı: {successful}\n"
        f"✗ Başarısız: {failed}\n"
        f"📊 Toplam kullanıcı: {len(user_ids)}"
    )

# Diğer mesajlara cevap
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.from_user.id
    user_ids.add(user_id)  # Mesaj atan kullanıcıyı da kaydet
    bot.reply_to(message, "🤖 Sadece /start komutunu kullanabilirsiniz.")

if __name__ == "__main__":
    print("🤖 Bot başlatıldı...")
    print(f"👤 Toplam kayıtlı kullanıcı: {len(user_ids)}")
    bot.infinity_polling()
