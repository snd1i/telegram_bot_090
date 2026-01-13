import telebot
import os

# Bot tokenini buraya yapıştır
BOT_TOKEN = "BURAYA_KENDİ_TOKENİNİ_YAPIŞTIR"

bot = telebot.TeleBot(BOT_TOKEN)

# /start komutu için
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Ben çalışıyorum. 🎉")

# Botu çalıştır
print("Bot çalışıyor...")
bot.polling()
