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
    """Abone ol butonları (dil destekli)"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang_code, "subscribe"), 
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                get_text(lang_code, "check_again"), 
                callback_data="check_subscription"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(lang_code="en"):
    """Ana menü butonları"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang_code, "select_language"),
                callback_data="change_language"
            )
        ],
        [
            InlineKeyboardButton("ℹ️ Bot Info", callback_data="bot_info"),
            InlineKeyboardButton("📖 Help", callback_data="help"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard(lang_code="en"):
    """Menüye dön butonu"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_text(lang_code, "main_menu"),
                callback_data="main_menu"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
