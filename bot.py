#!/usr/bin/env python3
"""
TELEGRAM BOT - KESİN ÇÖZÜM
"""

import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

print("=" * 60)
print("🤖 BOT ÇALIŞIYOR!")
print("=" * 60)

# Token
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ HATA: BOT_TOKEN yok!")
    exit()

print(f"✅ Token var")

# Log
logging.basicConfig(level=logging.INFO)

# Komutlar
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f"Merhaba {user.first_name}! ✅")

def help(update: Update, context: CallbackContext):
    update.message.reply_text("Yardım: /start")

# Ana fonksiyon
def main():
    print("Bot başlıyor...")
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    
    print("✅ Bot hazır!")
    print("📱 Telegram'da /start yaz")
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
