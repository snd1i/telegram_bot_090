from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from languages import get_text
from config import CHANNEL_LINK

def language_keyboard():
    """Dil seçim butonları"""
    keyboard = [
        [
            InlineKeyboardButton("Kürtçe Sorani 🇹🇯", callback_data="lang_ckb"),
            InlineKeyboardButton("Kürtçe Badini 🇹🇯", callback_data="lang_badini"),
        ],
        [
            InlineKeyboardButton("Türkçe 🇹🇷", callback_data="lang_tr"),
            InlineKeyboardButton("İngilizce 🇬🇧", callback_data="lang_en"),
        ],
        [
            InlineKeyboardButton("Arapça 🇮🇶", callback_data="lang_ar"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def subscribe_keyboard(lang_code="en"):
    """Abone ol butonları"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang_code, "subscribe"), 
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Kontrol Et / Check", 
                callback_data="check_subscription"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
