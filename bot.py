import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ADMIN_ID = 5541236874
USER_FILE = "kullanicilar.txt"

# Kullanıcı kaydet
def kaydet(user_id):
    with open(USER_FILE, "a") as f:
        f.write(f"{user_id}\n")

# Kullanıcıları oku
def kullanicilari_oku():
    try:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as f:
                return [line.strip() for line in f if line.strip()]
    except:
        pass
    return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    kaydet(user_id)
    await update.message.reply_text("Merhaba! Duyuru botuna hoş geldin.")

async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bu komutu kullanamazsın.")
        return
    
    await update.message.reply_text("Duyuru mesajını yaz:")
    context.user_data["duyuru_gonder"] = True

async def mesaj_al(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and context.user_data.get("duyuru_gonder"):
        mesaj = update.message.text
        kullanicilar = kullanicilari_oku()
        
        gonderilen = 0
        for kullanici in kullanicilar:
            try:
                await context.bot.send_message(int(kullanici), f"📢 Duyuru:\n\n{mesaj}")
                gonderilen += 1
            except:
                pass
        
        context.user_data["duyuru_gonder"] = False
        await update.message.reply_text(f"Duyuru {gonderilen} kişiye gönderildi.")

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_al))
    
    app.run_polling()

if __name__ == "__main__":
    main()
