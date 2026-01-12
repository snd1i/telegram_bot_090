import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

ADMIN_ID = 5541236874
KULLANICILAR = "kullanicilar.txt"

# Kullanıcı kaydet
def kaydet(user_id):
    with open(KULLANICILAR, "a") as f:
        f.write(f"{user_id}\n")

# Kullanıcıları oku
def kullanicilari_al():
    try:
        with open(KULLANICILAR, "r") as f:
            return [line.strip() for line in f]
    except:
        return []

# /start
def start(update, context):
    kaydet(str(update.effective_user.id))
    update.message.reply_text("Bot aktif!")

# /duyuru
def duyuru(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Admin değilsin!")
        return
    
    update.message.reply_text("Duyuru mesajını yaz:")
    context.user_data["duyuru_mod"] = True

# Mesaj işleme
def mesaj(update, context):
    if update.effective_user.id == ADMIN_ID and context.user_data.get("duyuru_mod"):
        mesaj_text = update.message.text
        kullanicilar = kullanicilari_al()
        
        for kullanici in kullanicilar:
            try:
                context.bot.send_message(int(kullanici), f"📢 Duyuru:\n{mesaj_text}")
            except:
                pass
        
        context.user_data["duyuru_mod"] = False
        update.message.reply_text(f"Duyuru gönderildi: {len(kullanicilar)} kişi")

# Ana fonksiyon
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("duyuru", duyuru))
    dp.add_handler(MessageHandler(Filters.text, mesaj))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
