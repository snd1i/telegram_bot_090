"""
Dil dosyası - Tüm metinler burada
"""

TEXTS = {
    # Türkçe
    "tr": {
        "welcome": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "welcome_back": "🇹🇷 Tekrar hoş geldiniz {name}!",
        "welcome_selected": "🇹🇷 Hoş geldiniz! Dil olarak Türkçe seçildi.",
        "subscribe": "📢 Devam etmek için lütfen kanala abone olun:",
        "not_subscribed": "❌ Kanala abone olmadınız. Lütfen önce abone olun.",
        "already_subscribed": "✅ Zaten abonesiniz! Devam edebilirsiniz.",
        "checking": "⏳ Abonelik kontrol ediliyor...",
        "check_again": "🔍 Tekrar Kontrol Et",
        "subscription_success": "🎉 Tebrikler! Başarıyla abone oldunuz.",
        "main_menu": "🏠 Ana Menü",
        "select_language": "🌍 Dil Seçimi",
        "error": "⚠️ Bir hata oluştu, lütfen tekrar deneyin.",
        "bot_info": "🤖 Bot Bilgileri\n\nAd: {name}\nVersiyon: {version}\nDiliniz: Türkçe",
        "help": "📖 Yardım\n\nBu çok dilli bir Telegram botudur.\n\nKomutlar:\n/start - Botu başlat\n/help - Yardım mesajı\n/language - Dil değiştir\n/info - Bot bilgileri",
    },
    
    # İngilizce
    "en": {
        "welcome": "🤖 Welcome! Please select your language:",
        "welcome_back": "🇬🇧 Welcome back {name}!",
        "welcome_selected": "🇬🇧 Welcome! English has been selected as language.",
        "subscribe": "📢 Please subscribe to the channel to continue:",
        "not_subscribed": "❌ You are not subscribed to the channel. Please subscribe first.",
        "already_subscribed": "✅ You are already subscribed! You can continue.",
        "checking": "⏳ Checking subscription...",
        "check_again": "🔍 Check Again",
        "subscription_success": "🎉 Congratulations! You have successfully subscribed.",
        "main_menu": "🏠 Main Menu",
        "select_language": "🌍 Language Selection",
        "error": "⚠️ An error occurred, please try again.",
        "bot_info": "🤖 Bot Information\n\nName: {name}\nVersion: {version}\nYour language: English",
        "help": "📖 Help\n\nThis is a multi-language Telegram bot.\n\nCommands:\n/start - Start the bot\n/help - Help message\n/language - Change language\n/info - Bot information",
    },
    
    # Arapça
    "ar": {
        "welcome": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "welcome_back": "🇮🇶 أهلاً بك مرة أخرى {name}!",
        "welcome_selected": "🇮🇶 أهلاً بك! تم اختيار العربية كلغة.",
        "subscribe": "📢 يرجى الاشتراك في القناة للمتابعة:",
        "not_subscribed": "❌ لم تشترك في القناة. يرجى الاشتراك أولاً.",
        "already_subscribed": "✅ أنت مشترك بالفعل! يمكنك المتابعة.",
        "checking": "⏳ جاري التحقق من الاشتراك...",
        "check_again": "🔍 تحقق مرة أخرى",
        "subscription_success": "🎉 مبروك! لقد اشتركت بنجاح.",
        "main_menu": "🏠 القائمة الرئيسية",
        "select_language": "🌍 اختيار اللغة",
        "error": "⚠️ حدث خطأ، يرجى المحاولة مرة أخرى.",
        "bot_info": "🤖 معلومات البوت\n\nالاسم: {name}\nالإصدار: {version}\nلغتك: العربية",
        "help": "📖 مساعدة\n\nهذا بوت تيليجرام متعدد اللغات.\n\nالأوامر:\n/start - بدء البوت\n/help - رسالة المساعدة\n/language - تغيير اللغة\n/info - معلومات البوت",
    },
    
    # Kürtçe Sorani
    "ckb": {
        "welcome": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "welcome_back": "🇹🇯 بەخێربێیت دووبارە {name}!",
        "welcome_selected": "🇹🇯 بەخێربێیت! زمانی کوردی سۆرانی هەڵبژێردرا.",
        "subscribe": "📢 تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوام بوون:",
        "not_subscribed": "❌ تۆ سەبسکرایبی کەناڵەکەت نەکردووە. تکایە سەبسکرایب بکە.",
        "already_subscribed": "✅ تۆ سەبسکرایبی کەناڵەکەیت کردووە! دەتوانی بەردەوام ببی.",
        "checking": "⏳ سەبسکرایب چێک دەکرێت...",
        "check_again": "🔍 دووبارە چێک بکە",
        "subscription_success": "🎉 پیرۆزبێت! سەبسکرایبی کەناڵەکەت بە سەرکەوتوویی کرد.",
        "main_menu": "🏠 مێنیوی سەرەکی",
        "select_language": "🌍 هەڵبژاردنی زمان",
        "error": "⚠️ هەڵەیەک ڕوویدا، تکایە دووبارە هەوڵ بدەوە.",
        "bot_info": "🤖 زانیاری بۆت\n\nناو: {name}\nوەشان: {version}\nزمانەکەت: کوردی سۆرانی",
        "help": "📖 یارمەتی\n\nئەمە بۆتێکی تێلیگرامی فرە زمانەیە.\n\nفەرمانەکان:\n/start - دەستپێکردنی بۆت\n/help - پەیامی یارمەتی\n/language - گۆڕینی زمان\n/info - زانیاری بۆت",
    },
    
    # Kürtçe Badini
    "badini": {
        "welcome": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "welcome_back": "🇹🇯 Bi xêr hatî dîsa {name}!",
        "welcome_selected": "🇹🇯 Bi xêr hatî! Zimanê Kurdî Badînî hate hilbijartin.",
        "subscribe": "📢 Ji bo domandinê ji kerema xwe li kanalê abone bibin:",
        "not_subscribed": "❌ Te li kanalê abone nebûye. Ji kerema xwe pêşî abone bibin.",
        "already_subscribed": "✅ Te berê abone bûye! Tu dikarî bidomînî.",
        "checking": "⏳ Aboneyî tê kontrolkirin...",
        "check_again": "🔍 Dîsa Kontrol Bike",
        "subscription_success": "🎉 Pîroz be! Te bi serkeftinî abone bûye.",
        "main_menu": "🏠 Meniya Sereke",
        "select_language": "🌍 Hilbijartina Ziman",
        "error": "⚠️ Çewtî çêbû, ji kerema xwe dîsa hewl bide.",
        "bot_info": "🤖 Agahiyên Bot\n\nNav: {name}\nVersiyon: {version}\nZimanê te: Kurdî Badînî",
        "help": "📖 Alîkarî\n\nEv botekî Telegrama pirzimanî ye.\n\nFerman:\n/start - Destpêkirina bot\n/help - Peyama alîkariyê\n/language - Guherandina ziman\n/info - Agahiyên bot",
    }
}

def get_text(lang_code, text_key, **kwargs):
    """Dil koduna göre metni döndürür"""
    if lang_code in TEXTS:
        text = TEXTS[lang_code].get(text_key, TEXTS["en"][text_key])
    else:
        text = TEXTS["en"][text_key]
    
    # Formatlama varsa uygula
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    
    return text
