"""
Dil dosyası - Tüm metinler burada
"""

TEXTS = {
    # Türkçe
    "tr": {
        "welcome": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "welcome_selected": "🇹🇷 Hoş geldiniz! Dil olarak Türkçe seçildi.",
        "subscribe": "📢 Devam etmek için lütfen kanala abone olun:",
        "not_subscribed": "❌ Kanala abone olmadınız. Lütfen önce abone olun.",
        "checking": "⏳ Abonelik kontrol ediliyor...",
        "subscribed": "✅ Zaten abonesiniz! Devam edebilirsiniz.",
        "main_menu": "🏠 Ana Menü",
        "start": "🤖 Hoş geldiniz! Lütfen dilinizi seçin:",
        "help": "📖 Yardım\n\nBu çok dilli bir Telegram botudur.",
    },
    
    # İngilizce
    "en": {
        "welcome": "🤖 Welcome! Please select your language:",
        "welcome_selected": "🇬🇧 Welcome! English has been selected as language.",
        "subscribe": "📢 Please subscribe to the channel to continue:",
        "not_subscribed": "❌ You are not subscribed to the channel. Please subscribe first.",
        "checking": "⏳ Checking subscription...",
        "subscribed": "✅ You are already subscribed! You can continue.",
        "main_menu": "🏠 Main Menu",
        "start": "🤖 Welcome! Please select your language:",
        "help": "📖 Help\n\nThis is a multi-language Telegram bot.",
    },
    
    # Arapça
    "ar": {
        "welcome": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "welcome_selected": "🇮🇶 أهلاً بك! تم اختيار العربية كلغة.",
        "subscribe": "📢 يرجى الاشتراك في القناة للمتابعة:",
        "not_subscribed": "❌ لم تشترك في القناة. يرجى الاشتراك أولاً.",
        "checking": "⏳ جاري التحقق من الاشتراك...",
        "subscribed": "✅ أنت مشترك بالفعل! يمكنك المتابعة.",
        "main_menu": "🏠 القائمة الرئيسية",
        "start": "🤖 أهلاً بك! الرجاء اختيار لغتك:",
        "help": "📖 مساعدة\n\nهذا بوت تيليجرام متعدد اللغات.",
    },
    
    # Kürtçe Sorani
    "ckb": {
        "welcome": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "welcome_selected": "🇹🇯 بەخێربێیت! زمانی کوردی سۆرانی هەڵبژێردرا.",
        "subscribe": "📢 تکایە سەبسکرایبی کەناڵەکە بکە بۆ بەردەوام بوون:",
        "not_subscribed": "❌ تۆ سەبسکرایبی کەناڵەکەت نەکردووە. تکایە سەبسکرایب بکە.",
        "checking": "⏳ سەبسکرایب چێک دەکرێت...",
        "subscribed": "✅ تۆ سەبسکرایبی کەناڵەکەیت کردووە! دەتوانی بەردەوام ببی.",
        "main_menu": "🏠 مێنیوی سەرەکی",
        "start": "🤖 بەخێربێیت! تکایە زمانەکەت هەڵبژێرە:",
        "help": "📖 یارمەتی\n\nئەمە بۆتێکی تێلیگرامی فرە زمانەیە.",
    },
    
    # Kürtçe Badini
    "badini": {
        "welcome": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "welcome_selected": "🇹🇯 Bi xêr hatî! Zimanê Kurdî Badînî hate hilbijartin.",
        "subscribe": "📢 Ji bo domandinê ji kerema xwe li kanalê abone bibin:",
        "not_subscribed": "❌ Te li kanalê abone nebûye. Ji kerema xwe pêşî abone bibin.",
        "checking": "⏳ Aboneyî tê kontrolkirin...",
        "subscribed": "✅ Te berê abone bûye! Tu dikarî bidomînî.",
        "main_menu": "🏠 Meniya Sereke",
        "start": "🤖 Bi xêr hatî! Ji kerema xwe zimanê xwe hilbijêrin:",
        "help": "📖 Alîkarî\n\nEv botekî Telegrama pirzimanî ye.",
    }
}

def get_text(lang_code, text_key):
    """Dil koduna göre metni döndürür"""
    if lang_code in TEXTS:
        return TEXTS[lang_code].get(text_key, TEXTS["en"][text_key])
    return TEXTS["en"][text_key]
