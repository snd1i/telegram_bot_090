# Dil veritabanı
DILLER = {
    'ku_badini': {
        'code': 'ku_badini',
        'name': 'Kurdî (Badînî) 🇹🇯',
        'welcome': 'خێرهاتی بو ناف بوتێ پرومپتا',
        'select_language': 'زمانەکێ هەلبژێرە',
        'description': 'ئەف بوتە بو پرومتسایە',
        'menu': 'دەسپێک',
        'help': 'هاریکاری',
        'start': 'بدەکاری',
        'exit': 'دەرکەتن',
        'language': 'زمان',
        'choose': 'هەلبژێرە'
    },
    'ku_sorani': {
        'code': 'ku_sorani',
        'name': 'کوردی (سۆرانی) 🇹🇯',
        'welcome': 'بەخێربێیت بۆ بۆتی پرۆمپت',
        'select_language': 'زمان هەڵبژێرە',
        'description': 'ئەم بۆتە بۆ پرۆمپتە',
        'menu': 'مەینۆی سەرەکی',
        'help': 'یارمەتی',
        'start': 'دەستپێکردن',
        'exit': 'دەرچوون',
        'language': 'زمان',
        'choose': 'هەڵبژێرە'
    },
    'tr': {
        'code': 'tr',
        'name': 'Türkçe 🇹🇷',
        'welcome': 'Prompt Botuna Hoş Geldiniz',
        'select_language': 'Dil seçin',
        'description': 'Bu bot ile promptlar alacaksınız',
        'menu': 'Ana menü',
        'help': 'Yardım',
        'start': 'Başlat',
        'exit': 'Çıkış',
        'language': 'Dil',
        'choose': 'Seç'
    },
    'en': {
        'code': 'en',
        'name': 'English 🇬🇧',
        'welcome': 'Welcome to Prompt Bot',
        'select_language': 'Select language',
        'description': 'You will receive prompts through this bot',
        'menu': 'Main menu',
        'help': 'Help',
        'start': 'Start',
        'exit': 'Exit',
        'language': 'Language',
        'choose': 'Choose'
    },
    'ar': {
        'code': 'ar',
        'name': 'العربية 🇮🇶',
        'welcome': 'مرحبًا بك في بوت البرومبت',
        'select_language': 'اختر اللغة',
        'description': 'ستتلقى برومبتات من خلال هذا البوت',
        'menu': 'القائمة الرئيسية',
        'help': 'مساعدة',
        'start': 'بدء',
        'exit': 'خروج',
        'language': 'لغة',
        'choose': 'اختر'
    }
}

# Kullanıcı dil tercihlerini sakla
user_languages = {}

def get_user_language(user_id):
    """Kullanıcının dil tercihini getir"""
    return user_languages.get(user_id, None)

def set_user_language(user_id, lang_code):
    """Kullanıcı dil tercihini kaydet"""
    if lang_code in DILLER:
        user_languages[user_id] = lang_code
        return True
    return False

def get_language_text(user_id, key):
    """Kullanıcı diline göre metin getir"""
    lang_code = get_user_language(user_id)
    
    # Eğer dil tercihi yoksa, Türkçe varsayılan
    if not lang_code:
        lang_code = 'tr'
    
    lang_data = DILLER.get(lang_code, DILLER['tr'])
    return lang_data.get(key, '')
