"""
Dil dosyası - Tüm metinler burada
"""

TEXTS = {
    "tr": {
        "welcome": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "welcome_back": "🇹🇷 Tekrar hoş geldin {name}!",
        "welcome_selected": "🇹🇷 Hoş geldiniz! Dil olarak Türkçe seçildi.",
        "subscribe": "📢 Devam etmek için lütfen kanala abone olun:",
        "not_subscribed": "❌ Kanala abone olmadınız. Lütfen önce abone olun.",
        "checking": "⏳ Abonelik kontrol ediliyor...",
        "check_again": "🔍 Tekrar Kontrol Et",
        "subscribed": "✅ Zaten abonesiniz! Devam edebilirsiniz.",
        "main_menu": "🏠 Ana Menü",
        "help": "📖 Yardım\n\nKomutlar:\n/start - Botu başlat\n/help - Yardım\n/language - Dil değiştir",
        "select_language": "🌍 Dil Seçimi",
        "error": "⚠️ Bir hata oluştu",
    },
    "en": {
        "welcome": "🤖 Welcome! Please select your language:",
        "welcome_back": "🇬🇧 Welcome back {name}!",
        "welcome_selected": "🇬🇧 Welcome! English has been selected as language.",
        "subscribe": "📢 Please subscribe to the channel to continue:",
        "not_subscribed": "❌ You are not subscribed to the channel. Please subscribe first.",
        "checking": "⏳ Checking subscription...",
        "check_again": "🔍 Check Again",
        "subscribed": "✅ You are already subscribed! You can continue.",
        "main_menu": "🏠 Main Menu",
        "help": "📖 Help\n\nCommands:\n/start - Start bot\n/help - Help\n/language - Change language",
        "select_language": "🌍 Language Selection",
        "error": "⚠️ An error occurred",
    },
    "ckb": {
        "welcome": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "welcome_back": "🇹🇯 بەخێربێیت دووبارە {name}!",
        "welcome_selected": "🇹🇯 بەخێربێیت! زمانی کوردی سۆرانی هەڵبژێردرا.",
        "subscribe": "📢 تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوام بوون:",
        "not_subscribed": "❌ تۆ سەبسکرایبی کەناڵەکەت نەکردووە. تکایە سەبسکرایب بکە.",
        "checking": "⏳ سەبسکرایب چێک دەکرێت...",
        "check_again": "🔍 دووبارە چێک بکە",
        "subscribed": "✅ تۆ سەبسکرایبی کەناڵەکەیت کردووە! دەتوانی بەردەوام ببی.",
        "main_menu": "🏠 مێنیوی سەرەکی",
        "help": "📖 یارمەتی\n\nفەرمانەکان:\n/start - دەستپێکردنی بۆت\n/help - یارمەتی\n/language - گۆڕینی زمان",
        "select_language": "🌍 هەڵبژاردنی زمان",
        "error": "⚠️ هەڵەیەک ڕوویدا",
    },
    "badini": {
        "welcome": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "welcome_back": "🇹🇯 Bi xêr hatî dîsa {name}!",
        "welcome_selected": "🇹🇯 Bi xêr hatî! Zimanê Kurdî Badînî hate hilbijartin.",
        "subscribe": "📢 Ji bo domandinê ji kerema xwe li kanalê abone bibin:",
        "not_subscribed": "❌ Te li kanalê abone nebûye. Ji kerema xwe pêşî abone bibin.",
        "checking": "⏳ Aboneyî tê kontrolkirin...",
        "check_again": "🔍 Dîsa Kontrol Bike",
        "subscribed": "✅ Te berê abone bûye! Tu dikarî bidomînî.",
        "main_menu": "🏠 Meniya Sereke",
        "help": "📖 Alîkarî\n\nFerman:\n/start - Destpêkirina bot\n/help - Alîkarî\n/language - Guherandina ziman",
        "select_language": "🌍 Hilbijartina Ziman",
        "error": "⚠️ Çewtî çêبû",
    },
    "ar": {
        "welcome": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "welcome_back": "🇮🇶 أهلاً بك مرة أخرى {name}!",
        "welcome_selected": "🇮🇶 أهلاً بك! تم اختيار العربية كلغة.",
        "subscribe": "📢 يرجى الاشتراك في القناة للمتابعة:",
        "not_subscribed": "❌ لم تشترك في القناة. يرجى الاشتراك أولاً.",
        "checking": "⏳ جاري التحقق من الاشتراك...",
        "check_again": "🔍 تحقق مرة أخرى",
        "subscribed": "✅ أنت مشترك بالفعل! يمكنك المتابعة.",
        "main_menu": "🏠 القائمة الرئيسية",
        "help": "📖 مساعدة\n\nالأوامر:\n/start - بدء البوت\n/help - مساعدة\n/language - تغيير اللغة",
        "select_language": "🌍 اختيار اللغة",
        "error": "⚠️ حدث خطأ",
    }
}

def get_text(lang_code, text_key, **kwargs):
    """Dil koduna göre metni döndürür"""
    if lang_code in TEXTS and text_key in TEXTS[lang_code]:
        text = TEXTS[lang_code][text_key]
        # Formatlama varsa uygula
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text
    return TEXTS["en"].get(text_key, text_key)
